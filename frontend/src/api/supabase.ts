import { createClient } from '@supabase/supabase-js';

const supabaseUrl = (import.meta.env.VITE_SUPABASE_URL || '').trim();
const supabaseAnonKey = (import.meta.env.VITE_SUPABASE_ANON_KEY || '').trim();

// Safe fallback for pre-configuration/build time so Vite does not fail if env vars are unset
const defaultUrl = supabaseUrl || 'https://placeholder.supabase.co';
const defaultKey = supabaseAnonKey || 'placeholder-anon-key';

if (!supabaseUrl && typeof window !== 'undefined' && !window.location.hostname.includes('localhost')) {
  console.warn('SkillAlpha: VITE_SUPABASE_URL is not set. Supabase Auth will not work until configured in Vercel settings.');
}

export const supabase = createClient(defaultUrl, defaultKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    detectSessionInUrl: true,
  },
});

/**
 * Helper to get the current Supabase session access token
 */
export const getSupabaseToken = async (): Promise<string | null> => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || localStorage.getItem('skillalpha_token');
  } catch {
    return localStorage.getItem('skillalpha_token');
  }
};
