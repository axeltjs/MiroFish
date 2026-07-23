import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'
import { useAuth } from './store/auth.js'

const { init } = useAuth()

// Resolve auth session before mounting so route guards have state on first navigation
init().then(() => {
  const app = createApp(App)
  app.use(router)
  app.use(i18n)
  app.mount('#app')
})
