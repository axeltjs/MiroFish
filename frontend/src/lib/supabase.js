import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('[MiroFish] VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY not set — auth features disabled.')
}

export const supabase = createClient(supabaseUrl || 'http://localhost', supabaseAnonKey || 'placeholder')
