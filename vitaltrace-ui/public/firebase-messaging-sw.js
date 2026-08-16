importScripts('https://www.gstatic.com/firebasejs/12.0.0/firebase-app-compat.js')
importScripts('https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging-compat.js')

firebase.initializeApp({
  apiKey: 'AIzaSyCGMJBwoCSvNeXzg0x_I1ZCbRs18n0tzA0',
  authDomain: 'vitaltrace-489dc.firebaseapp.com',
  projectId: 'vitaltrace-489dc',
  storageBucket: 'vitaltrace-489dc.firebasestorage.app',
  messagingSenderId: '776543917158',
  appId: '1:776543917158:web:cb88341bdb23576a3549a7',
})

const messaging = firebase.messaging()

messaging.onBackgroundMessage((payload) => {
  ;('🔥 Background FCM:', payload)

  const notificationTitle = payload.notification?.title || payload.data?.title || 'Emergency Alert'

  const notificationOptions = {
    body: payload.notification?.body || payload.data?.body || 'New emergency alert received',

    icon: '/favicon.ico',
    badge: '/favicon.ico',

    requireInteraction: true,

    vibrate: [200, 100, 200, 100, 200],

    actions: [
      {
        action: 'acknowledge',
        title: '✅ Acknowledge',
      },
    ],

    data: payload.data || {},
  }

  self.registration.showNotification(notificationTitle, notificationOptions)
})

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  if (event.action === 'acknowledge') {
    const alertId = event.notification.data?.alert_id
    const token = null // can't access localStorage in SW

    // Open the app
    event.waitUntil(clients.openWindow(`/?alert_id=${alertId}`))
  } else {
    event.waitUntil(clients.openWindow('/'))
  }
})
