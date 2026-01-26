import os
import requests
from icalendar import Calendar
from datetime import datetime, timezone, timedelta

# --- KONFIGURATION ---
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
USER_TOKEN = os.getenv('TWITCH_TOKEN')
CHANNEL_NAME = os.getenv('TWITCH_CHANNEL')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
ICS_URL = "https://export.kalender.digital/ics/0/4ccef74582e0eb8d7026/twitchhd1920x1080.ics?past_months=3&future_months=36"

def should_run_now(cal, now):
    """Prüft, ob ein Stream im iCal vor 30 bis 65 Minuten gestartet ist (GMT)."""
    for event in cal.walk('vevent'):
        start = event.get('dtstart').dt
        if not isinstance(start, datetime):
            continue
        
        # GMT/UTC Sicherheit
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        else:
            start = start.astimezone(timezone.utc)

        diff_minutes = (now - start).total_seconds() / 60
        
        # Trigger-Fenster: 30 bis 65 Minuten nach Start
        if 30 <= diff_minutes <= 65:
            print(f"Passender Stream gefunden: '{event.get('summary')}' (Start vor {int(diff_minutes)} Min)")
            return True
    return False

def update_supabase(event_data, now_iso):
    """Löscht vergangene Streams und trägt den nächsten ein."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase Config fehlt (URL oder KEY).")
        return
    
    url = f"{SUPABASE_URL}/rest/v1/streams"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    # 1. LÖSCHEN: Alles, was vor 'jetzt' gestartet ist
    requests.delete(f"{url}?start_time=lt.{now_iso}", headers=headers)

    # 2. EINTRAGEN: Den nächsten Stream als ID 1
    if event_data:
        payload = {
            "id": 1, 
            "title": event_data['title'],
            "start_time": event_data['start_time']
        }
        headers["Prefer"] = "resolution=merge-duplicates"
        r = requests.post(url, headers=headers, json=payload)
        print(f"Supabase Update Status: {r.status_code}")

def sync():
    now = datetime.now(timezone.utc)
    now_iso = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    print("Lade iCal Feed...")
    try:
        response = requests.get(ICS_URL)
        response.raise_for_status()
        cal = Calendar.from_ical(response.content)
    except Exception as e:
        print(f"Fehler beim Laden des iCal: {e}")
        return

    # Zeit-Check (wird bei manuellem Start übersprungen)
    if os.getenv('GITHUB_EVENT_NAME') != 'workflow_dispatch':
        if not should_run_now(cal, now):
            print("Kein Stream-Start vor 30 Min gefunden. Beende.")
            return

    # Events parsen
    upcoming_events = []
    for event in cal.walk('vevent'):
        start = event.get('dtstart').dt
        if not isinstance(start, datetime): continue
        if start.tzinfo is None: start = start.replace(tzinfo=timezone.utc)
        
        if start > now:
            upcoming_events.append({
                "title": str(event.get('summary'))[:140],
                "start_time": start.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "duration": int((event.get('dtend').dt - start).total_seconds() / 60)
            })

    upcoming_events.sort(key=lambda x: x['start_time'])

    # --- SUPABASE UPDATE ---
    next_event = upcoming_events[0] if upcoming_events else None
    update_supabase(next_event, now_iso)

    # --- TWITCH SYNC ---
    if not USER_TOKEN:
        print("Kein TWITCH_TOKEN vorhanden. Überspringe Twitch Sync.")
        return

    print("Starte Twitch Sync...")
    twitch_headers = {
        "Client-Id": CLIENT_ID,
        "Authorization": f"Bearer {USER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Broadcaster ID holen
        u_resp = requests.get(f"https://api.twitch.tv/helix/users?login={CHANNEL_NAME}", headers=twitch_headers)
        u_resp.raise_for_status()
        b_id = u_resp.json()['data'][0]['id']

        # Segmente hochladen
        for ev in upcoming_events[:5]: # Max 5 zukünftige Einträge
            payload = {
                "start_time": ev['start_time'],
                "timezone": "Europe/Berlin",
                "duration": str(ev['duration']),
                "is_recurring": False,
                "title": ev['title']
            }
            r = requests.post("https://api.twitch.tv/helix/schedule/segment", 
                              headers=twitch_headers, json=payload, params={"broadcaster_id": b_id})
            print(f"Twitch '{ev['title']}': {r.status_code}")
    except Exception as e:
        print(f"Twitch Sync Fehler: {e}")

if __name__ == "__main__":
    sync()
