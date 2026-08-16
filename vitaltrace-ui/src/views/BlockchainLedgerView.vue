<template>
  <v-container fluid class="pa-0">
    <v-card class="rounded-xl elevation-1" border="0">
      <v-card-title class="py-4 px-6 d-flex align-center ga-2">
        <v-icon color="teal-darken-2">mdi-cube-outline</v-icon>
        <span class="text-subtitle-1 font-weight-bold">Blockchain Ledger</span>
        <v-spacer />
        <v-chip color="teal-darken-2" variant="tonal" size="small">
          {{ ledger.length }} Blocks
        </v-chip>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="ledger"
        :loading="loading"
        density="comfortable"
        class="px-2 pb-4"
      >
        <!-- Block -->
        <template #item.block="{ item }">
          <v-chip color="teal-darken-2" variant="tonal" size="small" class="font-weight-bold">
            #{{ item.block }}
          </v-chip>
        </template>

        <!-- TX Hash -->
        <template #item.tx_hash="{ item }">
          <span class="text-caption text-mono text-grey-darken-2">
            {{ item.tx_hash?.slice(0, 16) }}...
          </span>
        </template>

        <!-- Block Number -->
        <template #item.block_number="{ item }">
          <v-chip color="blue-darken-2" variant="tonal" size="small">
            {{ item.block_number }}
          </v-chip>
        </template>

        <!-- AI Status -->
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

        <!-- Hash -->
        <template #item.blockchain_hash="{ item }">
          <span class="text-caption text-mono text-grey-darken-2">
            {{ item.blockchain_hash?.slice(0, 20) }}...
          </span>
        </template>

        <!-- Previous Hash -->
        <template #item.previous_hash="{ item }">
          <span class="text-caption text-mono text-grey">
            {{ item.previous_hash?.slice(0, 20) }}...
          </span>
        </template>

        <!-- Time -->
        <!-- Time -->
        <template #item.created_at="{ item }">
          <span class="text-caption text-grey-darken-2 text-no-wrap">
            {{ new Date(item.created_at).toLocaleDateString('en-GB') }}
          </span>
        </template>

        <!-- Expand for full hash -->
        <template #expanded-row="{ item }">
          <tr>
            <td :colspan="headers.length" class="pa-4 bg-grey-lighten-4">
              <p class="text-caption font-weight-bold mb-1">Full Hash:</p>
              <p class="text-caption text-mono">{{ item.blockchain_hash }}</p>
              <p class="text-caption font-weight-bold mt-2 mb-1">Previous Hash:</p>
              <p class="text-caption text-mono">{{ item.previous_hash }}</p>
              <p class="text-caption font-weight-bold mt-2 mb-1">AI Notes:</p>
              <p class="text-caption">{{ item.ai_notes }}</p>
            </td>
          </tr>
        </template>
      </v-data-table>
    </v-card>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'

const loading = ref(false)
const ledger = ref([])

const headers = [
  { title: 'Block', key: 'block', width: '80px' },
  { title: 'Patient', key: 'patient_name', width: '130px' },
  { title: 'HR', key: 'heart_rate', width: '60px' },
  { title: 'BP', key: 'systolic_bp', width: '60px' },
  { title: 'SpO2', key: 'spo2', width: '60px' },
  { title: 'Temp', key: 'temperature', width: '70px' },
  { title: 'Status', key: 'ai_status', width: '100px' },
  { title: 'Hash', key: 'blockchain_hash', width: '160px' },
  { title: 'Prev Hash', key: 'previous_hash', width: '160px' },
  { title: 'TX Hash', key: 'tx_hash', width: '140px' },
  { title: 'Time', key: 'created_at', width: '200px' },
]

const statusColor = (status) => {
  if (status === 'critical') return 'red-darken-2'
  if (status === 'warning') return 'orange-darken-2'
  return 'teal-darken-2'
}

const fetchLedger = async () => {
  loading.value = true
  try {
    ledger.value = (await api.get('/ledger/')).reverse()
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchLedger)
</script>
