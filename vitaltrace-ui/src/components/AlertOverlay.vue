<template>
  <v-overlay
    v-if="activeAlert"
    :model-value="show"
    persistent
    class="align-center justify-center"
    style="z-index: 9999"
  >
    <v-card class="rounded-xl pa-6 text-center" width="480" color="red-darken-3" dark>
      <div class="d-flex justify-center mb-4">
        <v-icon icon="mdi-alert-circle" size="80" color="white" class="alert-pulse" />
      </div>

      <v-card-title class="text-h5 font-weight-bold text-white justify-center mb-2">
        🚨 CRITICAL EMERGENCY
      </v-card-title>

      <v-card-subtitle class="text-white mb-4">
        {{ activeAlert.title }}
      </v-card-subtitle>

      <v-card-text class="text-white text-body-1 mb-4">
        {{ activeAlert.message }}
      </v-card-text>

      <v-card-text class="text-white text-caption mb-4">
        {{ formatTime(activeAlert.created_at) }}
      </v-card-text>

      <v-btn
        color="white"
        variant="flat"
        class="text-red-darken-3 font-weight-bold px-8"
        size="large"
        @click="handleDismiss"
      >
        ✅ Acknowledge & Dismiss
      </v-btn>
    </v-card>
  </v-overlay>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useAlert } from '@/composables/useAlert'

const { activeAlert, dismissAlert } = useAlert()

const show = ref(false)
let audio = null

// ─── Audio ───────────────────────────────────────────────────────
const playAlertSound = () => {
  stopSound()
  audio = new Audio('/alert.wav')
  audio.loop = true
  audio.volume = 1.0
  audio.play().catch((err) => console.warn('Audio play failed:', err))
}

const stopSound = () => {
  if (audio) {
    audio.pause()
    audio.currentTime = 0
    audio = null
  }
}

// ─── Push Notification ───────────────────────────────────────────
const requestNotificationPermission = async () => {
  if (!('Notification' in window)) return
  if (Notification.permission === 'default') {
    await Notification.requestPermission()
  }
}

const sendPushNotification = (alert) => {
  if (!('Notification' in window)) return
  if (Notification.permission !== 'granted') return
  new Notification('🚨 CRITICAL ALERT', {
    body: alert.message || alert.title,
    icon: '/favicon.ico',
    requireInteraction: true,
    silent: false,
  })
}

// ─── Visibility: resume sound when tab comes back ─────────────────
const handleVisibilityChange = () => {
  if (document.visibilityState === 'visible' && activeAlert.value) {
    playAlertSound()
  }
}

// ─── Handlers ────────────────────────────────────────────────────
const handleDismiss = async () => {
  stopSound()
  show.value = false
  await dismissAlert()
}

const formatTime = (dt) => new Date(dt).toLocaleString()

// ─── Watchers ────────────────────────────────────────────────────
watch(
  activeAlert,
  (val) => {
    if (val) {
      show.value = true
      playAlertSound()
      sendPushNotification(val)
    } else {
      show.value = false
      stopSound()
    }
  },
  { immediate: true },
)

// ─── Lifecycle ───────────────────────────────────────────────────
onMounted(() => {
  requestNotificationPermission()
  document.addEventListener('visibilitychange', handleVisibilityChange)
})

onUnmounted(() => {
  stopSound()
  document.removeEventListener('visibilitychange', handleVisibilityChange)
})
</script>

<style scoped>
.alert-pulse {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
