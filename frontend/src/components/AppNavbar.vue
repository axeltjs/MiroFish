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
        <div class="user-info">
          <div class="avatar" :style="{ background: avatarColor }">{{ userInitial }}</div>
          <span class="user-email">{{ userEmail }}</span>
        </div>
        <button class="btn-logout" @click="handleLogout" title="Keluar dari aplikasi">
          <i class="ti ti-logout"></i>
          <span>Keluar</span>
        </button>
      </div>

    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '../store/auth.js'

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
  color: #36454f;
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
  color: #36454f;
}

.nav-item.active {
  background: #f0f0ee;
  color: #36454f;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 9px;
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
