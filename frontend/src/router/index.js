import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Process from '../views/MainView.vue'
import SimulationView from '../views/SimulationView.vue'
import SimulationRunView from '../views/SimulationRunView.vue'
import ReportView from '../views/ReportView.vue'
import InteractionView from '../views/InteractionView.vue'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import AdminView from '../views/AdminView.vue'
import { useAuth } from '../store/auth.js'

const routes = [
  { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
  { path: '/', name: 'Home', component: Home },
  { path: '/process/:projectId', name: 'Process', component: Process, props: true },
  { path: '/simulation/:simulationId', name: 'Simulation', component: SimulationView, props: true },
  { path: '/simulation/:simulationId/start', name: 'SimulationRun', component: SimulationRunView, props: true },
  { path: '/report/:reportId', name: 'Report', component: ReportView, props: true },
  { path: '/interaction/:reportId', name: 'Interaction', component: InteractionView, props: true },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView },
  { path: '/admin', name: 'Admin', component: AdminView, meta: { requiresAdmin: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to) => {
  const { isAuthenticated, isAdmin } = useAuth()

  if (to.meta.public) {
    // Redirect already-logged-in users away from /login
    if (isAuthenticated.value && to.name === 'Login') return { name: 'Home' }
    return true
  }

  if (false && !isAuthenticated.value) return { name: 'Login', query: { redirect: to.fullPath } }

  if (to.meta.requiresAdmin && !isAdmin.value) return { name: 'Home' }

  return true
})

export default router
