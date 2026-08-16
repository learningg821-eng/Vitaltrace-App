<template>
  <v-container fluid class="pa-0">
    <div class="d-flex justify-end mb-6">
      <v-btn
        v-if="authStore.isAdmin"
        color="teal-darken-2"
        prepend-icon="mdi-account-plus"
        class="text-capitalize elevation-0"
        @click="openAddDialog"
      >
        Add New Staff
      </v-btn>
    </div>

    <v-alert v-if="error" type="error" class="mb-4" closable>{{ error }}</v-alert>

    <v-card class="rounded-xl elevation-1" border="0">
      <v-card-title class="d-flex align-center justify-space-between py-4 px-6">
        <span class="text-subtitle-1 font-weight-bold">Hospital Personnel Directory</span>
        <v-text-field
          v-model="search"
          prepend-inner-icon="mdi-magnify"
          placeholder="Search staff..."
          density="compact"
          variant="outlined"
          hide-details
          class="bg-grey-lighten-4 rounded-lg"
          style="max-width: 250px"
        />
      </v-card-title>

      <v-data-table
        :headers="headers"
        :items="staffList"
        :search="search"
        :loading="loading"
        density="comfortable"
        class="px-2 pb-4"
        :header-props="{ class: 'font-weight-bold' }"
      >
        <template #item.staffId="{ item }">
          <span class="font-weight-medium text-teal-darken-2">{{ item.staffId }}</span>
        </template>

        <template #item.name="{ item }">
          <div class="d-flex align-center py-2">
            <span class="font-weight-medium text-grey-darken-3">
              {{ item.firstName }} {{ item.lastName }}
            </span>
          </div>
        </template>

        <template #item.role="{ item }">
          <v-chip size="small" color="teal-darken-1" variant="tonal" class="font-weight-medium">
            {{ item.role }}
          </v-chip>
        </template>

        <template #item.status="{ item }">
          <v-chip
            size="small"
            :color="item.status === 'Active' ? 'success' : 'grey-darken-1'"
            variant="flat"
            class="font-weight-medium"
          >
            {{ item.status }}
          </v-chip>
        </template>

        <template #item.actions="{ item }">
          <div class="d-flex align-center">
            <v-btn
              v-if="authStore.isAdmin"
              color="teal-darken-2"
              variant="text"
              size="small"
              @click="openEditDialog(item)"
            >
              <v-icon>mdi-pencil-outline</v-icon>
              Edit
            </v-btn>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!-- Add / Edit Dialog -->
    <v-dialog v-model="dialog" max-width="600px">
      <v-card class="rounded-xl pa-2">
        <v-card-title class="px-4 pt-4 d-flex justify-space-between align-center">
          <span class="text-h6 font-weight-bold text-grey-darken-3">
            {{ isEditing ? 'Edit Staff Details' : 'Add New Staff Member' }}
          </span>
          <v-btn icon="mdi-close" variant="text" size="small" @click="closeDialog" />
        </v-card-title>

        <v-card-text class="px-4 py-2">
          <v-form ref="formRef" v-model="isFormValid">
            <v-row>
              <!-- Staff Info -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="staffForm.firstName"
                  label="First Name *"
                  variant="outlined"
                  density="compact"
                  :rules="[requiredRule]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="staffForm.lastName"
                  label="Last Name *"
                  variant="outlined"
                  density="compact"
                  :rules="[requiredRule]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="staffForm.department"
                  :items="departmentOptions"
                  label="Department *"
                  variant="outlined"
                  density="compact"
                  :rules="[requiredRule]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="staffForm.shift"
                  :items="shiftOptions"
                  label="Shift Assignment"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="staffForm.phone"
                  label="Phone Number"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="staffForm.status"
                  :items="statusOptions"
                  label="Status"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <v-divider class="my-2 w-100" />

              <!-- Account Info -->
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="staffForm.username"
                  label="Username *"
                  prepend-inner-icon="mdi-account-outline"
                  variant="outlined"
                  density="compact"
                  :rules="[requiredRule]"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="staffForm.password"
                  label="Password *"
                  prepend-inner-icon="mdi-lock-outline"
                  type="password"
                  variant="outlined"
                  density="compact"
                  :rules="isEditing ? [] : [requiredRule]"
                  :placeholder="isEditing ? 'Leave blank to keep current' : ''"
                />
              </v-col>

              <v-col cols="12" sm="6">
                <v-select
                  v-model="staffForm.role_id"
                  :items="roleOptions"
                  item-title="name"
                  item-value="id"
                  label="Role *"
                  prepend-inner-icon="mdi-shield-account-outline"
                  variant="outlined"
                  density="compact"
                  :rules="[requiredRule]"
                />
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>

        <v-card-actions class="px-4 pb-4 justify-end gap-2">
          <v-btn
            variant="outlined"
            color="grey-darken-1"
            class="text-capitalize"
            @click="closeDialog"
          >
            Cancel
          </v-btn>
          <v-btn
            color="teal-darken-2"
            variant="flat"
            class="text-capitalize px-6"
            :loading="saving"
            :disabled="!isFormValid"
            @click="saveStaff"
          >
            {{ isEditing ? 'Update Changes' : 'Save Staff' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useStaff } from '@/composables/useStaff'
import { api } from '@/services/api'

const authStore = useAuthStore()
const { staffList, loading, saving, error, fetchStaff, createStaff, updateStaff } = useStaff()

const search = ref('')
const dialog = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const isFormValid = ref(false)
const roleOptions = ref([])

const departmentOptions = [
  'ICU / Monitoring',
  'General Ward',
  'Cardiology',
  'Pediatrics',
  'Emergency',
]
const shiftOptions = [
  'Morning Shift (07:00 - 15:00)',
  'Evening Shift (15:00 - 23:00)',
  'Night Shift (23:00 - 07:00)',
]
const statusOptions = ['Active', 'On Leave', 'Inactive']

const headers = computed(() => {
  const base = [
    { title: 'Staff ID', key: 'staffId' },
    { title: 'Staff Member', key: 'name' },
    { title: 'Department', key: 'department' },
    { title: 'Shift', key: 'shift' },
    { title: 'Role', key: 'role' },
    { title: 'Status', key: 'status' },
  ]

  if (authStore.isAdmin) {
    base.push({ title: 'Actions', key: 'actions', sortable: false })
  }

  return base
})

const defaultStaff = {
  firstName: '',
  lastName: '',
  department: 'General Ward',
  shift: 'Morning Shift (07:00 - 15:00)',
  phone: '',
  status: 'Active',
  username: '',
  password: '',
  role_id: null,
}

const staffForm = ref({ ...defaultStaff })

const requiredRule = (v) => !!v || 'This field is required'
const getInitials = (first, last) => `${first?.[0] ?? ''}${last?.[0] ?? ''}`.toUpperCase()

const fetchRoles = async () => {
  try {
    roleOptions.value = await api.get('/roles/')
  } catch {
    roleOptions.value = []
  }
}

const openAddDialog = () => {
  isEditing.value = false
  editingId.value = null
  staffForm.value = { ...defaultStaff }
  dialog.value = true
}

const openEditDialog = (item) => {
  isEditing.value = true
  editingId.value = item.id
  staffForm.value = {
    firstName: item.firstName,
    lastName: item.lastName,
    department: item.department,
    shift: item.shift,
    phone: item.phone,
    status: item.status,
    username: item.username,
    password: '',
    role_id: item.role_id,
  }
  dialog.value = true
}

const saveStaff = async () => {
  const { valid } = await formRef.value.validate()
  if (!valid) return

  if (isEditing.value) {
    await updateStaff(editingId.value, staffForm.value)
  } else {
    await createStaff(staffForm.value)
  }

  closeDialog()
}

const closeDialog = () => {
  dialog.value = false
  setTimeout(() => {
    isEditing.value = false
    editingId.value = null
    staffForm.value = { ...defaultStaff }
    formRef.value?.resetValidation()
  }, 300)
}

onMounted(async () => {
  await fetchStaff()
  if (authStore.isAdmin) {
    await fetchRoles()
  }
})
</script>
