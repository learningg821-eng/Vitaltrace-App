import { initializeApp } from 'firebase/app'
import { getMessaging } from 'firebase/messaging'

const firebaseConfig = {
  apiKey: 'AIzaSyCGMJBwoCSvNeXzg0x_I1ZCbRs18n0tzA0',
  authDomain: 'vitaltrace-489dc.firebaseapp.com',
  projectId: 'vitaltrace-489dc',
  storageBucket: 'vitaltrace-489dc.firebasestorage.app',
  messagingSenderId: '776543917158',
  appId: '1:776543917158:web:cb88341bdb23576a3549a7',
}

const app = initializeApp(firebaseConfig)

export const messaging = getMessaging(app)

export const vapidKey =
  'BDFBJDZBZlE_BqBr01TmXmZqNkl5Lq8_3giajKqL2kWn9xQmUDqBNzOS4M4irwkKOFBoQ1W86oXhpNL8RfZo59c'
