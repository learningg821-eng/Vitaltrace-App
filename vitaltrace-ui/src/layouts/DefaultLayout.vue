<template>
  <v-app class="bg-grey-lighten-4">
    <!-- 1. Left Sidebar Navigation -->
    <v-navigation-drawer v-model="drawer" width="260" class="border-e-0 elevation-0 px-2 py-4">
      <!-- Logo Header -->
      <div class="px-4 mb-4">
        <v-icon color="teal-darken-1" icon="mdi-heart-pulse" size="32" class="me-2" />
        <span class="text-h6 font-weight-bold text-teal-darken-3">VitaChain Healthcare</span>
      </div>

      <v-divider />

      <!-- Main Navigation Items -->
      <v-list density="compact" nav color="teal-darken-1">
        <v-list-item
          v-for="item in navItems"
          :key="item.value"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.value"
          :to="item.to"
          class="rounded-lg mb-1"
        />
      </v-list>

      <template v-slot:append>
        <v-divider />
        <div class="text-center">
          <p class="text-caption text-teal-darken-2 ma-0">VitalTrace © 2026</p>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- 2. Top Header Bar -->
    <v-app-bar flat color="teal-darken-2" class="px-4">
      <v-app-bar-nav-icon @click="drawer = !drawer" />
      <v-app-bar-title class="font-weight-medium text-subtitle-1">{{ pageTitle }}</v-app-bar-title
      ><v-spacer />

      <!-- User Profile Menu -->
      <v-menu location="bottom end" min-width="280">
        <template v-slot:activator="{ props }">
          <div v-bind="props" class="d-flex align-center cursor-pointer ms-2">
            <v-avatar size="36" color="teal-lighten-4" rounded="circle">
              <span class="text-teal-darken-2 font-weight-bold text-body-1">
                {{ authStore.user?.username?.charAt(0).toUpperCase() }}
              </span>
            </v-avatar>
          </div>
        </template>

        <v-list density="comfortable" class="mt-2 rounded-lg pa-2" width="250">
          <v-list-item
            :title="authStore.user?.username"
            :subtitle="authStore.user?.role"
            class="mb-1"
          >
            <template #title>
              <span class="text-h5 font-weight-bold">{{ authStore.user?.username }}</span>
            </template>

            <template #subtitle>
              <v-chip color="teal-darken-4" variant="flat" size="small" class="text-white">
                {{ authStore.user?.role }}
              </v-chip>
            </template>
          </v-list-item>
          <v-divider class="mb-1" />
          <v-list-item
            prepend-icon="mdi-logout"
            title="Logout"
            @click="handleLogout"
            class="rounded-lg mr-5"
          />
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- 3. Dynamic Page View Slot -->
    <v-main>
      <AlertOverlay v-if="authStore.isLoggedIn" />
      <v-container fluid class="pa-6">
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

import AlertOverlay from '@/components/AlertOverlay.vue'

const drawer = ref(true)
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const pageTitle = computed(() => {
  const current = navItems.find((item) => item.to === route.path)
  return current ? current.title : 'Patient Monitoring'
})

const navItems = [
  { title: 'Dashboard', icon: 'mdi-view-dashboard', value: 'dashboard', to: '/dashboard' },
  {
    title: 'Patient Records',
    icon: 'mdi-file-document-outline',
    value: 'records',
    to: '/patients',
  },
  { title: 'Vitals Logs', icon: 'mdi-pulse', value: 'vitals', to: '/vitals' },
  { title: 'Blockchain Ledger', icon: 'mdi-cube-outline', value: 'blockchain', to: '/ledger' },
  { title: 'Staff Management', icon: 'mdi-account-group-outline', value: 'staff', to: '/staff' },
]

const handleLogout = () => {
  authStore.logout()
}
</script>
