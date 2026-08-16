<template>
  <!-- Floating Button -->
  <div class="chatbot-wrapper">
    <v-btn
      v-if="!open"
      icon
      color="teal-darken-2"
      size="large"
      class="chatbot-fab"
      @click="open = true"
    >
      <v-icon>mdi-robot</v-icon>
    </v-btn>

    <!-- Chat Window -->
    <v-card v-if="open" class="chatbot-window elevation-8 rounded-xl">
      <!-- Header -->
      <v-card-title class="d-flex align-center py-3 px-4 bg-teal-darken-2">
        <v-icon color="white" class="mr-2">mdi-robot</v-icon>
        <span class="text-white text-subtitle-2 font-weight-bold">VitalTrace Chat</span>
        <v-spacer />
        <v-btn icon size="small" variant="text" @click="open = false">
          <v-icon color="white">mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <!-- Messages -->
      <v-card-text class="chatbot-messages pa-3" ref="messagesContainer">
        <div v-if="messages.length === 0" class="text-center text-grey mt-4">
          <v-icon size="40" color="teal-lighten-2">mdi-robot-outline</v-icon>
          <p class="text-caption mt-2">Ask me about patients, vitals, or alerts.</p>
        </div>

        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="mb-3"
          :class="msg.role === 'user' ? 'd-flex justify-end' : 'd-flex justify-start'"
        >
          <v-chip
            :color="msg.role === 'user' ? 'teal-darken-2' : 'grey-lighten'"
            :text-color="msg.role === 'user' ? 'white' : 'black'"
            class="chatbot-bubble text-caption pa-3"
            label
          >
            {{ msg.text }}
          </v-chip>
        </div>

        <div v-if="loading" class="d-flex justify-start mb-2">
          <v-chip color="grey-lighten-3" class="text-caption pa-3" label>
            <v-progress-circular size="12" width="2" indeterminate class="mr-2" />
            Thinking...
          </v-chip>
        </div>
      </v-card-text>

      <!-- Input -->
      <v-card-actions class="pa-3 pt-0">
        <v-text-field
          v-model="input"
          placeholder="Ask something..."
          density="compact"
          variant="outlined"
          hide-details
          class="mr-2"
          @keyup.enter="sendMessage"
        />
        <v-btn icon color="teal-darken-2" :disabled="loading || !input.trim()" @click="sendMessage">
          <v-icon>mdi-send</v-icon>
        </v-btn>
      </v-card-actions>
    </v-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { api } from '@/services/api'

const open = ref(false)
const input = ref('')
const loading = ref(false)
const messages = ref([])
const messagesContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.$el.scrollTop = messagesContainer.value.$el.scrollHeight
  }
}

const sendMessage = async () => {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', text })
  input.value = ''
  loading.value = true
  await scrollToBottom()

  try {
    const res = await api.post('/chat/', { message: text })
    messages.value.push({ role: 'bot', text: res.reply })
  } catch (err) {
    messages.value.push({ role: 'bot', text: 'Something went wrong. Try again.' })
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}
</script>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
}

.chatbot-fab {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.chatbot-window {
  width: 340px;
  height: 480px;
  display: flex;
  flex-direction: column;
  position: absolute;
  bottom: 0;
  right: 0;
}

.chatbot-messages {
  flex: 1;
  overflow-y: auto;
  max-height: 340px;
}

.chatbot-bubble {
  max-width: 240px;
  white-space: normal;
  height: auto !important;
  word-break: break-word;
  line-height: 1.5;
}
</style>
