# Manual Second Voting Round - Feature Documentation

## Overview
This feature adds a manual second voting round system that allows administrators to run a special voting round for "Clip des Jahres" (Clip of the Year) using the top 10 clips from a previous monthly voting period.

## Key Features

### 1. Manual Second Voting Round
- Can only be started and stopped via GitHub Actions workflows
- Uses the top 10 clips from a specified monthly voting period
- Automatically expires if not ended before the next automatic monthly voting round
- Separate vote tracking from regular monthly voting

### 2. Clip des Jahres (Clip of the Year)
- Winners are saved to a special "Clip des Jahres" table
- Accessible at `/cdj` endpoint
- **Period**: December (previous year) through November (current year) - 12 months total
- Example: In 2026, shows December 2025 through November 2026
- Shows top 10 clips per month
- Similar design to Clip des Monats but without voting functionality
- Automatic cleanup when December voting completes (removes previous cycle)

## Clip des Jahres Period Logic

The "Clip des Jahres" follows a December-to-November cycle:
- **Current Period** (when viewing in 2026): December 2025 - November 2026
- **Display Order**: December appears first, followed by January through November
- **Cleanup**: When December voting is saved, the previous cycle is automatically deleted
  - Example: Saving December 2026 results will delete December 2024 and Jan-Nov 2025 data

## Database Schema Changes

### New Tables

#### `second_voting_config`
Stores configuration for the manual second voting round:
- `id`: Primary key
- `is_active`: Boolean indicating if second voting is currently active
- `started_at`: Timestamp when second voting started
- `ends_at`: Timestamp when second voting should end
- `source_year`: Year of the monthly results being used
- `source_month`: Month of the monthly results being used
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

#### `clip_des_jahres`
Stores winners of the second voting round:
- `id`: Primary key
- `year`: Year of the winner
- `month`: Month of the winner (1-12)
- `clip_id`: Twitch clip ID
- All clip metadata (url, title, views, etc.)
- `votes`: Number of votes received in second voting
- `calculated_at`: Timestamp when winner was determined
- Unique constraint on (year, month, clip_id)

### Modified Tables

#### `votes`
- Added `voting_round` column (default: 'monthly')
- Values: 'monthly' for regular voting, 'second' for second voting round
- Updated unique constraint to (ip_hash, voting_round)

## GitHub Actions Workflows

### 1. Start Second Voting Round
**File**: `.github/workflows/start-second-voting.yml`

**Trigger**: Manual (workflow_dispatch)

**Inputs**:
- `source_year`: Year of monthly results to use (YYYY)
- `source_month`: Month of monthly results to use (1-12)
- `duration_days`: Duration of second voting in days (default: 7)

**What it does**:
1. Fetches top 10 clips from specified monthly results
2. Checks that end date won't overlap with next automatic voting
3. Clears previous second voting round votes
4. Replaces current clips with top 10 from monthly results
5. Activates second voting configuration

**Example usage**:
```bash
# Via GitHub UI: Actions → Start Second Voting Round → Run workflow
# Inputs: source_year=2026, source_month=1, duration_days=7
```

### 2. End Second Voting Round
**File**: `.github/workflows/end-second-voting.yml`

**Trigger**: Manual (workflow_dispatch)

**What it does**:
1. Fetches all clips and votes from second voting round
2. Calculates results based on vote counts
3. Replaces the original monthly results with second voting results
4. Saves winner(s) to clip_des_jahres table
5. Cleans up old year's data if applicable
6. Clears second voting votes
7. Deactivates second voting configuration

**Example usage**:
```bash
# Via GitHub UI: Actions → End Second Voting Round → Run workflow
```

### 3. Check Second Voting Expiry
**File**: `.github/workflows/check-second-voting-expiry.yml`

**Trigger**: 
- Scheduled (daily at midnight UTC)
- Manual (workflow_dispatch)

**What it does**:
1. Checks if there's an active second voting round
2. If expired (past end date), automatically aborts it
3. Clears second voting votes
4. Deactivates second voting configuration

## Frontend Changes

### Updated Files

#### `js/clip-voting.js`
- Added support for detecting active second voting rounds
- Separate vote tracking for second voting (localStorage key: `cdm_voted_clip_second`)
- Special UI indicators for second voting rounds
- Passes voting_round parameter when submitting votes

#### `js/supabase-client.js`
- Added `getSecondVotingConfig()` function
- Updated `submitVoteToDB()` to support voting_round parameter
- Added `fetchClipDesJahres()` function

### New Files

#### `cdj.html`
New page for displaying Clip des Jahres winners at `/cdj` endpoint

#### `js/clip-des-jahres.js`
JavaScript for displaying Clip des Jahres organized by months:
- Fetches winners from current year
- Organizes by month (most recent first)
- Displays clips without voting functionality
- Similar design to Clip des Monats

#### `css/clip-voting.css` (updated)
Added styles for:
- Second voting notice banner
- Clip des Jahres month sections
- Winner card highlighting
- Responsive layouts

### Navigation

Added link to `/cdj` page in `index.html`:
```html
<a class="link-card" href="cdj.html" target="_self" rel="noopener">
    <img src="img/Logos/CDM.svg" alt="Clip des Jahres" class="icon">
    <div class="card-text">
        <strong>Clip des Jahres</strong>
        <span>Die Gewinner der zweiten Voting-Runde</span>
    </div>
</a>
```

## Usage Flow

### Starting a Second Voting Round

1. Ensure monthly voting has completed and results are saved
2. Go to GitHub Actions → "Start Second Voting Round"
3. Click "Run workflow"
4. Enter:
   - Source year (e.g., 2026)
   - Source month (e.g., 1 for January)
   - Duration in days (e.g., 7)
5. Click "Run workflow"
6. The system will:
   - Validate inputs
   - Check for conflicts with automatic voting
   - Load top 10 clips from specified month
   - Activate second voting on the website

### During Second Voting

- Users can visit the Clip des Monats page
- They'll see a special banner indicating second voting is active
- They can vote once (tracked separately from monthly voting)
- Voting interface shows top 10 clips from the specified month

### Ending Second Voting

1. Before the end date, go to GitHub Actions → "End Second Voting Round"
2. Click "Run workflow"
3. The system will:
   - Calculate vote results
   - Replace monthly results with second voting results
   - Save winner(s) to Clip des Jahres
   - Clean up votes
   - Deactivate second voting

### Automatic Expiry

If second voting is not manually ended before the expiry date:
- Daily scheduled job checks for expired second voting
- Automatically aborts it without saving results
- Clears votes
- Deactivates configuration

### Viewing Clip des Jahres

1. Visit `/cdj` or click "Clip des Jahres" link on homepage
2. See winners organized by month
3. Most recent months appear first
4. Winners have special highlighting
5. No voting functionality (display only)

## Data Cleanup

### CDJ Cycle Cleanup

When ending a second voting round:
- System checks if this is December voting
- If yes, automatically deletes the previous CDJ cycle:
  - Deletes December from 2 years ago
  - Deletes January-November from last year
- This ensures only the current 12-month period (Dec-Nov) is stored

Example cleanup flow:
- Saving December 2026 results triggers cleanup
- Deletes: December 2024 and January-November 2025
- Keeps: December 2025, January-November 2026, and newly saved December 2026
- Next period will be: December 2026 - November 2027

## Security Considerations

1. **Workflow Permissions**: Only repository administrators can trigger workflows
2. **Vote Integrity**: 
   - IP-based voting (hashed)
   - Separate tracking for monthly vs. second voting
   - Database-level constraints prevent duplicate votes
3. **RLS Policies**: All new tables have proper Row Level Security policies
4. **Input Validation**: All workflow inputs are validated before processing

## Error Handling

### Start Second Voting
- Validates source year/month exist
- Checks for overlap with automatic voting
- Prevents starting during active monthly voting
- Requires top 10 results to exist

### End Second Voting
- Checks if second voting is active
- Handles cases with no votes
- Ensures atomic database operations

### Expiry Check
- Safely handles non-existent configurations
- Logs all actions for debugging

## Testing Checklist

- [ ] Start second voting with valid inputs
- [ ] Verify clips appear on website
- [ ] Submit votes as different users
- [ ] End second voting manually
- [ ] Verify results are saved correctly
- [ ] Check Clip des Jahres page displays winners
- [ ] Test automatic expiry (adjust end date in past)
- [ ] Verify CDJ cycle cleanup works (December cleanup)
- [ ] Test overlap prevention with monthly voting
- [ ] Verify vote tracking is separate between rounds

## Troubleshooting

### Second voting not appearing on website
- Check `second_voting_config` table: is_active should be true
- Verify clips are loaded in the database
- Check browser console for JavaScript errors

### Votes not being counted
- Verify votes are being inserted with correct voting_round ('second')
- Check IP hash is being generated correctly
- Look for database constraint violations in logs

### Winners not appearing on /cdj
- Verify clip_des_jahres table has entries
- Check year matches current year
- Review browser console for fetch errors

### Automatic expiry not working
- Check workflow schedule is enabled
- Review workflow run logs in GitHub Actions
- Verify SUPABASE credentials are set in repository secrets

## Future Enhancements

Possible improvements:
1. Email notifications when second voting starts/ends
2. Admin dashboard for managing second voting
3. Multi-winner support (top 3 instead of just #1)
4. Historical archive of all past Clip des Jahres winners
5. Vote analytics and statistics
6. Custom duration per voting round (already supported in workflow)
