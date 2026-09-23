import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from './stores/auth'

// Import Bootstrap CSS and JS
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Import global styles
import './assets/css/global.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Initialize authentication
const authStore = useAuthStore()
authStore.initializeAuth().then(() => {
  app.mount('#app')
}).catch(() => {
  // Even if auth initialization fails, still mount the app
  app.mount('#app')
})
