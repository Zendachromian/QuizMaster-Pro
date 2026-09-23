import { defineStore } from 'pinia'
import axios from '@/utils/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || sessionStorage.getItem('token'),
    loading: false,
    initialized: false
  }),

  getters: {
    isAuthenticated: (state) => !!state.token && !!state.user,
    isAdmin: (state) => state.user?.role === 'admin',
    userName: (state) => state.user?.username || state.user?.full_name
  },

  actions: {
    async initializeAuth () {
      // Don't init twice
      if (this.initialized) return

      let token = localStorage.getItem('token') || sessionStorage.getItem('token')
      if (token) {
        this.token = token
        axios.defaults.headers.common.Authorization = `Bearer ${token}`
        try {
          await this.fetchUser()
        } catch (error) {
          // Keep token but clear user - let them stay on page
          this.user = null
        }
      }
      this.initialized = true
    },

    async login (credentials) {
      try {
        this.loading = true
        const response = await axios.post('/auth/login', credentials)

        const { access_token, user } = response.data

        this.token = access_token
        this.user = user

        // Store token - remember me logic
        if (credentials.remember) {
          localStorage.setItem('token', access_token)
          sessionStorage.removeItem('token')
        } else {
          sessionStorage.setItem('token', access_token)
          localStorage.removeItem('token')
        }

        // Set auth header
        axios.defaults.headers.common.Authorization = `Bearer ${access_token}`

        return { success: true }
      } catch (error) {
        const message = error.response?.data?.message || 'Login failed'
        return { success: false, message }
      } finally {
        this.loading = false
      }
    },

    async register (userData) {
      try {
        this.loading = true
        const response = await axios.post('/auth/register', userData)

        return { success: true, message: response.data.message }
      } catch (error) {
        const message = error.response?.data?.message || 'Registration failed'
        return { success: false, message }
      } finally {
        this.loading = false
      }
    },

    async fetchUser () {
      try {
        const response = await axios.get('/auth/profile')
        this.user = response.data
      } catch (error) {
        console.error('Error fetching user:', error)
        throw error
      }
    },

    async updateProfile (userData) {
      try {
        const response = await axios.put('/auth/profile', userData)
        this.user = { ...this.user, ...response.data.user }
        return { success: true, message: 'Profile updated successfully' }
      } catch (error) {
        const message = error.response?.data?.message || 'Profile update failed'
        return { success: false, message }
      }
    },

    async logout (forceRedirect = true) {
      try {
        await axios.post('/auth/logout')
      } catch (error) {
        // Continue with local logout anyway
      }

      // Clear everything
      this.user = null
      this.token = null
      this.initialized = false

      localStorage.removeItem('token')
      sessionStorage.removeItem('token')
      delete axios.defaults.headers.common.Authorization

      // Redirect if needed
      if (forceRedirect && window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    },

    // Clear invalid tokens when needed
    clearInvalidToken () {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
      sessionStorage.removeItem('token')
      delete axios.defaults.headers.common.Authorization
    }
  }
})
