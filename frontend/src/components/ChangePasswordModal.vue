<template>
  <div class="modal-overlay" @click.self="handleClose">
    <div class="modal">
      <div class="modal-head">
        <span>Ubah Password</span>
        <button class="modal-close" @click="handleClose" :disabled="loading"><i class="ti ti-x"></i></button>
      </div>

      <div class="modal-body">
        <template v-if="!successMsg">
          <label class="field-label">Password saat ini</label>
          <input
            v-model="currentPassword"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            :disabled="loading"
          />

          <label class="field-label" style="margin-top:14px;">Password baru</label>
          <input
            v-model="newPassword"
            type="password"
            placeholder="Minimal 6 karakter"
            autocomplete="new-password"
            :disabled="loading"
          />

          <label class="field-label" style="margin-top:14px;">Ulangi password baru</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="••••••••"
            autocomplete="new-password"
            :disabled="loading"
            @keyup.enter="submit"
          />

          <div v-if="errorMsg" class="msg error" style="margin-top:12px;">
            <i class="ti ti-alert-circle"></i> {{ errorMsg }}
          </div>
        </template>

        <div v-else class="msg success standalone">
          <i class="ti ti-circle-check"></i> {{ successMsg }}
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" @click="handleClose" :disabled="loading">
          {{ successMsg ? 'Tutup' : 'Batal' }}
        </button>
        <button v-if="!successMsg" class="btn-action" @click="submit" :disabled="loading || !canSubmit">
          <span v-if="!loading"><i class="ti ti-key"></i> Simpan</span>
          <span v-else>Menyimpan…</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '../store/auth.js'

const emit = defineEmits(['close'])
const { changePassword } = useAuth()

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const canSubmit = computed(() =>
  currentPassword.value !== '' && newPassword.value !== '' && confirmPassword.value !== ''
)

async function submit() {
  if (loading.value) return
  errorMsg.value = ''

  if (!currentPassword.value || !newPassword.value || !confirmPassword.value) {
    errorMsg.value = 'Semua kolom wajib diisi.'
    return
  }
  if (newPassword.value.length < 6) {
    errorMsg.value = 'Password baru minimal 6 karakter.'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Konfirmasi password baru tidak cocok.'
    return
  }

  loading.value = true
  try {
    await changePassword(currentPassword.value, newPassword.value)
    successMsg.value = 'Password berhasil diperbarui.'
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (err) {
    errorMsg.value = err.message ?? 'Gagal memperbarui password.'
  } finally {
    loading.value = false
  }
}

function handleClose() {
  if (loading.value) return
  emit('close')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.3); backdrop-filter: blur(2px);
  display: flex; align-items: center; justify-content: center; z-index: 200;
}

.modal {
  background: #fff; border-radius: 12px; border: 1px solid #e3e3e0;
  width: 100%; max-width: 400px; overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
  font-family: 'Space Grotesk', -apple-system, 'Segoe UI', sans-serif;
}

.modal-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 20px; border-bottom: 1px solid #e3e3e0;
  font-weight: 700; font-size: 14px;
}

.modal-close {
  background: none; border: none; cursor: pointer; color: #708090;
  font-size: 18px; padding: 0; line-height: 1; transition: color 0.15s;
}
.modal-close:hover:not(:disabled) { color: #36454f; }
.modal-close:disabled { opacity: 0.5; cursor: not-allowed; }

.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 0; }

.modal-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 10px;
  padding: 14px 20px; border-top: 1px solid #e3e3e0;
}

.field-label {
  font-size: 12px; font-family: 'JetBrains Mono', monospace; font-weight: 700;
  color: #36454f; display: block; margin-bottom: 6px;
}

input[type="password"] {
  width: 100%; border: 1px solid #e3e3e0; border-radius: 7px; padding: 10px 13px;
  font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #36454f;
  background: #fbfbfa; outline: none; transition: border-color 0.15s;
}
input[type="password"]:focus { border-color: #708090; background: #fff; }
input[type="password"]:disabled { opacity: 0.5; cursor: not-allowed; }

.msg {
  display: flex; align-items: center; gap: 7px;
  font-size: 12px; font-family: 'JetBrains Mono', monospace;
  border-radius: 7px; padding: 10px 12px;
}
.msg.error { color: #c0392b; background: #fdf3f2; border: 1px solid #f5c6c2; }
.msg.success { color: #2d7a55; background: #eafaf1; border: 1px solid #b8e6c9; }
.msg.standalone { margin: 4px 0; }

.btn-action {
  background: #E60012; color: #fff; border: none; border-radius: 7px;
  padding: 9px 16px; font-size: 13px; font-weight: 700;
  font-family: 'Space Grotesk', sans-serif; cursor: pointer;
  display: flex; align-items: center; gap: 6px; transition: background 0.15s;
}
.btn-action:hover:not(:disabled) { background: #B8000E; }
.btn-action:disabled { background: #e3e3e0; color: #a0a0a0; cursor: not-allowed; }

.btn-secondary {
  background: none; color: #708090; border: 1px solid #e3e3e0; border-radius: 7px;
  padding: 9px 16px; font-size: 13px; font-family: 'Space Grotesk', sans-serif;
  cursor: pointer; transition: border-color 0.15s;
}
.btn-secondary:hover:not(:disabled) { border-color: #708090; }
.btn-secondary:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
