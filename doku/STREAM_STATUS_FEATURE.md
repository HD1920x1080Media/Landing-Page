# Stream Status Feature

## Overview
The landing page now automatically detects if the Twitch stream is online or offline and displays appropriate content:
- **When Live**: Shows the Twitch embed player and chat
- **When Offline**: Shows a message with information about the next scheduled stream

## How It Works

### 1. Database Schema
A new `streams` table has been added to Supabase to store upcoming stream information:
```sql
CREATE TABLE streams (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

This table is automatically updated by the `.github/scripts/sync_to_twitch.py` script which runs every 30 minutes via GitHub Actions.

### 2. Stream Status Checking
The `js/stream-status.js` script:
- Checks if the stream is live using the Twitch public API (via decapi.me)
- Runs every 60 seconds to monitor stream status
- Automatically switches between live embed and offline message

### 3. Offline Message Display
When the stream is offline, users see:
- A friendly "Stream ist offline" message
- Information about the next scheduled stream (title and start time)
- A link to the stream schedule if no next stream is available

### 4. Automatic Live Detection
The page continuously monitors the stream status and automatically switches to the live embed when the stream goes online, without requiring a page refresh.

## Files Modified/Created

### Created
- `js/stream-status.js` - Main stream status monitoring logic
- `doku/STREAM_STATUS_FEATURE.md` - This documentation

### Modified
- `doku/supabase-schema.sql` - Added streams table
- `js/supabase-client.js` - Added `getNextStream()` function
- `index.html` - Added stream-status.js script
- `css/styles.css` - Added styling for offline message

## User Experience

### Desktop
- Users see either the live embed (with chat on the right) or the offline message
- No page refresh needed when stream goes live

### Mobile
- Works seamlessly with the existing mobile view toggle
- Offline message is responsive and looks good on small screens

## Technical Details

### Stream Status Check
- Uses `https://decapi.me/twitch/uptime/` API to check stream status
- Fail-safe: If the API check fails, assumes stream is live (shows embed)
- Check interval: 60 seconds

### Performance Optimizations
- Monitoring pauses when browser tab is hidden (saves resources)
- Only updates UI when status actually changes
- Minimal API calls (once per minute)

### Data Flow
1. GitHub Actions runs `sync_to_twitch.py` every 30 minutes
2. Script fetches calendar data and updates Supabase `streams` table
3. Frontend queries Supabase for next stream info when showing offline message
4. Frontend checks Twitch API every 60 seconds for live status

## Future Enhancements
Potential improvements:
- Add countdown timer to next stream
- Show stream thumbnail/preview
- Cache next stream info to reduce database queries
- Add notification when stream goes live (with user permission)
