# Schnellstart-Anleitung: Twitch Clip Voting System

## Voraussetzungen

- Node.js (Version 14 oder höher)
- Twitch Developer Account
- Git

## Schritt 1: Twitch Developer App einrichten (5 Minuten)

1. **Gehe zu:** https://dev.twitch.tv/console/apps
2. **Klicke:** "Register Your Application"
3. **Fülle aus:**
   - Name: `HD Clip Voting`
   - OAuth Redirect URLs: `http://localhost:3000/auth/callback`
   - Category: `Website Integration`
4. **Klicke:** "Create"
5. **Notiere:** Client ID und Client Secret (nach Klick auf "New Secret")

## Schritt 2: Projekt einrichten (2 Minuten)

```bash
# Im Projektverzeichnis:
cd /pfad/zum/projekt

# Dependencies installieren
npm install

# .env Datei erstellen
cp .env.example .env
```

## Schritt 3: .env konfigurieren (1 Minute)

Öffne `.env` und fülle aus:

```env
TWITCH_CLIENT_ID=deine_client_id_von_schritt_1
TWITCH_CLIENT_SECRET=dein_client_secret_von_schritt_1
TWITCH_REDIRECT_URI=http://localhost:3000/auth/callback
SESSION_SECRET=GeneriereEinSicheresZufälligesSecret123!
PORT=3000
```

## Schritt 4: Voting-Zeiträume konfigurieren (1 Minute)

Öffne `config.txt` und passe die Daten an:

```txt
# Wann dürfen Leute abstimmen?
VOTING_START=2026-01-10T00:00:00Z
VOTING_END=2026-01-31T23:59:59Z

# Welche Clips sollen zur Auswahl stehen?
CLIPS_START=2026-01-01T00:00:00Z
CLIPS_END=2026-01-09T23:59:59Z

# Dein Twitch-Benutzername
TWITCH_BROADCASTER_ID=hd1920x1080

# Anzahl der Clips
MAX_CLIPS=10
```

**Wichtig:** Alle Daten müssen im Format `YYYY-MM-DDTHH:MM:SSZ` sein!

## Schritt 5: Server starten (1 Sekunde)

```bash
npm start
```

Du solltest sehen:
```
Server running on http://localhost:3000
```

## Schritt 6: Testen

1. **Öffne Browser:** http://localhost:3000
2. **Klicke auf:** "Clip Voting"
3. **Melde dich an** mit deinem Twitch-Account
4. **Wähle einen Clip** und stimme ab
5. **Nach Voting-Ende:** Besuche http://localhost:3000/html/results.html

## Häufige Probleme

### "Cannot find module 'express'"
```bash
npm install
```

### "Error getting Twitch token"
- Prüfe `TWITCH_CLIENT_ID` und `TWITCH_CLIENT_SECRET` in `.env`
- Stelle sicher, dass die Werte keine Leerzeichen oder Anführungszeichen enthalten

### "Not authenticated" beim Abstimmen
- Stelle sicher, dass du dich mit Twitch angemeldet hast
- Prüfe, ob die Redirect URI in der Twitch App korrekt ist

### "Voting has not started yet"
- Prüfe `VOTING_START` in `config.txt`
- Stelle sicher, dass das Datum in der Vergangenheit liegt (für Tests)

### Clips werden nicht geladen
- Prüfe `TWITCH_BROADCASTER_ID` in `config.txt`
- Stelle sicher, dass es der exakte Twitch-Benutzername ist
- Prüfe, ob es Clips im angegebenen Zeitraum gibt

## Nächste Schritte

### Für Produktion

1. **Erstelle Produktions-Domain** bei einem Hosting-Anbieter
2. **Füge Redirect URI hinzu** in Twitch Developer Console:
   - `https://deine-domain.de/auth/callback`
3. **Aktualisiere .env:**
   ```env
   TWITCH_REDIRECT_URI=https://deine-domain.de/auth/callback
   ```
4. **Aktiviere HTTPS** in server.js (Zeile mit `cookie: { secure: true }`)
5. **Verwende eine Datenbank** statt In-Memory-Storage (siehe VOTING_README.md)

### Für Tests (Zeiträume anpassen)

Um das System sofort zu testen, setze in `config.txt`:

```txt
# Voting läuft jetzt
VOTING_START=2026-01-01T00:00:00Z
VOTING_END=2026-12-31T23:59:59Z

# Clips der letzten 30 Tage
CLIPS_START=2025-12-10T00:00:00Z
CLIPS_END=2026-01-09T23:59:59Z
```

Dann Server neu starten:
```bash
# Strg+C zum Stoppen
npm start
```

## Support

- **Ausführliche Dokumentation:** Siehe `VOTING_README.md`
- **E-Mail:** Admin@HD1920x1080.de
- **Twitch API Docs:** https://dev.twitch.tv/docs/api/

## Feature-Übersicht

✅ Automatisches Laden von Clips via Twitch API  
✅ OAuth-Login mit Twitch  
✅ Ein Vote pro Account  
✅ Konfigurierbare Zeiträume über Textdatei  
✅ Responsive Design  
✅ Ergebnisseite mit Podium  
✅ Direkte Links zu Clips  
✅ Eingebettete Clip-Player  

Viel Erfolg! 🎬🎉
