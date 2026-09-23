<template>
  <AppLayout>
    <div class="container py-4 no-hover-profile">
      <!-- Profile Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card border-0 shadow-sm no-hover-effect">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <div class="avatar-circle me-4">
                  <i class="bi bi-person-circle display-4 text-primary"></i>
                </div>
                <div>
                  <h2 class="mb-1">{{ user?.full_name || user?.username }}</h2>
                  <p class="text-muted mb-0">{{ user?.email }}</p>
                  <span class="badge bg-primary">{{ user?.role?.charAt(0).toUpperCase() + user?.role?.slice(1) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Profile Form -->
      <div class="row">
        <div class="col-md-8">
          <div class="card border-0 shadow-sm no-hover-effect">
            <div class="card-header bg-light">
              <h5 class="mb-0">
                <i class="bi bi-pencil-square me-2"></i>
                Edit Profile
              </h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="updateProfile">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="fullName" class="form-label">Full Name *</label>
                      <input
                        id="fullName"
                        v-model="form.full_name"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.full_name }"
                        placeholder="Enter your full name"
                        required
                      >
                      <div v-if="errors.full_name" class="invalid-feedback">
                        {{ errors.full_name }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="username" class="form-label">Username *</label>
                      <input
                        id="username"
                        v-model="form.username"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.username }"
                        placeholder="Enter your username"
                        required
                      >
                      <div v-if="errors.username" class="invalid-feedback">
                        {{ errors.username }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email Address *</label>
                  <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    class="form-control"
                    :class="{ 'is-invalid': errors.email }"
                    placeholder="Enter your email"
                    required
                  >
                  <div v-if="errors.email" class="invalid-feedback">
                    {{ errors.email }}
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="currentPassword" class="form-label">Current Password</label>
                      <input
                        id="currentPassword"
                        v-model="form.current_password"
                        type="password"
                        class="form-control"
                        :class="{ 'is-invalid': errors.current_password }"
                        placeholder="Enter current password to change"
                      >
                      <div v-if="errors.current_password" class="invalid-feedback">
                        {{ errors.current_password }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="newPassword" class="form-label">New Password</label>
                      <input
                        id="newPassword"
                        v-model="form.new_password"
                        type="password"
                        class="form-control"
                        :class="{ 'is-invalid': errors.new_password }"
                        placeholder="Enter new password"
                      >
                      <div v-if="errors.new_password" class="invalid-feedback">
                        {{ errors.new_password }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="d-flex justify-content-end gap-2">
                  <router-link to="/dashboard" class="btn btn-secondary">
                    Cancel
                  </router-link>
                  <button type="submit" class="btn btn-primary" :disabled="saving">
                    <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                    Update Profile
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>

        <div class="col-md-4">
                    <div class="card border-0 shadow-sm no-hover-effect">
            <div class="card-header bg-light">
              <h5 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>
                Account Information
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <small class="text-muted">Member Since</small>
                <div class="fw-semibold">{{ formatDate(user?.created_at) }}</div>
              </div>
              <div class="mb-3">
                <small class="text-muted">Account Status</small>
                <div>
                  <span :class="user?.is_active ? 'badge bg-success' : 'badge bg-danger'">
                    {{ user?.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Notification Preferences -->
          <div class="card border-0 shadow-sm no-hover-effect mt-3">
            <div class="card-header bg-light">
              <h5 class="mb-0">
                <i class="bi bi-bell me-2"></i>
                Notification Preferences
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <label class="form-label">Monthly Report Format</label>
                <div class="btn-group w-100" role="group">
                  <input
                    type="radio"
                    class="btn-check"
                    name="reportFormat"
                    id="htmlFormat"
                    value="html"
                    v-model="preferences.monthly_report_format"
                    @change="updatePreferences"
                  >
                  <label class="btn btn-outline-primary" for="htmlFormat">
                    <i class="bi bi-file-text me-1"></i>HTML Email
                  </label>

                  <input
                    type="radio"
                    class="btn-check"
                    name="reportFormat"
                    id="pdfFormat"
                    value="pdf"
                    v-model="preferences.monthly_report_format"
                    @change="updatePreferences"
                  >
                  <label class="btn btn-outline-primary" for="pdfFormat">
                    <i class="bi bi-file-pdf me-1"></i>PDF Attachment
                  </label>
                </div>
                <small class="form-text text-muted">
                  Choose how you'd like to receive your monthly quiz performance reports
                </small>
              </div>

              <div class="form-check mb-3">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="monthlyReportEnabled"
                  v-model="preferences.monthly_report_enabled"
                  @change="updatePreferences"
                >
                <label class="form-check-label" for="monthlyReportEnabled">
                  Enable monthly activity reports
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { toast } from '@/utils/toast'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Profile',
  components: { AppLayout },
  setup () {
    const authStore = useAuthStore()

    // Reactive data
    const saving = ref(false)
    const errors = ref({})

    // Form data
    const form = ref({
      full_name: '',
      username: '',
      email: '',
      current_password: '',
      new_password: ''
    })

    // Preferences data
    const preferences = ref({
      monthly_report_enabled: true,
      monthly_report_format: 'html'
    })

    // Computed
    const user = computed(() => authStore.user)

    // Methods
    const initializeForm = () => {
      if (user.value) {
        form.value = {
          full_name: user.value.full_name || '',
          username: user.value.username || '',
          email: user.value.email || '',
          current_password: '',
          new_password: ''
        }
      }
    }

    const updateProfile = async () => {
      try {
        saving.value = true
        errors.value = {}

        const result = await authStore.updateProfile(form.value)

        if (result.success) {
          toast.success(result.message)
          // Clear password fields
          form.value.current_password = ''
          form.value.new_password = ''
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('An error occurred while updating profile')
      } finally {
        saving.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const loadPreferences = async () => {
      try {
        const response = await fetch('/api/user/notification-preferences', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            preferences.value = {
              monthly_report_enabled: data.preferences.monthly_report_enabled,
              monthly_report_format: data.preferences.monthly_report_format || 'html'
            }
          }
        }
      } catch (error) {
        console.error('Failed to load preferences:', error)
      }
    }

    const updatePreferences = async () => {
      try {
        const response = await fetch('/api/user/notification-preferences', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          },
          body: JSON.stringify(preferences.value)
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            toast.success('Preferences updated successfully')
          }
        } else {
          toast.error('Failed to update preferences')
        }
      } catch (error) {
        toast.error('An error occurred while updating preferences')
      }
    }

    // Lifecycle
    onMounted(() => {
      initializeForm()
      loadPreferences()
    })

    return {
      // State
      saving,
      errors,
      form,
      preferences,

      // Computed
      user,

      // Methods
      updateProfile,
      updatePreferences,
      formatDate
    }
  }
}
</script>

<style scoped>
.avatar-circle {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bs-primary-bg);
  border-radius: 50%;
}

.badge {
  font-size: 0.75em;
}

/* Force all text to be black/dark colors */
.no-hover-profile,
.no-hover-profile * {
  color: #212529 !important;
}

/* Specific overrides for different text elements */
.no-hover-profile h1,
.no-hover-profile h2,
.no-hover-profile h3,
.no-hover-profile h4,
.no-hover-profile h5,
.no-hover-profile h6 {
  color: #212529 !important;
}

.no-hover-profile p,
.no-hover-profile div,
.no-hover-profile span:not(.badge) {
  color: #212529 !important;
}

.no-hover-profile .text-muted,
.no-hover-profile small {
  color: #495057 !important;
}

/* Override badge colors to ensure black text */
.no-hover-profile .badge.bg-primary,
.no-hover-profile .badge.bg-success,
.no-hover-profile .badge.bg-danger,
.no-hover-profile .badge.bg-warning,
.no-hover-profile .badge.bg-info {
  color: #212529 !important;
  background-color: #f8f9fa !important;
  border: 1px solid #dee2e6 !important;
}

/* Form labels and inputs */
.no-hover-profile .form-label,
.no-hover-profile .form-control,
.no-hover-profile .form-control::placeholder {
  color: #212529 !important;
}

/* Make form input fields light colored */
.no-hover-profile .form-control {
  background-color: #f8f9fa !important; /* Light gray background for inputs */
  border: 1px solid #dee2e6 !important;
  color: #212529 !important;
}

.no-hover-profile .form-control:focus {
  background-color: #ffffff !important; /* White background when focused */
  border-color: #007bff !important;
  color: #212529 !important;
}

/* Button text - make Cancel and Update Profile white */
.no-hover-profile .btn {
  color: #fff !important; /* White text for buttons */
}

.no-hover-profile .btn-secondary {
  color: #fff !important; /* White text for Cancel button */
  background-color: #6c757d !important; /* Ensure proper background */
}

.no-hover-profile .btn-primary {
  color: #fff !important; /* White text for Update Profile button */
  background-color: #007bff !important; /* Ensure proper background */
}

/* Completely disable all hover effects on this page */
.no-hover-profile .card,
.no-hover-profile .card:hover,
.card.no-hover-effect,
.card.no-hover-effect:hover {
  transform: none !important;
  transition: none !important;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1) !important;
  background-color: #ffffff !important; /* White background for cards */
}

/* Make card headers light */
.no-hover-profile .card-header,
.card.no-hover-effect .card-header {
  background-color: #f8f9fa !important; /* Light gray for headers */
  border-bottom: 1px solid #dee2e6 !important;
  color: #212529 !important; /* Dark text for headers */
}

/* Make card bodies white */
.no-hover-profile .card-body,
.card.no-hover-effect .card-body {
  background-color: #ffffff !important; /* White background for card bodies */
  color: #212529 !important; /* Dark text for content */
}

.no-hover-profile .card:hover .text-muted,
.card.no-hover-effect:hover .text-muted {
  color: #495057 !important;
}

.no-hover-profile .card:hover .small,
.card.no-hover-effect:hover .small {
  color: #495057 !important;
}

/* Override any global hover effects using deep selectors */
:deep(.no-hover-profile .card),
:deep(.no-hover-profile .card:hover),
:deep(.card.no-hover-effect),
:deep(.card.no-hover-effect:hover) {
  transform: none !important;
  transition: none !important;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1) !important;
  background-color: #ffffff !important; /* White background for cards */
}

/* Deep selectors for card headers and bodies */
:deep(.no-hover-profile .card-header),
:deep(.card.no-hover-effect .card-header) {
  background-color: #f8f9fa !important; /* Light gray for headers */
  border-bottom: 1px solid #dee2e6 !important;
  color: #212529 !important; /* Dark text for headers */
}

:deep(.no-hover-profile .card-body),
:deep(.card.no-hover-effect .card-body) {
  background-color: #ffffff !important; /* White background for card bodies */
  color: #212529 !important; /* Dark text for content */
}

:deep(.no-hover-profile .card:hover .text-muted),
:deep(.card.no-hover-effect:hover .text-muted) {
  color: #495057 !important;
}

:deep(.no-hover-profile .card:hover .small),
:deep(.card.no-hover-effect:hover .small) {
  color: #495057 !important;
}

/* Additional overrides for specific global selectors */
:deep(.btn:hover),
:deep(.card:hover),
:deep(.list-group-item:hover) {
  transition: none !important;
}

:deep(.no-hover-profile *:hover) {
  transform: none !important;
  transition: none !important;
}

/* Deep selectors to override global styles */
:deep(.no-hover-profile *) {
  color: #212529 !important;
}

:deep(.no-hover-profile .text-muted),
:deep(.no-hover-profile small) {
  color: #495057 !important;
}

:deep(.no-hover-profile .badge) {
  color: #212529 !important;
  background-color: #f8f9fa !important;
  border: 1px solid #dee2e6 !important;
}
</style>
