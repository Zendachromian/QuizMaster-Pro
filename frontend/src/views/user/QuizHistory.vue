<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1 text-white">
                <i class="bi bi-clock-history text-primary me-2"></i>
                Quiz History
              </h1>
              <p class="text-white">View all your completed quiz attempts</p>
            </div>
            <div>
              <button class="btn btn-outline-primary" @click="loadHistory" :disabled="loading">
                <i class="bi bi-arrow-clockwise me-1"></i>
                {{ loading ? 'Loading...' : 'Refresh' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-white">Loading quiz history...</p>
      </div>

      <!-- Quiz History List -->
      <div v-else-if="attempts.length > 0" class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0 text-white">Recent Quiz Attempts</h5>
            </div>
            <div class="card-body p-0">
              <div class="table-responsive">
                <table class="table table-striped mb-0">
                  <thead>
                    <tr>
                      <th class="text-white">Quiz Title</th>
                      <th class="text-white">Subject</th>
                      <th class="text-white">Score</th>
                      <th class="text-white">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attempt in attempts" :key="attempt.id">
                      <td>
                        <strong class="text-white">{{ attempt.quiz_title || 'Unknown Quiz' }}</strong>
                        <br>
                        <small class="text-white">{{ attempt.chapter_name || 'Unknown Chapter' }}</small>
                      </td>
                      <td>
                        <span class="badge bg-info">
                          {{ attempt.subject_name || 'Unknown Subject' }}
                        </span>
                      </td>
                      <td>
                        <div class="d-flex align-items-center">
                          <div class="progress me-2" style="width: 60px; height: 8px;">
                            <div
                              class="progress-bar"
                              :class="getScoreClass(attempt.score_percentage)"
                              :style="`width: ${attempt.score_percentage}%`"
                            ></div>
                          </div>
                          <strong class="text-white">{{ attempt.score_percentage }}%</strong>
                        </div>
                        <small class="text-white">
                          {{ attempt.obtained_marks }}/{{ attempt.total_marks }} marks
                        </small>
                      </td>
                      <td>
                        <div class="text-white">{{ formatDate(attempt.end_time) }}</div>
                        <small class="text-white">{{ formatTime(attempt.end_time) }}</small>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div v-if="pagination && pagination.pages > 1" class="d-flex justify-content-center mt-4">
            <nav>
              <ul class="pagination">
                <li class="page-item" :class="{ disabled: pagination.page <= 1 }">
                  <button class="page-link" @click="changePage(pagination.page - 1)" :disabled="pagination.page <= 1">
                    Previous
                  </button>
                </li>
                <li
                  v-for="page in getPageNumbers()"
                  :key="page"
                  class="page-item"
                  :class="{ active: page === pagination.page }"
                >
                  <button class="page-link" @click="changePage(page)">{{ page }}</button>
                </li>
                <li class="page-item" :class="{ disabled: pagination.page >= pagination.pages }">
                  <button class="page-link" @click="changePage(pagination.page + 1)" :disabled="pagination.page >= pagination.pages">
                    Next
                  </button>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-5">
        <div class="mb-4">
          <i class="bi bi-clipboard-data display-1 text-muted"></i>
        </div>
        <h3 class="text-white">No Quiz History</h3>
        <p class="text-white mb-4">You haven't completed any quizzes yet.</p>
        <button class="btn btn-primary" @click="$router.push('/quiz')">
          <i class="bi bi-play-circle me-1"></i>
          Start Your First Quiz
        </button>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'QuizHistory',
  components: { AppLayout },
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const attempts = ref([])
    const pagination = ref(null)
    const currentPage = ref(1)

    const loadHistory = async (page = 1) => {
      try {
        loading.value = true
        const response = await fetch(`/api/user/history?page=${page}&per_page=10`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            attempts.value = data.attempts
            pagination.value = data.pagination
            currentPage.value = page
          } else {
            throw new Error(data.error || 'Failed to load history')
          }
        } else {
          throw new Error('Failed to load history')
        }
      } catch (error) {
        console.error('Error loading history:', error)
        notificationStore.error(error.message || 'Failed to load quiz history')
      } finally {
        loading.value = false
      }
    }

    const changePage = (page) => {
      if (page >= 1 && page <= pagination.value.pages) {
        loadHistory(page)
      }
    }

    const getPageNumbers = () => {
      if (!pagination.value) return []

      const current = pagination.value.page
      const total = pagination.value.pages
      const pages = []

      // Show max 5 page numbers
      let start = Math.max(1, current - 2)
      const end = Math.min(total, start + 4)

      if (end - start < 4) {
        start = Math.max(1, end - 4)
      }

      for (let i = start; i <= end; i++) {
        pages.push(i)
      }

      return pages
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 75) return 'bg-primary'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleDateString()
    }

    const formatTime = (dateString) => {
      if (!dateString) return 'Unknown'
      return new Date(dateString).toLocaleTimeString()
    }

    const viewResult = (quizId) => {
      router.push(`/quiz/${quizId}/result`)
    }

    const retakeQuiz = (quizId) => {
      router.push(`/quiz/${quizId}/take`)
    }

    onMounted(() => {
      loadHistory()
    })

    return {
      loading,
      attempts,
      pagination,
      currentPage,
      loadHistory,
      changePage,
      getPageNumbers,
      getScoreClass,
      formatDate,
      formatTime,
      viewResult,
      retakeQuiz
    }
  }
}
</script>

<style scoped>
.progress {
  border-radius: 4px;
}

/* Hover effect removed */
.table tbody tr:hover {
  background-color: transparent !important;
}

/* Turn "Recent Quiz Attempts" text black on hover */
.card-header:hover h5,
.card:hover .card-header h5 {
  color: black !important;
}

.pagination .page-link {
  border-color: #dee2e6;
  color: #6c757d;
}

.pagination .page-item.active .page-link {
  background-color: #007bff;
  border-color: #007bff;
}

.pagination .page-link:hover {
  background-color: #e9ecef;
  border-color: #dee2e6;
}
</style>
