<template>
  <v-container fluid class="pa-0">
    <!-- Patient Selector -->
    <v-card class="rounded-xl mb-6 elevation-1 pa-4" border="0">
      <v-select
        v-model="selectedPatient"
        :items="patients"
        :item-title="(p) => `${p.firstName} ${p.lastName} (${p.patientId})`"
        item-value="id"
        label="Select Patient"
        variant="outlined"
        density="compact"
        hide-details
        style="max-width: 400px"
        return-object
      />
    </v-card>

    <!-- Vitals Input -->
    <v-card v-if="selectedPatient" class="rounded-xl elevation-1 pa-6" border="0">
      <v-card-title class="text-subtitle-1 font-weight-bold mb-4 px-0">
        Enter Vitals — {{ selectedPatient.firstName }} {{ selectedPatient.lastName }}
      </v-card-title>

      <v-row dense>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.heart_rate"
            label="Heart Rate (BPM)"
            variant="outlined"
            density="compact"
            type="number"
            prepend-inner-icon="mdi-heart-pulse"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.systolic_bp"
            label="Systolic BP (mmHg)"
            variant="outlined"
            density="compact"
            type="number"
            prepend-inner-icon="mdi-gauge"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.diastolic_bp"
            label="Diastolic BP (mmHg)"
            variant="outlined"
            density="compact"
            type="number"
            prepend-inner-icon="mdi-gauge-low"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.spo2"
            label="SpO2 (%)"
            variant="outlined"
            density="compact"
            type="number"
            prepend-inner-icon="mdi-lungs"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.temperature"
            label="Temperature (°C)"
            variant="outlined"
            density="compact"
            type="number"
            prepend-inner-icon="mdi-thermometer"
          />
        </v-col>
        <v-col cols="12" sm="4">
          <v-text-field
            v-model.number="form.respiratory_rate"
            label="Respiratory Rate (breaths/min)"
            variant="outlined"
            density="compact"
            type="number"
            prepend-inner-icon="mdi-air-filter"
          />
        </v-col>
      </v-row>

      <div class="d-flex justify-end mt-4">
        <v-btn
          color="teal-darken-2"
          variant="flat"
          class="text-capitalize px-8"
          :loading="submitting"
          @click="submitVitals"
        >
          Analyze & Submit
        </v-btn>
      </div>
    </v-card>

    <!-- AI Result -->
    <v-card v-if="aiResult" class="rounded-xl elevation-1 pa-6 mt-6" border="0">
      <v-card-title class="text-subtitle-1 font-weight-bold px-0 mb-2">AI Analysis</v-card-title>
      <v-chip
        :color="statusColor(aiResult.ai_status)"
        variant="flat"
        class="font-weight-bold mb-3 text-white"
        size="large"
      >
        {{ aiResult.ai_status?.toUpperCase() }}
      </v-chip>
      <p class="text-body-2 text-grey-darken-2">{{ aiResult.ai_notes }}</p>
      <p class="text-caption text-grey mt-2">Blockchain Hash: {{ aiResult.blockchain_hash }}</p>
    </v-card>

    <!-- Vitals History -->
    <v-card v-if="selectedPatient" class="rounded-xl elevation-1 mt-6" border="0">
      <v-card-title class="py-4 px-6 text-subtitle-1 font-weight-bold">Vitals History</v-card-title>
      <v-data-table
        :headers="headers"
        :items="vitalsHistory"
        :loading="loadingHistory"
        density="comfortable"
        class="px-2 pb-4"
      >
        <template #item.ai_status="{ item }">
          <v-chip
            :color="statusColor(item.ai_status)"
            variant="flat"
            size="small"
            class="font-weight-medium text-white"
          >
            {{ item.ai_status }}
          </v-chip>
        </template>
        <template #item.created_at="{ item }">
          <span class="text-caption text-no-wrap">
            {{ new Date(item.created_at).toLocaleDateString('en-GB') }}
          </span>
        </template>
      </v-data-table>
    </v-card>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { api } from '@/services/api'

const patients = ref([])
const selectedPatient = ref(null)
const submitting = ref(false)
const loadingHistory = ref(false)
const aiResult = ref(null)
const vitalsHistory = ref([])
let refreshInterval = null
const snackbar = ref({ show: false, message: '', color: 'success' })

const form = ref({
  heart_rate: null,
  systolic_bp: null,
  diastolic_bp: null,
  spo2: null,
  temperature: null,
  respiratory_rate: null,
})

const headers = [
  { title: 'Time', key: 'created_at', width: '110px' },
  { title: 'HR (BPM)', key: 'heart_rate', width: '90px' },
  { title: 'BP', key: 'systolic_bp', width: '70px' },
  { title: 'SpO2 (%)', key: 'spo2', width: '80px' },
  { title: 'Temp (°C)', key: 'temperature', width: '90px' },
  { title: 'RR', key: 'respiratory_rate', width: '70px' },
  { title: 'Status', key: 'ai_status', width: '100px' },
]

const statusColor = (status) => {
  if (status === 'critical') return 'red-darken-2'
  if (status === 'warning') return 'orange-darken-2'
  return 'teal-darken-2'
}

// Auto-send alert to all active staff when status is warning or critical
const sendAlert = async (result) => {
  if (!['warning', 'critical'].includes(result.ai_status)) return
  try {
    await api.post('/alerts/', {
      message: `Patient ${selectedPatient.value.firstName} ${selectedPatient.value.lastName} has a ${result.ai_status.toUpperCase()} vitals reading. Immediate attention required.`,
      ai_status: result.ai_status,
      patient_id: selectedPatient.value.id,
    })
  } catch (err) {
    console.error('Alert failed:', err)
  }
}

const fetchPatients = async () => {
  try {
    patients.value = await api.get('/patients/')
  } catch (err) {
    showSnackbar(err.message, 'error')
  }
}

const fetchVitalsHistory = async () => {
  if (!selectedPatient.value) return
  loadingHistory.value = true
  try {
    vitalsHistory.value = await api.get(`/vitals/${selectedPatient.value.id}`)
  } catch (err) {
    showSnackbar(err.message, 'error')
  } finally {
    loadingHistory.value = false
  }
}

const submitVitals = async () => {
  submitting.value = true
  aiResult.value = null
  try {
    const result = await api.post('/vitals/', {
      ...form.value,
      patient_id: selectedPatient.value.id,
    })
    aiResult.value = result

    // Auto-alert on warning or critical
    await sendAlert(result)

    showSnackbar(
      `AI Analysis: ${result.ai_status?.toUpperCase()}`,
      result.ai_status === 'critical' ? 'error' : 'success',
    )
    await fetchVitalsHistory()
  } catch (err) {
    showSnackbar(err.message, 'error')
  } finally {
    submitting.value = false
  }
}

const showSnackbar = (message, color = 'success') => {
  snackbar.value = { show: true, message, color }
}

watch(selectedPatient, fetchVitalsHistory)

onMounted(() => {
  fetchPatients()
  refreshInterval = setInterval(fetchVitalsHistory, 30000)
})

onUnmounted(() => {
  clearInterval(refreshInterval)
})
</script>
