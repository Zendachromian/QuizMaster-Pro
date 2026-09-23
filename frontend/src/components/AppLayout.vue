<template>
  <div>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">
          <i class="bi bi-mortarboard me-2"></i>QuizMaster Pro
        </router-link>

        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#navbarNav"
          aria-controls="navbarNav"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <template v-if="isAuthenticated || hasToken">
              <template v-if="isAdmin || (hasToken && !authStore.user)">
                <li class="nav-item">
                  <router-link class="nav-link" to="/admin">
                    <i class="bi bi-speedometer2 me-1"></i>Dashboard
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/admin/subjects">
                    <i class="bi bi-book me-1"></i>Subjects
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/admin/users">
                    <i class="bi bi-people me-1"></i>Users
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/admin/quizzes">
                    <i class="bi bi-list-check me-1"></i>Quizzes
                  </router-link>
                </li>
              </template>
              <template v-else>
                <li class="nav-item">
                  <router-link class="nav-link" to="/dashboard">
                    <i class="bi bi-house me-1"></i>Dashboard
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/subjects">
                    <i class="bi bi-book me-1"></i>Subjects
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/quiz">
                    <i class="bi bi-puzzle me-1"></i>Quizzes
                  </router-link>
                </li>
                <li class="nav-item">
                  <router-link class="nav-link" to="/analytics">
                    <i class="bi bi-graph-up me-1"></i>Analytics
                  </router-link>
                </li>
              </template>
            </template>
          </ul>

          <ul class="navbar-nav">
            <template v-if="isAuthenticated || hasToken">
              <li class="nav-item dropdown">
                <a class="nav-link" href="#" @click.prevent="dropdownOpen = !dropdownOpen">
                  <i class="bi bi-person-circle me-1"></i>{{ userName || 'Loading...' }}
                </a>
                <ul class="dropdown-menu dropdown-menu-end" :class="{ show: dropdownOpen }">
                  <li>
                    <router-link class="dropdown-item" to="/profile">
                      <i class="bi bi-person me-2"></i>Profile
                    </router-link>
                  </li>
                  <li><hr class="dropdown-divider"></li>
                  <li>
                    <a class="dropdown-item" href="#" @click.prevent="handleLogout">
                      <i class="bi bi-box-arrow-right me-2"></i>Logout
                    </a>
                  </li>
                </ul>
              </li>
            </template>
            <template v-else>
              <li class="nav-item">
                <router-link class="nav-link" to="/login">
                  <i class="bi bi-box-arrow-in-right me-1"></i>Login
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/register">
                  <i class="bi bi-person-plus me-1"></i>Register
                </router-link>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Flash Messages -->
    <div class="container mt-3">
      <div
        v-for="(notification, index) in notifications"
        :key="index"
        :class="`alert alert-${notification.type} alert-dismissible fade show`"
        role="alert"
      >
        {{ notification.message }}
        <button
          type="button"
          class="btn-close"
          @click="removeNotification(index)"
          aria-label="Close"
        ></button>
      </div>
    </div>

    <!-- Main Content -->
    <main>
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-light mt-5 py-4">
      <div class="container">
        <div class="row">
          <div class="col-md-6">
            <h5 class="fw-bold">QuizMaster Pro</h5>
            <p class="text-muted mb-0">Your ultimate exam preparation platform</p>
          </div>
          <div class="col-md-6 text-md-end">
            <p class="text-muted mb-0">&copy; 2025 QuizMaster Pro. All rights reserved.</p>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

export default {
  name: 'AppLayout',
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const isAdmin = computed(() => authStore.isAdmin)
    const userName = computed(() => authStore.userName)
    const hasToken = computed(() => !!authStore.token)
    const notifications = computed(() => notificationStore.notifications)
    const dropdownOpen = ref(false)

    onMounted(() => {
      document.addEventListener('click', event => {
        if (!event.target.closest('.nav-item.dropdown')) dropdownOpen.value = false
      })
    })

    const handleLogout = async () => {
      await authStore.logout(true) // Explicitly redirect when user clicks logout
    }

    const removeNotification = (index) => {
      notificationStore.removeNotification(index)
    }

    return {
      isAuthenticated,
      isAdmin,
      userName,
      hasToken,
      authStore,
      notifications,
      handleLogout,
      removeNotification,
      dropdownOpen
    }
  }
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
}

.nav-link {
  transition: all 0.3s ease;
}

.nav-link:hover {
  transform: translateY(-1px);
}

.dropdown-menu {
  border: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.alert {
  border-radius: 8px;
}
</style>
