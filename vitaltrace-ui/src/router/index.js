import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '@/views/LoginView.vue'
import DashboardView from '@/views/DashboardView.vue'
import PatientRecordsView from '@/views/PatientRecordsView.vue'
import VitalsView from '@/views/VitalsView.vue'
import BlockchainLedgerView from '@/views/BlockchainLedgerView.vue'
import StaffManagementView from '@/views/StaffManagementView.vue'

const routes = [
  { path: '/login', name: 'Login', component: LoginView, meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', name: 'Dashboard', component: DashboardView },
  { path: '/patients', name: 'PatientRecords', component: PatientRecordsView },
  { path: '/vitals', name: 'VitalsLogs', component: VitalsView },
  { path: '/ledger', name: 'BlockchainLedger', component: BlockchainLedgerView },
  { path: '/staff', name: 'StaffManagement', component: StaffManagementView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Route guard
router.beforeEach((to) => {
  const token = localStorage.getItem('token')

  if (!to.meta.public && !token) {
    return '/login'
  }

  if (to.path === '/login' && token) {
    return '/dashboard'
  }
})

export default router
