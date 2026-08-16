<template>
  <v-container fluid class="pa-0">
    <!-- Top Action Bar -->
    <div class="d-flex justify-end mt-5 mb-3">
      <v-btn
        v-if="authStore.isAdmin"
        color="teal-darken-2"
        prepend-icon="mdi-account-plus"
        class="text-capitalize elevation-0"
        @click="openDialog()"
      >
        Add New Patient
      </v-btn>
    </div>

    <!-- Table -->
    <v-card class="rounded-xl elevation-1" border="0">
      <v-card-title class="py-4 px-6">
        <span class="text-subtitle-1 font-weight-bold">Patient Registry</span>
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="patients"
        :loading="loading"
        density="comfortable"
        class="px-2 pb-4"
      >
        <template v-slot:item.fullName="{ item }">
          {{ item.firstName }} {{ item.lastName }}
        </template>

        <template v-slot:item.patientId="{ item }">
          <span class="text-teal-darken-2 font-weight-bold">{{ item.patientId }}</span>
        </template>

        <template v-slot:item.status="{ item }">
          <v-chip
            size="small"
            :color="item.status === 'Active' ? 'success' : 'grey-darken-1'"
            variant="flat"
            class="font-weight-medium"
          >
            {{ item.status }}
          </v-chip>
        </template>

        <template v-slot:item.actions="{ item }">
          <v-btn
            v-if="authStore.isAdmin"
            size="x-small"
            variant="outlined"
            color="teal-darken-2"
            class="text-capitalize"
            @click="openDialog(item)"
          >
            Edit
          </v-btn>
        </template>
      </v-data-table>
    </v-card>

    <!-- Add/Edit Dialog -->
    <v-dialog v-model="dialog" max-width="600" persistent>
      <v-card class="rounded-xl pa-4">
        <v-card-title class="text-subtitle-1 font-weight-bold mb-4">
          {{ editMode ? 'Edit Patient' : 'Add New Patient' }}
        </v-card-title>

        <v-card-text>
          <v-row dense>
            <v-col cols="6">
              <v-text-field
                v-model="form.firstName"
                label="First Name"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.lastName"
                label="Last Name"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.dob"
                label="Date of Birth"
                variant="outlined"
                density="compact"
                placeholder="MM/DD/YYYY"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="form.gender"
                :items="['Male', 'Female', 'Other']"
                label="Gender"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.admissionDate"
                label="Admission Date"
                variant="outlined"
                density="compact"
                placeholder="MM/DD/YYYY"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="form.department"
                :items="departments"
                label="Department"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="12">
              <v-text-field
                v-model="form.diagnosis"
                label="Primary Diagnosis"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-text-field
                v-model="form.doctor"
                label="Attending Doctor"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="form.patientType"
                :items="['inpatient', 'outpatient']"
                label="Patient Type"
                variant="outlined"
                density="compact"
              />
            </v-col>
            <v-col cols="6">
              <v-select
                v-model="form.status"
                :items="['Active', 'Discharged']"
                label="Status"
                variant="outlined"
                density="compact"
              />
            </v-col>
          </v-row>
        </v-card-text>

        <v-card-actions class="justify-end gap-2">
          <v-btn variant="text" @click="dialog = false">Cancel</v-btn>
          <v-btn color="teal-darken-2" variant="flat" :loading="saving" @click="savePatient">
            {{ editMode ? 'Update' : 'Create' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
    </v-snackbar>
  </v-container>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { api } from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const loading = ref(false)
const saving = ref(false)
const dialog = ref(false)
const editMode = ref(false)
const patients = ref([])
const editingId = ref(null)
const snackbar = ref({ show: false, message: '', color: 'success' })

const departments = ['ICU', 'Cardiology', 'General Ward', 'Pediatrics']

const headers = [
  { title: 'Patient ID', key: 'patientId' },
  { title: 'Full Name', key: 'fullName', sortable: false },
  { title: 'DOB', key: 'dob' },
  { title: 'Gender', key: 'gender' },
  { title: 'Admission Date', key: 'admissionDate' },
  { title: 'Diagnosis', key: 'diagnosis' },
  { title: 'Doctor', key: 'doctor' },
  { title: 'Department', key: 'department' },
  { title: 'Status', key: 'status' },
  { title: 'Actions', key: 'actions', sortable: false },
]

const defaultForm = () => ({
  firstName: '',
  lastName: '',
  dob: '',
  gender: '',
  admissionDate: '',
  diagnosis: '',
  doctor: '',
  department: '',
  patientType: 'inpatient',
  status: 'Active',
})

const form = ref(defaultForm())

const fetchPatients = async () => {
  loading.value = true
  try {
    patients.value = await api.get('/patients/')
  } catch (err) {
    showSnackbar(err.message, 'error')
  } finally {
    loading.value = false
  }
}

const openDialog = (patient = null) => {
  if (patient) {
    editMode.value = true
    editingId.value = patient.patientId
    form.value = {
      firstName: patient.firstName,
      lastName: patient.lastName,
      dob: patient.dob,
      gender: patient.gender,
      admissionDate: patient.admissionDate,
      diagnosis: patient.diagnosis,
      doctor: patient.doctor,
      department: patient.department,
      patientType: patient.patientType,
      status: patient.status,
    }
  } else {
    editMode.value = false
    editingId.value = null
    form.value = defaultForm()
  }
  dialog.value = true
}

const savePatient = async () => {
  saving.value = true
  try {
    if (editMode.value) {
      await api.put(`/patients/${editingId.value}`, form.value)
      showSnackbar('Patient updated successfully')
    } else {
      await api.post('/patients/', form.value)
      showSnackbar('Patient created successfully')
    }
    dialog.value = false
    await fetchPatients()
  } catch (err) {
    showSnackbar(err.message, 'error')
  } finally {
    saving.value = false
  }
}

const showSnackbar = (message, color = 'success') => {
  snackbar.value = { show: true, message, color }
}

onMounted(fetchPatients)
</script>
