<template>
  <div class="register-page min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow no-hover-effect">
            <div class="card-body p-5">
              <!-- Header -->
              <div class="text-center mb-4">
                <router-link to="/" class="text-decoration-none">
                  <h2 class="text-primary fw-bold">
                    <i class="bi bi-mortarboard me-2"></i>QuizMaster Pro
                  </h2>
                </router-link>
                <p class="text-dark fw-semibold">Create your account and start learning!</p>
              </div>

              <!-- Alert for messages -->
              <div v-if="message" :class="`alert alert-${messageType} alert-dismissible fade show`" role="alert">
                {{ message }}
                <button type="button" class="btn-close" @click="message = ''" aria-label="Close"></button>
              </div>

              <!-- Registration Form -->
              <form @submit.prevent="handleRegister">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="fullName" class="form-label text-dark fw-semibold">Full Name *</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-person"></i>
                      </span>
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

                  <div class="col-md-6 mb-3">
                    <label for="username" class="form-label text-dark fw-semibold">Username *</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-at"></i>
                      </span>
                      <input
                        id="username"
                        v-model="form.username"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.username }"
                        placeholder="Choose a username"
                        required
                      >
                      <div v-if="errors.username" class="invalid-feedback">
                        {{ errors.username }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label text-dark fw-semibold">Email Address *</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input
                      id="email"
                      v-model="form.email"
                      type="email"
                      class="form-control"
                      :class="{ 'is-invalid': errors.email }"
                      placeholder="Enter your email address"
                      required
                    >
                    <div v-if="errors.email" class="invalid-feedback">
                      {{ errors.email }}
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="password" class="form-label text-dark fw-semibold">Password *</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-lock"></i>
                      </span>
                      <input
                        id="password"
                        v-model="form.password"
                        :type="showPassword ? 'text' : 'password'"
                        class="form-control"
                        :class="{ 'is-invalid': errors.password }"
                        placeholder="Create a password"
                        required
                      >
                      <button
                        class="btn btn-outline-secondary no-hover-effect"
                        type="button"
                        @click="showPassword = !showPassword"
                      >
                        <i :class="`bi bi-eye${showPassword ? '-slash' : ''}`"></i>
                      </button>
                      <div v-if="errors.password" class="invalid-feedback">
                        {{ errors.password }}
                      </div>
                    </div>
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="confirmPassword" class="form-label text-dark fw-semibold">Confirm Password *</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-lock-fill"></i>
                      </span>
                      <input
                        id="confirmPassword"
                        v-model="form.confirm_password"
                        :type="showConfirmPassword ? 'text' : 'password'"
                        class="form-control"
                        :class="{ 'is-invalid': errors.confirm_password }"
                        placeholder="Confirm your password"
                        required
                      >
                      <button
                        class="btn btn-outline-secondary no-hover-effect"
                        type="button"
                        @click="showConfirmPassword = !showConfirmPassword"
                      >
                        <i :class="`bi bi-eye${showConfirmPassword ? '-slash' : ''}`"></i>
                      </button>
                      <div v-if="errors.confirm_password" class="invalid-feedback">
                        {{ errors.confirm_password }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="qualification" class="form-label text-dark fw-semibold">Qualification</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-award"></i>
                      </span>
                      <select
                        id="qualification"
                        v-model="form.qualification"
                        class="form-select"
                      >
                        <option value="">Select your qualification</option>
                        <option value="kindergarten">Kindergarten</option>
                        <option value="elementary">Elementary</option>
                        <option value="middle school">Middle School</option>
                        <option value="secondary">Secondary</option>
                        <option value="higher secondary">Higher Secondary</option>
                        <option value="undergraduate">Undergraduate</option>
                        <option value="graduate">Graduate</option>
                        <option value="post graduate">Post Graduate</option>
                        <option value="masters">Masters</option>
                        <option value="phd">PhD</option>
                        <option value="post doc">Post Doc</option>
                      </select>
                    </div>
                  </div>

                  <div class="col-md-6 mb-3">
                    <label for="dateOfBirth" class="form-label text-dark fw-semibold">Date of Birth</label>
                    <div class="input-group">
                      <span class="input-group-text">
                        <i class="bi bi-calendar"></i>
                      </span>
                      <input
                        id="dateOfBirth"
                        v-model="form.date_of_birth"
                        type="date"
                        class="form-control"
                      >
                    </div>
                  </div>
                </div>

                <div class="mb-3 form-check">
                  <input
                    id="terms"
                    v-model="form.acceptTerms"
                    type="checkbox"
                    class="form-check-input"
                    :class="{ 'is-invalid': errors.acceptTerms }"
                    required
                  >
                  <label class="form-check-label text-dark fw-semibold" for="terms">
                    I agree to the <a href="#" class="text-decoration-none fw-bold">Terms of Service</a>
                    and <a href="#" class="text-decoration-none fw-bold">Privacy Policy</a>
                  </label>
                  <div v-if="errors.acceptTerms" class="invalid-feedback">
                    {{ errors.acceptTerms }}
                  </div>
                </div>

                <div class="d-grid">
                  <button
                    type="submit"
                    class="btn btn-primary btn-lg no-hover-effect"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ loading ? 'Creating Account...' : 'Create Account' }}
                  </button>
                </div>
              </form>

              <!-- Footer Links -->
              <div class="text-center mt-4">
                <p class="mb-0 text-dark">
                  Already have an account?
                  <router-link to="/login" class="text-decoration-none fw-semibold">
                    Sign in here
                  </router-link>
                </p>
              </div>
            </div>
          </div>

          <!-- Back to Home -->
          <div class="text-center mt-3">
            <router-link to="/" class="text-dark text-decoration-none fw-semibold">
              <i class="bi bi-arrow-left me-1"></i>Back to Home
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { validateEmail, validatePassword } from '@/utils/helpers'

export default {
  name: 'Register',
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()

    const form = reactive({
      full_name: '',
      username: '',
      email: '',
      password: '',
      confirm_password: '',
      qualification: '',
      date_of_birth: '',
      acceptTerms: false
    })

    const errors = reactive({
      full_name: '',
      username: '',
      email: '',
      password: '',
      confirm_password: '',
      acceptTerms: ''
    })

    const message = ref('')
    const messageType = ref('danger')
    const showPassword = ref(false)
    const showConfirmPassword = ref(false)

    const loading = computed(() => authStore.loading)

    const validateForm = () => {
      let isValid = true

      // Reset errors
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })

      // Validate full name
      if (!form.full_name.trim()) {
        errors.full_name = 'Full name is required'
        isValid = false
      } else if (form.full_name.trim().length < 2) {
        errors.full_name = 'Full name must be at least 2 characters'
        isValid = false
      }

      // Validate username
      if (!form.username.trim()) {
        errors.username = 'Username is required'
        isValid = false
      } else if (form.username.trim().length < 3) {
        errors.username = 'Username must be at least 3 characters'
        isValid = false
      } else if (!/^[a-zA-Z0-9_]+$/.test(form.username.trim())) {
        errors.username = 'Username can only contain letters, numbers, and underscores'
        isValid = false
      }

      // Validate email
      if (!form.email.trim()) {
        errors.email = 'Email is required'
        isValid = false
      } else if (!validateEmail(form.email.trim())) {
        errors.email = 'Please enter a valid email address'
        isValid = false
      }

      // Validate password
      if (!form.password) {
        errors.password = 'Password is required'
        isValid = false
      } else if (!validatePassword(form.password)) {
        errors.password = 'Password must be at least 6 characters'
        isValid = false
      }

      // Validate confirm password
      if (!form.confirm_password) {
        errors.confirm_password = 'Please confirm your password'
        isValid = false
      } else if (form.password !== form.confirm_password) {
        errors.confirm_password = 'Passwords do not match'
        isValid = false
      }

      // Validate terms acceptance
      if (!form.acceptTerms) {
        errors.acceptTerms = 'You must accept the terms and conditions'
        isValid = false
      }

      return isValid
    }

    const handleRegister = async () => {
      if (!validateForm()) {
        return
      }

      try {
        const result = await authStore.register({
          full_name: form.full_name.trim(),
          username: form.username.trim(),
          email: form.email.toLowerCase().trim(),
          password: form.password,
          confirm_password: form.confirm_password,
          qualification: form.qualification.trim() || null,
          date_of_birth: form.date_of_birth || null
        })

        if (result.success) {
          message.value = result.message || 'Registration successful! You can now log in.'
          messageType.value = 'success'

          // Reset form
          Object.keys(form).forEach(key => {
            if (typeof form[key] === 'boolean') {
              form[key] = false
            } else {
              form[key] = ''
            }
          })

          // Redirect to login after 2 seconds
          setTimeout(() => {
            router.push('/login')
          }, 2000)
        } else {
          message.value = result.message || 'Registration failed. Please try again.'
          messageType.value = 'danger'
        }
      } catch (error) {
        message.value = 'An error occurred. Please try again.'
        messageType.value = 'danger'
        console.error('Registration error:', error)
      }
    }

    return {
      form,
      errors,
      message,
      messageType,
      showPassword,
      showConfirmPassword,
      loading,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-page {
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
}

.card {
  border: none;
  border-radius: 15px;
  background: #ffffff;
}

.input-group .form-control:focus {
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
  border-color: #0d6efd;
}

.input-group-text {
  background: #e9ecef;
  border-right: none;
  color: #495057;
  font-weight: 500;
}

.form-control {
  border-left: none;
  border-color: #ced4da;
  color: #212529;
  font-weight: 500;
  background-color: #ffffff !important; /* Force white background */
}

.form-control::placeholder {
  color: #6c757d;
  opacity: 0.8;
}

.form-control:focus {
  border-left: none;
  color: #212529;
  background-color: #ffffff !important; /* Force white background on focus */
}

.form-select {
  border-left: none;
  border-color: #ced4da;
  color: #212529;
  font-weight: 500;
  background-color: #ffffff !important; /* Force white background for select */
}

.form-select:focus {
  border-left: none;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
  border-color: #0d6efd;
  color: #212529;
  background-color: #ffffff !important; /* Force white background on focus */
}

.form-label {
  color: #212529;
  font-weight: 600;
}

.form-check-label {
  color: #212529;
}

.form-check-label a {
  color: #0d6efd;
}

.btn-primary {
  border-radius: 8px;
  font-weight: 600;
  background: #0d6efd;
  border-color: #0d6efd;
}

.btn-outline-secondary {
  border-color: #6c757d;
  color: #6c757d;
  font-weight: 500;
}

.text-primary {
  color: #0d6efd !important;
}

.alert {
  border-radius: 8px;
  font-weight: 500;
}

@media (max-width: 576px) {
  .card-body {
    padding: 2rem !important;
  }
}
</style>
