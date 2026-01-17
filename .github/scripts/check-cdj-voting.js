const { 
  getSupabaseClient, 
  getClipDesJahresVotingConfig,
  setClipDesJahresVotingConfig
} = require('./db-helper');

const { execSync } = require('child_process');

async function main() {
  // Initialize Supabase
  const supabase = getSupabaseClient();
  
  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1; // 1-12
  const currentDay = now.getDate();
  
  console.log(`Checking Clip des Jahres voting automation (${currentYear}-${currentMonth}-${currentDay})...`);
  
  // Get CDJ voting config
  const config = await getClipDesJahresVotingConfig(supabase);
  
  if (config && config.is_active) {
    // Check if voting should be ended (December 21 at 23:59 or later)
    const endsAt = new Date(config.ends_at);
    
    if (now >= endsAt) {
      console.log(`Clip des Jahres voting expired at ${endsAt.toISOString()}`);
      console.log('Auto-ending Clip des Jahres voting...');
      
      try {
        execSync('node .github/scripts/end-cdj-voting.js', { 
          stdio: 'inherit',
          env: {
            ...process.env,
            SUPABASE_URL: process.env.SUPABASE_URL,
            SUPABASE_PUBLISHABLE_KEY: process.env.SUPABASE_PUBLISHABLE_KEY
          }
        });
        console.log('Clip des Jahres voting ended successfully');
      } catch (error) {
        console.error('Error ending Clip des Jahres voting:', error);
        // Deactivate to prevent continuous retries
        await setClipDesJahresVotingConfig(supabase, { is_active: false });
      }
    } else {
      const hoursRemaining = Math.round((endsAt - now) / (1000 * 60 * 60));
      console.log(`Clip des Jahres voting is still active (${hoursRemaining} hours remaining)`);
    }
  } else if (currentMonth === 12 && currentDay >= 15) {
    // Check if we should auto-start voting
    // Auto-start on December 15th if not already started
    
    // Check if voting was already started and ended this year
    if (config && !config.is_active && config.target_year === currentYear) {
      console.log(`Clip des Jahres voting for ${currentYear} was already completed`);
      return;
    }
    
    // Check if we haven't started yet
    if (!config || config.target_year !== currentYear) {
      console.log(`Auto-starting Clip des Jahres voting for year ${currentYear}...`);
      
      try {
        // Calculate duration: from now until December 21 at 23:59
        const targetEndDate = new Date(currentYear, 11, 21, 23, 59, 59, 999); // December 21
        const durationDays = Math.ceil((targetEndDate - now) / (1000 * 60 * 60 * 24));
        
        execSync('node .github/scripts/start-cdj-voting.js', { 
          stdio: 'inherit',
          env: {
            ...process.env,
            SUPABASE_URL: process.env.SUPABASE_URL,
            SUPABASE_PUBLISHABLE_KEY: process.env.SUPABASE_PUBLISHABLE_KEY,
            TARGET_YEAR: currentYear.toString(),
            DURATION_DAYS: Math.max(1, durationDays).toString(),
            AUTO_START: 'true'
          }
        });
        console.log('Clip des Jahres voting started successfully');
      } catch (error) {
        console.error('Error auto-starting Clip des Jahres voting:', error);
      }
    }
  } else {
    console.log('No action needed for Clip des Jahres voting automation');
  }
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
