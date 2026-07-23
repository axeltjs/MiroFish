<template>
  <div class="login-bg">
    <div class="login-card">

      <div class="brand">
        <div class="brand-mark">
          <img src="../assets/logo/mmc-logo.png" alt="MMC" class="brand-logo" />
        </div>
        <div>
          <div class="brand-name">MIROFISH</div>
          <div class="brand-sub">MMKSI internal · prediction engine</div>
        </div>
      </div>

      <div class="form-section">
        <div class="form-group">
          <label class="field-label">Email</label>
          <input
            v-model="email"
            type="email"
            placeholder="you@mitsubishi-motors.co.id"
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="form-group">
          <label class="field-label">Password</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </div>

        <div v-if="errorMsg" class="error-box">
          <i class="ti ti-alert-circle"></i> {{ errorMsg }}
        </div>

        <button class="btn-primary" @click="handleLogin" :disabled="loading || !canSubmit">
          <span v-if="!loading">Sign in <i class="ti ti-arrow-right"></i></span>
          <span v-else>Signing in…</span>
        </button>
      </div>

      <p class="footer-note">
        <i class="ti ti-lock"></i> Access by invitation only — contact your administrator.
      </p>

    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../store/auth.js'

const router = useRouter()
const { signIn } = useAuth()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const canSubmit = computed(() => email.value.trim() !== '' && password.value !== '')

async function handleLogin() {
  if (!canSubmit.value || loading.value) return
  loading.value = true
  errorMsg.value = ''
  try {
    await signIn(email.value.trim(), password.value)
    router.replace({ name: 'Home' })
  } catch (err) {
    errorMsg.value = err.message ?? 'Sign-in failed. Check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
* { box-sizing: border-box; }

.login-bg {
  min-height: 100vh;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  font-family: 'Space Grotesk', -apple-system, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 12px;
  padding: 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 28px;
  padding-bottom: 24px;
  border-bottom: 1px solid #e3e3e0;
}

.brand-mark {
  width: 32px;
  height: 32px;
  border-radius: 7px;
  background: #fff;
  border: 1px solid #e3e3e0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  padding: 4px;
}

.brand-logo { width: 100%; height: 100%; object-fit: contain; }

.brand-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 15px;
  letter-spacing: 0.5px;
  color: #36454f;
}

.brand-sub {
  font-size: 11px;
  color: #708090;
  font-family: 'JetBrains Mono', monospace;
}

.form-section { display: flex; flex-direction: column; gap: 16px; }

.form-group { display: flex; flex-direction: column; gap: 6px; }

.field-label {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: #36454f;
}

input {
  width: 100%;
  border: 1px solid #e3e3e0;
  border-radius: 8px;
  padding: 11px 13px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 13px;
  color: #36454f;
  background: #fbfbfa;
  outline: none;
  transition: border-color 0.15s;
}

input:focus { border-color: #708090; background: #fff; }
input:disabled { opacity: 0.5; cursor: not-allowed; }
input::placeholder { color: #a0a0a0; }

.error-box {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 12px;
  color: #c0392b;
  background: #fdf3f2;
  border: 1px solid #f5c6c2;
  border-radius: 7px;
  padding: 10px 12px;
  font-family: 'JetBrains Mono', monospace;
}

.btn-primary {
  width: 100%;
  background: #E60012;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 13px 20px;
  font-size: 14px;
  font-weight: 700;
  font-family: 'Space Grotesk', sans-serif;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) { background: #B8000E; }

.btn-primary:disabled {
  background: #e3e3e0;
  color: #a0a0a0;
  cursor: not-allowed;
}

.footer-note {
  margin-top: 20px;
  font-size: 11px;
  color: #a0a0a0;
  font-family: 'JetBrains Mono', monospace;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}
</style>
