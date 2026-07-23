-- ================================================================
-- MiroFish Supabase Schema
-- Run this in the Supabase SQL Editor (Dashboard > SQL Editor)
-- ================================================================

-- IMPORTANT: After running this schema, go to:
--   Authentication > Providers > Email
--   and DISABLE "Allow new users to sign up" to block self-registration.
--
-- To create the first admin user:
--   1. Invite them via Authentication > Users > Invite user
--   2. After they accept and sign in, run:
--      UPDATE public.profiles SET role = 'admin' WHERE email = 'admin@example.com';

-- ================================================================
-- 1. profiles — must exist before is_admin() references it
-- ================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
  id          UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email       TEXT,
  full_name   TEXT DEFAULT '',
  role        TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
  is_active   BOOLEAN NOT NULL DEFAULT TRUE,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ================================================================
-- 2. is_admin() helper — SECURITY DEFINER bypasses RLS recursion
--    Must be created AFTER profiles table exists.
-- ================================================================
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN
LANGUAGE sql SECURITY DEFINER STABLE
SET search_path = public AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin'
  );
$$;

-- ================================================================
-- 3. RLS policies for profiles
-- ================================================================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Users see only their own row; admins see all
CREATE POLICY "profiles_select"
  ON public.profiles FOR SELECT TO authenticated
  USING (id = auth.uid() OR public.is_admin());

-- Only admins can update (role / active changes)
CREATE POLICY "profiles_update"
  ON public.profiles FOR UPDATE TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- ================================================================
-- 4. Auto-create profile on new user signup
-- ================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', '')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ================================================================
-- 5. simulation_logs — token usage per simulation run
-- ================================================================
CREATE TABLE IF NOT EXISTS public.simulation_logs (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id             UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  simulation_id       TEXT NOT NULL,
  project_id          TEXT,
  date                DATE DEFAULT CURRENT_DATE,
  phase               TEXT DEFAULT 'simulation',
  model               TEXT,
  tokens_in           INTEGER DEFAULT 0,
  tokens_out          INTEGER DEFAULT 0,
  total_tokens        INTEGER DEFAULT 0,
  estimated_cost_usd  NUMERIC(12, 8) DEFAULT 0,
  created_at          TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.simulation_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "logs_select"
  ON public.simulation_logs FOR SELECT TO authenticated
  USING (user_id = auth.uid() OR public.is_admin());

CREATE POLICY "logs_insert"
  ON public.simulation_logs FOR INSERT TO authenticated
  WITH CHECK (user_id = auth.uid());

-- ================================================================
-- 6. settings — admin-configurable key/value store
-- ================================================================
CREATE TABLE IF NOT EXISTS public.settings (
  key         TEXT PRIMARY KEY,
  value       JSONB NOT NULL,
  updated_by  UUID REFERENCES auth.users(id),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE public.settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "settings_select"
  ON public.settings FOR SELECT TO authenticated USING (TRUE);

CREATE POLICY "settings_upsert"
  ON public.settings FOR ALL TO authenticated
  USING (public.is_admin())
  WITH CHECK (public.is_admin());

-- Default token pricing (USD per 1M tokens)
INSERT INTO public.settings (key, value) VALUES (
  'token_pricing',
  '{
    "default":       {"input_per_1m": 0.15,  "output_per_1m": 0.60},
    "gpt-4o":        {"input_per_1m": 2.50,  "output_per_1m": 10.00},
    "gpt-4o-mini":   {"input_per_1m": 0.15,  "output_per_1m": 0.60},
    "gpt-4-turbo":   {"input_per_1m": 10.00, "output_per_1m": 30.00},
    "qwen-plus":     {"input_per_1m": 0.08,  "output_per_1m": 0.24},
    "qwen-max":      {"input_per_1m": 0.40,  "output_per_1m": 1.20},
    "qwen-vl-plus":  {"input_per_1m": 0.08,  "output_per_1m": 0.24}
  }'::jsonb
) ON CONFLICT (key) DO NOTHING;
