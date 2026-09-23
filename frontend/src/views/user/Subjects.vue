<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">
                <i class="bi bi-book-fill text-primary me-2"></i>
                Explore Subjects
              </h1>
              <p class="text-muted">Choose a subject and start your quiz journey!</p>
            </div>
            <div>
              <button class="btn btn-outline-primary" @click="refreshSubjects" :disabled="loading">
                <i class="bi bi-arrow-clockwise me-1"></i>
                {{ loading ? 'Loading...' : 'Refresh' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filter -->
      <div class="row mb-4">
        <div class="col-md-6">
          <div class="input-group">
            <span class="input-group-text">
              <i class="bi bi-search"></i>
            </span>
            <input
              type="text"
              class="form-control"
              placeholder="Search subjects..."
              v-model="searchQuery"
            >
          </div>
        </div>
        <div class="col-md-6">
          <select class="form-select" v-model="sortBy">
            <option value="name">Sort by Name</option>
            <option value="quizzes">Sort by Quiz Count</option>
            <option value="difficulty">Sort by Difficulty</option>
          </select>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading subjects...</p>
      </div>

      <!-- No Subjects State -->
      <div v-else-if="filteredSubjects.length === 0" class="text-center py-5">
        <i class="bi bi-book display-1 text-muted"></i>
        <h4 class="mt-3">No subjects found</h4>
        <p class="text-muted">
          {{ searchQuery ? 'Try adjusting your search terms.' : 'No subjects are available at the moment.' }}
        </p>
      </div>

      <!-- Subjects Grid -->
      <div v-else class="row">
        <div
          v-for="subject in filteredSubjects"
          :key="subject.id"
          class="col-lg-4 col-md-6 mb-4"
        >
          <div class="card h-100 subject-card" @click="exploreSubject(subject.id)">
            <div class="card-header border-primary">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 text-primary">
                  <i class="bi bi-mortarboard me-2"></i>
                  {{ subject.name }}
                </h5>
                <span class="badge bg-light text-dark border">
                  {{ subject.total_quizzes }} quizzes
                </span>
              </div>
            </div>
            <div class="card-body">
              <p class="card-text text-muted">{{ subject.description }}</p>

              <div class="row mb-3">
                <div class="col-6 text-center">
                  <div class="h5 text-primary mb-0">{{ subject.total_chapters }}</div>
                  <small class="text-muted">Chapters</small>
                </div>
                <div class="col-6 text-center">
                  <div class="h5 text-success mb-0">{{ subject.user_attempts || 0 }}</div>
                  <small class="text-muted">Your Attempts</small>
                </div>
              </div>

              <!-- Progress Bar -->
              <div class="mb-3" v-if="subject.user_progress">
                <div class="d-flex justify-content-between mb-1">
                  <small class="text-muted">Your Progress</small>
                  <small class="text-muted">{{ subject.user_progress }}%</small>
                </div>
                <div class="progress" style="height: 8px;">
                  <div
                    class="progress-bar"
                    :class="getProgressBarClass(subject.user_progress)"
                    :style="{ width: subject.user_progress + '%' }"
                  ></div>
                </div>
              </div>

              <!-- Best Score -->
              <div v-if="subject.best_score" class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="text-muted">Best Score:</span>
                  <span class="badge" :class="getScoreClass(subject.best_score)">
                    {{ subject.best_score }}%
                  </span>
                </div>
              </div>
            </div>
            <div class="card-footer bg-transparent">
              <div class="d-grid gap-2">
                <button class="btn btn-primary btn-sm" @click.stop="exploreSubject(subject.id)">
                  <i class="bi bi-play-circle me-1"></i>
                  Start Learning
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="row mt-4">
        <div class="col-12">
          <nav aria-label="Subjects pagination">
            <ul class="pagination justify-content-center">
              <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button class="page-link" @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">
                  Previous
                </button>
              </li>
              <li
                v-for="page in visiblePages"
                :key="page"
                class="page-item"
                :class="{ active: page === currentPage }"
              >
                <button class="page-link" @click="goToPage(page)">{{ page }}</button>
              </li>
              <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button class="page-link" @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">
                  Next
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'Subjects',
  components: { AppLayout },
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const subjects = ref([])
    const searchQuery = ref('')
    const sortBy = ref('name')
    const currentPage = ref(1)
    const itemsPerPage = 9

    const filteredSubjects = computed(() => {
      let filtered = [...subjects.value]

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(subject =>
          subject.name.toLowerCase().includes(query) ||
          subject.description.toLowerCase().includes(query)
        )
      }

      // Apply sorting
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'name':
            return a.name.localeCompare(b.name)
          case 'quizzes':
            return (b.total_quizzes || 0) - (a.total_quizzes || 0)
          case 'difficulty':
            return (a.difficulty_level || 0) - (b.difficulty_level || 0)
          default:
            return 0
        }
      })

      // Apply pagination
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filtered.slice(start, end)
    })

    const totalPages = computed(() => {
      const total = subjects.value.length
      return Math.ceil(total / itemsPerPage)
    })

    const visiblePages = computed(() => {
      const pages = []
      const start = Math.max(1, currentPage.value - 2)
      const end = Math.min(totalPages.value, start + 4)

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }
      return pages
    })

    const loadSubjects = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/user/subjects', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          subjects.value = data.subjects || []
        } else {
          throw new Error('Failed to load subjects')
        }
      } catch (error) {
        console.error('Error loading subjects:', error)
        notificationStore.error('Failed to load subjects')
      } finally {
        loading.value = false
      }
    }

    const refreshSubjects = () => {
      loadSubjects()
    }

    const exploreSubject = (subjectId) => {
      router.push(`/subjects/${subjectId}/chapters`)
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    const getProgressBarClass = (progress) => {
      if (progress >= 80) return 'bg-success'
      if (progress >= 60) return 'bg-info'
      if (progress >= 40) return 'bg-warning'
      return 'bg-danger'
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 75) return 'bg-primary'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    // Reset pagination when search or sort changes
    watch([searchQuery, sortBy], () => {
      currentPage.value = 1
    })

    onMounted(() => {
      loadSubjects()
    })

    return {
      loading,
      subjects,
      searchQuery,
      sortBy,
      currentPage,
      filteredSubjects,
      totalPages,
      visiblePages,
      refreshSubjects,
      exploreSubject,
      goToPage,
      getProgressBarClass,
      getScoreClass
    }
  }
}
</script>

<style scoped>
.subject-card {
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.card-header h5 {
  font-weight: 600;
}

.progress {
  border-radius: 10px;
}

.progress-bar {
  border-radius: 10px;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border: none;
  font-weight: 500;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #0056b3 0%, #004085 100%);
}

.page-link {
  border-radius: 8px;
  margin: 0 2px;
  border: 1px solid #dee2e6;
}

.page-item.active .page-link {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  border-color: #007bff;
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 15px;
  }

  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>
