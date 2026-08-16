<template>
  <v-app class="bg-teal-darken-2">
    <v-main class="d-flex align-center justify-center">
      <v-card class="rounded-xl pa-4" width="400">
        <!-- Logo -->
        <div class="d-flex align-center justify-center mb-6 mt-2">
          <v-icon color="teal-darken-2" icon="mdi-heart-pulse" size="36" class="me-2" />
          <span class="text-h6 font-weight-bold text-teal-darken-3">VitaChain Healthcare</span>
        </div>

        <v-card-title class="text-center text-subtitle-1 font-weight-bold text-grey-darken-3 mb-1">
          Sign in to your account
        </v-card-title>

        <!-- Error -->
        <v-alert v-if="error" type="error" class="mb-4 mx-4" density="compact" closable>
          {{ error }}
        </v-alert>

        <v-card-text>
          <v-form ref="formRef" v-model="isFormValid" @submit.prevent="handleLogin">
            <v-text-field
              v-model="form.username"
              label="Username"
              prepend-inner-icon="mdi-account-outline"
              variant="outlined"
              density="compact"
              autocomplete="username"
              class="mb-3"
              :rules="[requiredRule]"
              persistent-placeholder
              placeholder=" "
            />

            <v-text-field
              v-model="form.password"
              label="Password"
              prepend-inner-icon="mdi-lock-outline"
              :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
              :type="showPassword ? 'text' : 'password'"
              variant="outlined"
              density="compact"
              autocomplete="current-password"
              class="mb-4"
              :rules="[requiredRule]"
              @click:append-inner="showPassword = !showPassword"
              persistent-placeholder
              placeholder=" "
            />

            <v-btn
              type="submit"
              color="teal-darken-2"
              variant="flat"
              block
              class="text-capitalize"
              :loading="loading"
              :disabled="!isFormValid"
            >
              Sign In
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const isFormValid = ref(false)
const showPassword = ref(false)
const loading = ref(false)
const error = ref(null)

const form = ref({
  username: '',
  password: '',
})

const requiredRule = (v) => !!v || 'This field is required'

const handleLogin = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  loading.value = true
  error.value = null

  try {
    await authStore.login(form.value.username, form.value.password)
    router.push('/dashboard')
  } catch (err) {
    error.value = err.message || 'Invalid credentials'
  } finally {
    loading.value = false
  }
}
</script>
