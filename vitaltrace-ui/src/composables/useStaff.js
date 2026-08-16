import { ref } from 'vue'
import { api } from '@/services/api'

export const useStaff = () => {
  const staffList = ref([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref(null)

  const fetchStaff = async () => {
    loading.value = true
    error.value = null
    try {
      staffList.value = await api.get('/api/staff/')
    } catch (err) {
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  const createStaff = async (payload) => {
    saving.value = true
    error.value = null
    try {
      await api.post('/api/staff/', payload)
      await fetchStaff()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  const updateStaff = async (id, payload) => {
    saving.value = true
    error.value = null
    try {
      await api.put(`/api/staff/${id}`, payload)
      await fetchStaff()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      saving.value = false
    }
  }

  const deleteStaff = async (id) => {
    error.value = null
    try {
      await api.delete(`/api/staff/${id}`)
      await fetchStaff()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  return { staffList, loading, saving, error, fetchStaff, createStaff, updateStaff, deleteStaff }
}
