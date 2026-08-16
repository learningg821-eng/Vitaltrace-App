import { ref, onMounted } from 'vue'
import { requestNotificationPermission, listenForMessages } from '@/firebase/messaging'

const API_BASE = 'http://localhost:8000'

export const useAlert = () => {
  const activeAlert = ref(null)

  const getToken = () => localStorage.getItem('token')

  const registerFcmToken = async (fcmToken) => {
    const token = getToken()

    if (!token || !fcmToken) return

    const res = await fetch(`${API_BASE}/notifications/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        fcm_token: fcmToken,
      }),
    })

    if (!res.ok) {
      throw new Error(await res.text())
    }
  }

  const dismissAlert = async () => {
    if (!activeAlert.value) return

    if (activeAlert.value.id) {
      await fetch(`${API_BASE}/alerts/${activeAlert.value.id}/dismiss`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${getToken()}`,
        },
      })
    }

    activeAlert.value = null
  }

  onMounted(async () => {
    try {
      const fcmToken = await requestNotificationPermission()

      if (fcmToken) {
        await registerFcmToken(fcmToken)
      }

      listenForMessages((payload) => {
        ;('🚨 CRITICAL ALERT RECEIVED:', payload)

        activeAlert.value = {
          id: payload.data?.alert_id || null,
          patient_id: payload.data?.patient_id || null,
          vital_id: payload.data?.vital_id || null,
          status: payload.data?.ai_status || 'critical',

          title: payload.notification?.title || payload.data?.title || '🚨 CRITICAL ALERT',

          message: payload.notification?.body || payload.data?.body || 'Critical patient alert',

          created_at: new Date().toISOString(),
        }
      })
    } catch (error) {
      console.error('❌ Alert setup failed:', error)
    }
  })

  return {
    activeAlert,
    dismissAlert,
  }
}
