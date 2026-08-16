import { getToken, onMessage } from 'firebase/messaging'
import { messaging, vapidKey } from './firebase'

export const requestNotificationPermission = async () => {
  try {
    const permission = await Notification.requestPermission()

    if (permission !== 'granted') {
      console.log('❌ Notification permission denied')
      return null
    }

    console.log('✅ Notification permission granted')

    const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js')

    console.log('✅ Service worker registered:', registration)

    const token = await getToken(messaging, {
      vapidKey: vapidKey,
      serviceWorkerRegistration: registration,
    })

    if (!token) {
      console.log('❌ Failed to get FCM token')
      return null
    }

    console.log('🔥 FCM Token:', token)

    return token
  } catch (error) {
    console.error('❌ FCM token error:', error)
    return null
  }
}

export const listenForMessages = (callback) => {
  return onMessage(messaging, (payload) => {
    console.log('🔥 Foreground FCM message:', payload)

    callback(payload)
  })
}
