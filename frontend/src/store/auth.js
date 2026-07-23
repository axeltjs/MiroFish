import { ref, computed } from 'vue'
import { supabase } from '../lib/supabase.js'

// Module-level state — shared across all calls to useAuth()
const _session = ref(null)
const _profile = ref(null)
const _loading = ref(true)
let _initialized = false

async function _fetchProfile(userId) {
  const { data } = await supabase.from('profiles').select('*').eq('id', userId).single()
  _profile.value = data
}

export function useAuth() {
  const user = computed(() => _session.value?.user ?? null)
  const isAdmin = computed(() => _profile.value?.role === 'admin')
  const isAuthenticated = computed(() => !!_session.value)

  async function init() {
    if (_initialized) return
    _initialized = true
    _loading.value = true

    const { data: { session } } = await supabase.auth.getSession()
    _session.value = session
    if (session?.user) await _fetchProfile(session.user.id)
    _loading.value = false

    supabase.auth.onAuthStateChange(async (_event, session) => {
      _session.value = session
      if (session?.user) await _fetchProfile(session.user.id)
      else _profile.value = null
    })
  }

  async function signIn(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
    return data
  }

  async function signOut() {
    await supabase.auth.signOut()
    _session.value = null
    _profile.value = null
  }

  return {
    session: _session,
    profile: _profile,
    loading: _loading,
    user,
    isAdmin,
    isAuthenticated,
    init,
    signIn,
    signOut,
  }
}
