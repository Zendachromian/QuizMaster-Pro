<template>
  <div id="app">
    <div v-if="loading" class="d-flex justify-content-center align-items-center" style="height: 100vh;">
      <div class="text-center">
        <div class="loading-spinner mb-3"></div>
        <p>Loading QuizMaster Pro...</p>
      </div>
    </div>
    <div v-else>
      <router-view />
    </div>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup () {
    const loading = ref(true)
    const authStore = useAuthStore()

    onMounted(async () => {
      try {
        // Initialize authentication state
        await authStore.initializeAuth()
      } catch (error) {
        console.error('Error initializing app:', error)
      } finally {
        loading.value = false
      }
    })

    return {
      loading
    }
  }
}
</script>

<style>
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
