<template>
  <div class="login-page min-vh-100 d-flex align-items-center bg-light">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow no-hover-effect">
            <div class="card-body p-5">
              <!-- Header -->
              <div class="text-center mb-4">
                <router-link to="/" class="text-decoration-none">
                  <h2 class="text-primary fw-bold">
                    <i class="bi bi-mortarboard me-2"></i>QuizMaster Pro
                  </h2>
                </router-link>
                <p class="text-dark fw-semibold">Welcome back! Please sign in to your account.</p>
              </div>

              <!-- Alert for messages -->
              <div v-if="message" :class="`alert alert-${messageType} alert-dismissible fade show`" role="alert">
                {{ message }}
                <button type="button" class="btn-close" @click="message = ''" aria-label="Close"></button>
              </div>

              <!-- Login Form -->
              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="email" class="form-label text-dark fw-semibold">Email Address</label>
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
                      placeholder="Enter your email"
                      required
                    >
                    <div v-if="errors.email" class="invalid-feedback">
                      {{ errors.email }}
                    </div>
                  </div>
                </div>

                <div class="mb-4">
                  <label for="password" class="form-label text-dark fw-semibold">Password</label>
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
                      placeholder="Enter your password"
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

                <div class="d-grid">
                  <button
                    type="submit"
                    class="btn btn-primary btn-lg no-hover-effect"
                    :disabled="loading"
                  >
                    <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    {{ loading ? 'Signing In...' : 'Sign In' }}
                  </button>
                </div>
              </form>

              <!-- Footer Links -->
              <div class="text-center mt-4">
                <p class="mb-0 text-dark">
                  Don't have an account?
                  <router-link to="/register" class="text-decoration-none fw-semibold">
                    Sign up here
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
import { validateEmail } from '@/utils/helpers'

export default {
  name: 'Login',
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()

    const form = reactive({
      email: '',
      password: ''
    })

    const errors = reactive({
      email: '',
      password: ''
    })

    const message = ref('')
    const messageType = ref('danger')
    const showPassword = ref(false)

    const loading = computed(() => authStore.loading)

    const validateForm = () => {
      let isValid = true

      // Reset errors
      errors.email = ''
      errors.password = ''

      // Validate email
      if (!form.email) {
        errors.email = 'Email is required'
        isValid = false
      } else if (!validateEmail(form.email)) {
        errors.email = 'Please enter a valid email address'
        isValid = false
      }

      // Validate password
      if (!form.password) {
        errors.password = 'Password is required'
        isValid = false
      } else if (form.password.length < 6) {
        errors.password = 'Password must be at least 6 characters'
        isValid = false
      }

      return isValid
    }

    const handleLogin = async () => {
      if (!validateForm()) {
        return
      }

      try {
        const result = await authStore.login({
          email: form.email.toLowerCase().trim(),
          password: form.password
        })

        if (result.success) {
          message.value = 'Login successful! Redirecting...'
          messageType.value = 'success'

          // Redirect based on user role
          setTimeout(() => {
            if (authStore.isAdmin) {
              router.push('/admin')
            } else {
              router.push('/dashboard')
            }
          }, 1000)
        } else {
          message.value = result.message || 'Login failed. Please try again.'
          messageType.value = 'danger'
        }
      } catch (error) {
        message.value = 'An error occurred. Please try again.'
        messageType.value = 'danger'
        console.error('Login error:', error)
      }
    }

    return {
      form,
      errors,
      message,
      messageType,
      showPassword,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-page {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
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

.form-label {
  color: #212529;
  font-weight: 600;
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
