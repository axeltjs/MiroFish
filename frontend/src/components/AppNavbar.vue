<template>
  <nav class="navbar">
    <div class="navbar-inner">

      <!-- Brand -->
      <router-link to="/" class="brand">
        <div class="brand-mark">
          <img src="../assets/logo/mmc-logo.png" alt="MMC" />
        </div>
        <div class="brand-text">
          <span class="brand-name">MiroFish</span>
          <span class="brand-sub">MMKSI Prediction Engine</span>
        </div>
      </router-link>

      <!-- Nav items -->
      <div class="nav-items">
        <router-link to="/" class="nav-item" :class="{ active: route.name === 'Home' }">
          <i class="ti ti-home"></i>
          <span>Beranda</span>
        </router-link>
        <router-link to="/dashboard" class="nav-item" :class="{ active: route.name === 'Dashboard' }">
          <i class="ti ti-chart-bar"></i>
          <span>Penggunaan Saya</span>
        </router-link>
        <router-link v-if="isAdmin" to="/admin" class="nav-item" :class="{ active: route.name === 'Admin' }">
          <i class="ti ti-settings-2"></i>
          <span>Panel Admin</span>
        </router-link>
      </div>

      <!-- User area -->
      <div class="user-area">
        <div class="user-menu-wrap" ref="userMenuWrapRef">
          <button class="user-info" @click="showUserMenu = !showUserMenu">
            <div class="avatar" :style="{ background: avatarColor }">{{ userInitial }}</div>
            <span class="user-email">{{ userEmail }}</span>
            <i class="ti ti-chevron-down user-chevron" :class="{ open: showUserMenu }"></i>
          </button>
          <div v-if="showUserMenu" class="user-menu">
            <button class="user-menu-item" @click="openChangePassword">
              <i class="ti ti-key"></i>
              <span>Ubah Password</span>
            </button>
          </div>
        </div>
        <button class="btn-logout" @click="handleLogout" title="Keluar dari aplikasi">
          <i class="ti ti-logout"></i>
          <span>Keluar</span>
        </button>
      </div>

    </div>

    <ChangePasswordModal v-if="showChangePassword" @close="showChangePassword = false" />
  </nav>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../store/auth.js'
import ChangePasswordModal from './ChangePasswordModal.vue'

const route = useRoute()
const router = useRouter()
const { user, isAdmin, signOut } = useAuth()

const userEmail = computed(() => user.value?.email ?? '')
const userInitial = computed(() => userEmail.value.charAt(0).toUpperCase() || '?')

// Deterministic color from email so it's consistent per user
const avatarColor = computed(() => {
  const colors = ['#4f7fa0', '#5a8a6a', '#8a6a5a', '#7a6a8a', '#6a8a7a', '#8a7a4a']
  const email = userEmail.value
  const idx = email.split('').reduce((acc, c) => acc + c.charCodeAt(0), 0) % colors.length
  return colors[idx]
})

const showUserMenu = ref(false)
const showChangePassword = ref(false)
const userMenuWrapRef = ref(null)

function openChangePassword() {
  showUserMenu.value = false
  showChangePassword.value = true
}

function handleClickOutside(event) {
  if (showUserMenu.value && userMenuWrapRef.value && !userMenuWrapRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

async function handleLogout() {
  await signOut()
  router.replace({ name: 'Login' })
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 50;
  background: #ffffff;
  border-bottom: 1px solid #e3e3e0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* ── Brand ── */
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  flex-shrink: 0;
  margin-right: 16px;
}

.brand-mark {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #e3e3e0;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 5px;
  flex-shrink: 0;
}

.brand-mark img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.brand-text {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.brand-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.5px;
  color: #E60012;
  line-height: 1;
}

.brand-sub {
  font-size: 10px;
  color: #a0a0a0;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1;
  white-space: nowrap;
}

/* ── Nav items ── */
.nav-items {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 13px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: 'Space Grotesk', -apple-system, 'Segoe UI', sans-serif;
  color: #708090;
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}

.nav-item i {
  font-size: 16px;
  flex-shrink: 0;
}

.nav-item:hover {
  background: #f4f4f2;
  color: #E60012;
}

.nav-item.active {
  background: #f0f0ee;
  color: #E60012;
  font-weight: 700;
}

/* ── User area ── */
.user-area {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
  margin-left: auto;
}

.user-menu-wrap {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 9px;
  background: none;
  border: none;
  padding: 4px 6px;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  transition: background 0.15s;
}

.user-info:hover {
  background: #f4f4f2;
}

.user-chevron {
  font-size: 14px;
  color: #a0a0a0;
  transition: transform 0.15s;
}

.user-chevron.open {
  transform: rotate(180deg);
}

.user-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  min-width: 180px;
  background: #fff;
  border: 1px solid #e3e3e0;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  padding: 6px;
  z-index: 60;
}

.user-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 9px 10px;
  border: none;
  background: none;
  border-radius: 7px;
  font-size: 13px;
  font-family: 'Space Grotesk', sans-serif;
  color: #36454f;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.user-menu-item:hover {
  background: #f4f4f2;
}

.user-menu-item i {
  font-size: 15px;
  color: #708090;
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  color: #fff;
  font-size: 13px;
  font-weight: 700;
  font-family: 'Space Grotesk', sans-serif;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-email {
  font-size: 12px;
  font-family: 'JetBrains Mono', monospace;
  color: #708090;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 13px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  font-family: 'Space Grotesk', sans-serif;
  color: #708090;
  background: none;
  border: 1px solid #e3e3e0;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
  white-space: nowrap;
}

.btn-logout:hover {
  background: #fdf3f2;
  border-color: #f5c6c2;
  color: #c0392b;
}

.btn-logout i { font-size: 15px; }

@media (max-width: 640px) {
  .brand-sub { display: none; }
  .user-email { display: none; }
  .nav-item span { display: none; }
  .btn-logout span { display: none; }
  .nav-item { padding: 7px 10px; }
  .btn-logout { padding: 7px 10px; }
}
</style>
