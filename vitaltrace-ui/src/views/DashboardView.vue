<template>
  <v-container fluid class="pa-0">
    <!-- Stats Cards -->
    <v-row class="mb-4">
      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl elevation-1 pa-4" border="0">
          <div class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption text-grey-darken-1 mb-1">Total Patients</p>
              <p class="text-h5 font-weight-bold">{{ stats.total_patients }}</p>
            </div>
            <v-icon size="40" color="teal-darken-2">mdi-account-group</v-icon>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl elevation-1 pa-4" border="0">
          <div class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption text-grey-darken-1 mb-1">Total Staff</p>
              <p class="text-h5 font-weight-bold">{{ stats.total_staff }}</p>
            </div>
            <v-icon size="40" color="teal-darken-2">mdi-doctor</v-icon>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl elevation-1 pa-4" border="0">
          <div class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption text-grey-darken-1 mb-1">Critical Alerts</p>
              <p class="text-h5 font-weight-bold text-red">{{ stats.critical_count }}</p>
            </div>
            <v-icon size="40" color="red">mdi-alert-circle</v-icon>
          </div>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="rounded-xl elevation-1 pa-4" border="0">
          <div class="d-flex align-center justify-space-between">
            <div>
              <p class="text-caption text-grey-darken-1 mb-1">Warnings</p>
              <p class="text-h5 font-weight-bold text-orange">{{ stats.warning_count }}</p>
            </div>
            <v-icon size="40" color="orange">mdi-alert</v-icon>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <!-- Bottom Row -->
    <v-row>
      <!-- AI Vitals Summary -->
      <v-col cols="12" md="4" class="d-flex">
        <v-card class="rounded-xl elevation-1 pa-5 w-100" border="0">
          <p class="text-subtitle-2 font-weight-bold mb-5">AI Vitals Summary</p>
          <v-list density="compact" class="pa-0">
            <v-list-item class="px-0 mb-2">
              <template #prepend>
                <v-chip color="green" variant="flat" size="small" class="mr-3">Normal</v-chip>
              </template>
              <template #append>
                <span class="font-weight-bold text-body-1">{{ stats.normal_count }}</span>
              </template>
            </v-list-item>
            <v-divider />
            <v-list-item class="px-0 mb-2 mt-2">
              <template #prepend>
                <v-chip color="orange" variant="flat" size="small" class="mr-3">Warning</v-chip>
              </template>
              <template #append>
                <span class="font-weight-bold text-body-1">{{ stats.warning_count }}</span>
              </template>
            </v-list-item>
            <v-divider />
            <v-list-item class="px-0 mt-2">
              <template #prepend>
                <v-chip color="red" variant="flat" size="small" class="mr-3">Critical</v-chip>
              </template>
              <template #append>
                <span class="font-weight-bold text-body-1">{{ stats.critical_count }}</span>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- Recent Vitals -->
      <v-col cols="12" md="8" class="d-flex">
        <v-card class="rounded-xl elevation-1 w-100" border="0">
          <v-card-title class="py-4 px-6 text-subtitle-1 font-weight-bold">
            Recent Vitals
          </v-card-title>
          <v-data-table
            :headers="headers"
            :items="stats.recent_vitals"
            :loading="loading"
            density="comfortable"
            hide-default-footer
            class="px-2 pb-4"
          >
            <template #item.ai_status="{ item }">
              <v-chip
                :color="statusColor(item.ai_status)"
                variant="flat"
                size="small"
                class="font-weight-medium"
              >
                {{ item.ai_status }}
              </v-chip>
            </template>
            <template #item.created_at="{ item }">
              {{ new Date(item.created_at).toLocaleString() }}
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const loading = ref(false)
const stats = ref({
  total_patients: 0,
  total_staff: 0,
  critical_count: 0,
  warning_count: 0,
  normal_count: 0,
  recent_vitals: [],
})

const headers = [
  { title: 'Patient ID', key: 'patient_id' },
  { title: 'HR (BPM)', key: 'heart_rate' },
  { title: 'SpO2 (%)', key: 'spo2' },
  { title: 'Temp (°C)', key: 'temperature' },
  { title: 'Status', key: 'ai_status' },
  { title: 'Time', key: 'created_at' },
]

const statusColor = (status) => {
  if (status === 'critical') return 'red'
  if (status === 'warning') return 'orange'
  return 'green'
}

const fetchStats = async () => {
  loading.value = true
  try {
    stats.value = await api.get('/dashboard/stats')
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchStats)
</script>
