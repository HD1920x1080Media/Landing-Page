# Database Migration Guide - Second Voting Round Feature

## Overview
This guide helps you update your Supabase database to support the second voting round and Clip des Jahres features.

## Prerequisites
- Access to your Supabase project dashboard
- SQL Editor access in Supabase

## Migration Steps

### Step 1: Backup Current Data (Recommended)
Before making any changes, backup your current data:
1. Go to Supabase Dashboard → Database → Backups
2. Create a manual backup
3. Download a copy if desired

### Step 2: Update the votes table

Run this SQL to add the voting_round column:

```sql
-- Add voting_round column to votes table
ALTER TABLE votes ADD COLUMN IF NOT EXISTS voting_round TEXT DEFAULT 'monthly';

-- Drop the old unique constraint
ALTER TABLE votes DROP CONSTRAINT IF EXISTS votes_ip_hash_key;

-- Add new unique constraint
ALTER TABLE votes ADD CONSTRAINT votes_ip_hash_voting_round_unique UNIQUE (ip_hash, voting_round);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_votes_voting_round ON votes(voting_round);
```

### Step 3: Create second_voting_config table

```sql
-- Create second_voting_config table
CREATE TABLE IF NOT EXISTS second_voting_config (
    id BIGSERIAL PRIMARY KEY,
    is_active BOOLEAN DEFAULT FALSE,
    started_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    source_year INTEGER,
    source_month INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create index
CREATE INDEX IF NOT EXISTS idx_second_voting_config_is_active ON second_voting_config(is_active);

-- Enable RLS
ALTER TABLE second_voting_config ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Allow public read access to second_voting_config"
    ON second_voting_config FOR SELECT
    USING (true);

CREATE POLICY "Allow anon role to manage second_voting_config"
    ON second_voting_config FOR ALL
    USING (true);
```

### Step 4: Create clip_des_jahres table

```sql
-- Create clip_des_jahres table
CREATE TABLE IF NOT EXISTS clip_des_jahres (
    id BIGSERIAL PRIMARY KEY,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    clip_id TEXT NOT NULL,
    url TEXT NOT NULL,
    embed_url TEXT NOT NULL,
    broadcaster_id TEXT NOT NULL,
    broadcaster_name TEXT NOT NULL,
    creator_id TEXT NOT NULL,
    creator_name TEXT NOT NULL,
    video_id TEXT,
    game_id TEXT,
    language TEXT,
    title TEXT NOT NULL,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL,
    thumbnail_url TEXT,
    duration NUMERIC,
    vod_offset INTEGER,
    votes INTEGER DEFAULT 0,
    calculated_at TIMESTAMPTZ NOT NULL,
    UNIQUE(year, month, clip_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_clip_des_jahres_year_month ON clip_des_jahres(year, month);

-- Enable RLS
ALTER TABLE clip_des_jahres ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Allow public read access to clip_des_jahres"
    ON clip_des_jahres FOR SELECT
    USING (true);

CREATE POLICY "Allow anon role to manage clip_des_jahres"
    ON clip_des_jahres FOR ALL
    USING (true);
```

### Step 5: Verify Migration

Run these queries to verify the migration was successful:

```sql
-- Check if voting_round column exists
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'votes' AND column_name = 'voting_round';

-- Check if second_voting_config table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'second_voting_config';

-- Check if clip_des_jahres table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'clip_des_jahres';

-- Verify indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename IN ('votes', 'second_voting_config', 'clip_des_jahres');

-- Verify RLS policies
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename IN ('second_voting_config', 'clip_des_jahres');
```

### Step 6: Update Existing Votes (Optional)

If you have existing votes and want to ensure they're marked as 'monthly':

```sql
-- Update any existing votes without voting_round to 'monthly'
UPDATE votes 
SET voting_round = 'monthly' 
WHERE voting_round IS NULL;
```

## Rollback (If Needed)

If you need to rollback these changes:

```sql
-- Drop new tables
DROP TABLE IF EXISTS clip_des_jahres CASCADE;
DROP TABLE IF EXISTS second_voting_config CASCADE;

-- Revert votes table changes
ALTER TABLE votes DROP COLUMN IF EXISTS voting_round;
ALTER TABLE votes DROP CONSTRAINT IF EXISTS votes_ip_hash_voting_round_unique;
ALTER TABLE votes ADD CONSTRAINT votes_ip_hash_key UNIQUE (ip_hash);
DROP INDEX IF EXISTS idx_votes_voting_round;
```

## Post-Migration Steps

1. **Test the API**: Verify you can query the new tables
2. **Check Permissions**: Ensure RLS policies work as expected
3. **Monitor Logs**: Watch for any database errors in the first few days
4. **Update Documentation**: Record the migration date and any issues

## Troubleshooting

### Error: "relation 'votes' does not exist"
- Ensure you're running queries in the correct database
- Check that your schema is 'public'

### Error: "permission denied"
- Verify RLS policies are created correctly
- Check that anon key has proper permissions

### Unique constraint violation when updating votes
- This means some votes have duplicate (ip_hash, voting_round) combinations
- Run this to find duplicates:
```sql
SELECT ip_hash, voting_round, COUNT(*) 
FROM votes 
GROUP BY ip_hash, voting_round 
HAVING COUNT(*) > 1;
```
- Remove duplicates before adding the constraint

## Testing the Migration

After migration, test these scenarios:

1. **Read access**: Try fetching data from new tables via API
2. **Write access**: Try inserting test data
3. **Constraints**: Verify unique constraints work
4. **RLS**: Test that public read access works
5. **Indexes**: Check query performance on large datasets

## Support

If you encounter issues:
1. Check Supabase dashboard logs
2. Review the SQL error messages
3. Verify all steps were completed in order
4. Check the main `supabase-schema.sql` file for reference

## Complete Schema Reference

For the complete, up-to-date schema, see: `supabase-schema.sql`
