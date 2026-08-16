import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!user.value)
  const role = computed(() => user.value?.role || null)
  const permissions = computed(() => user.value?.permissions || [])

  const isAdmin = computed(() => ['admin', 'superadmin'].includes(role.value))
  const isSuperAdmin = computed(() => role.value === 'superadmin')
  const hasPermission = (action) => permissions.value.includes(action)

  const login = async (username, password) => {
    const { access_token } = await api.post('/auth/login', { username, password })

    localStorage.setItem('token', access_token)

    const me = await api.get('/auth/me')
    user.value = me
    localStorage.setItem('user', JSON.stringify(me))
  }

  const logout = () => {
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  return {
    user,
    isLoggedIn,
    role,
    permissions,
    isAdmin,
    isSuperAdmin,
    hasPermission,
    login,
    logout,
  }
})
