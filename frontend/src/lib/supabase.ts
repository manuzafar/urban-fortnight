import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Create a placeholder client that won't crash the app when env vars are missing
let supabase: SupabaseClient;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase environment variables not set. Auth will not work.');
  // Use placeholder URL to prevent crash - auth features will be disabled
  supabase = createClient(
    'https://placeholder.supabase.co',
    'placeholder-key'
  );
} else {
  supabase = createClient(supabaseUrl, supabaseAnonKey);
}

export { supabase };
