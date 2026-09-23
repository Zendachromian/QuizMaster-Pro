import axios from 'axios'

// Create axios instance
const instance = axios.create({
  baseURL: '/api', // Always use proxy path for both dev and production
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // Important for CORS with credentials
})

// Request interceptor
instance.interceptors.request.use(
  (config) => {
    // Add auth token to headers if available
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
instance.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Token expired or invalid - but don't auto-redirect
      // Let the components handle authentication state
      console.error('Authentication failed:', error.response.data?.message || error.response.data?.error)
    } else if (error.response?.status === 403) {
      // Forbidden
      console.error('Access denied:', error.response.data?.message || error.response.data?.error)
    } else if (error.response?.status === 500) {
      // Server error
      console.error('Server error:', error.response.data?.message || error.response.data?.error)
    }

    return Promise.reject(error)
  }
)

export default instance
