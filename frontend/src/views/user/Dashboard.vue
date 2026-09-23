<template>
  <AppLayout>
    <div class="container-fluid">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">Welcome back, {{ userName }}! 👋</h1>
              <p class="text-muted">Ready to test your knowledge today?</p>
            </div>
            <div>
              <button class="btn btn-outline-primary me-2" @click="refreshData" :disabled="loading">
                <i class="bi bi-arrow-clockwise me-1"></i>
                {{ loading ? 'Loading...' : 'Refresh' }}
              </button>
              <button v-if="!authStore.isAdmin" class="btn btn-outline-secondary" @click="exportData">
                <i class="bi bi-download me-1"></i>Export Data
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-primary">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-primary">
                <i class="bi bi-list-check"></i>
              </div>
              <h3 class="mb-1 text-primary">{{ stats.total_attempts || 0 }}</h3>
              <p class="mb-0 small text-muted">Total Attempts</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-success">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-success">
                <i class="bi bi-trophy"></i>
              </div>
              <h3 class="mb-1 text-success">{{ stats.average_score || 0 }}%</h3>
              <p class="mb-0 small text-muted">Average Score</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-info">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-info">
                <i class="bi bi-star"></i>
              </div>
              <h3 class="mb-1 text-info">{{ stats.best_score || 0 }}%</h3>
              <p class="mb-0 small text-muted">Best Score</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-warning">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-warning">
                <i class="bi bi-book"></i>
              </div>
              <h3 class="mb-1 text-warning">{{ stats.subjects_available || 0 }}</h3>
              <p class="mb-0 small text-muted">Subjects Available</p>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Recent Quiz Attempts -->
        <div class="col-lg-8 mb-4">
          <div class="card h-100 no-hover-effect">
            <div class="card-header border-bottom">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                  <i class="bi bi-clock-history me-2 text-primary"></i>Quiz Attempt History
                </h5>
                <div>
                  <button class="btn btn-sm btn-outline-secondary me-2" @click="refreshAttempts">
                    <i class="bi bi-arrow-clockwise"></i>
                  </button>
                  <router-link to="/quiz-history" class="btn btn-sm btn-outline-primary">
                    View All
                  </router-link>
                </div>
              </div>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="mt-2 text-muted">Loading quiz attempts...</p>
              </div>

              <div v-else-if="recentAttempts.length === 0" class="text-center py-4">
                <i class="bi bi-clipboard-x display-4 text-muted"></i>
                <p class="mt-3 text-muted">No quiz attempts yet. Start your learning journey!</p>
                <router-link to="/subjects" class="btn btn-primary">
                  <i class="bi bi-play-circle me-1"></i>Browse Subjects
                </router-link>
              </div>

              <div v-else class="quiz-attempts">
                <div
                  v-for="attempt in recentAttempts"
                  :key="attempt.id"
                  class="attempt-card mb-3"
                >
                  <div class="d-flex justify-content-between align-items-start">
                    <div class="attempt-info flex-grow-1">
                      <div class="d-flex align-items-center mb-2">
                        <h6 class="mb-0 me-2">{{ attempt.quiz_title }}</h6>
                        <span class="badge" :class="getStatusBadgeClass(attempt.status)">
                          {{ getStatusText(attempt.status) }}
                        </span>
                      </div>
                      <div class="row text-muted small">
                        <div class="col-sm-6">
                          <i class="bi bi-book me-1"></i>{{ attempt.subject_name }}
                          <span class="mx-2">•</span>
                          <i class="bi bi-bookmark me-1"></i>{{ attempt.chapter_name }}
                        </div>
                        <div class="col-sm-6">
                          <i class="bi bi-clock me-1"></i>{{ formatDateTime(attempt.end_time || attempt.start_time) }}
                        </div>
                      </div>
                      <div class="row mt-2">
                        <div class="col-sm-3">
                          <small class="text-muted">Score:</small>
                          <div class="h6 mb-0">
                            <span :class="getScoreTextClass(attempt.score_percentage)">
                              {{ attempt.score_percentage || 0 }}%
                            </span>
                          </div>
                        </div>
                        <div class="col-sm-3">
                          <small class="text-muted">Time:</small>
                          <div class="h6 mb-0">{{ formatDuration(attempt.time_taken) }}</div>
                        </div>
                        <div class="col-sm-3">
                          <small class="text-muted">Questions:</small>
                          <div class="h6 mb-0">{{ attempt.correct_answers || 0 }}/{{ attempt.total_questions }}</div>
                        </div>
                        <div class="col-sm-3">
                          <small class="text-muted">Marks:</small>
                          <div class="h6 mb-0">{{ attempt.obtained_marks || 0 }}/{{ attempt.total_marks }}</div>
                        </div>
                      </div>
                    </div>
                    <div class="attempt-actions">
                      <div class="btn-group-vertical btn-group-sm">
                        <button
                          v-if="attempt.status === 'completed'"
                          class="btn btn-outline-primary"
                          @click="viewResult(attempt.quiz_id, attempt.id)"
                          title="View Result"
                        >
                          <i class="bi bi-eye"></i>
                        </button>
                        <button
                          v-if="attempt.status === 'in_progress'"
                          class="btn btn-outline-success"
                          @click="resumeQuiz(attempt.quiz_id)"
                          title="Resume Quiz"
                        >
                          <i class="bi bi-play-circle"></i>
                        </button>
                        <button
                          v-if="canRetakeQuiz(attempt)"
                          class="btn btn-outline-warning"
                          @click="retakeQuiz(attempt.quiz_id)"
                          title="Retake Quiz"
                        >
                          <i class="bi bi-arrow-clockwise"></i>
                        </button>
                      </div>
                    </div>
                  </div>
                  <!-- Progress Bar for Score -->
                  <div class="mt-2">
                    <div class="progress" style="height: 6px;">
                      <div
                        class="progress-bar"
                        :class="getProgressBarClass(attempt.score_percentage)"
                        :style="{ width: (attempt.score_percentage || 0) + '%' }"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions & Available Subjects -->
        <div class="col-lg-4 mb-4">
          <!-- Quick Actions -->
          <div class="card mb-4 no-hover-effect">
            <div class="card-header bg-white text-dark">
              <h5 class="mb-0 text-dark">
                <i class="bi bi-lightning-fill text-warning me-2"></i>Quick Actions
              </h5>
            </div>
            <div class="card-body">
              <div class="d-grid gap-2">
                <router-link to="/subjects" class="btn btn-primary">
                  <i class="bi bi-book me-2"></i>Browse All Subjects
                </router-link>
                <router-link to="/quiz" class="btn btn-outline-primary">
                  <i class="bi bi-search me-2"></i>Search & Take Quiz
                </router-link>
                <router-link to="/analytics" class="btn btn-outline-info">
                  <i class="bi bi-graph-up me-2"></i>View Analytics
                </router-link>
                <button v-if="!authStore.isAdmin" class="btn btn-outline-info" @click="exportData">
                  <i class="bi bi-download me-2"></i>Export My Data
                </button>
              </div>
            </div>
          </div>

          <!-- Available Subjects -->
          <div class="card">
            <div class="card-header bg-white text-dark">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 text-dark">
                  <i class="bi bi-mortarboard text-success me-2"></i>Popular Subjects
                </h5>
                <router-link to="/subjects" class="btn btn-sm btn-outline-success">
                  View All
                </router-link>
              </div>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-3">
                <div class="spinner-border spinner-border-sm text-primary"></div>
                <p class="mt-2 text-muted small">Loading subjects...</p>
              </div>

              <div v-else-if="subjects.length === 0" class="text-center py-3">
                <i class="bi bi-book display-6 text-muted"></i>
                <p class="mt-2 text-muted small">No subjects available.</p>
              </div>

              <div v-else class="subjects-list">
                <div
                  v-for="subject in subjects.slice(0, 5)"
                  :key="subject.id"
                  class="subject-item"
                  @click="exploreSubject(subject.id)"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div class="flex-grow-1">
                      <h6 class="mb-1">{{ subject.name }}</h6>
                      <div class="row">
                        <div class="col-6">
                          <small class="text-muted">
                            <i class="bi bi-collection me-1"></i>{{ subject.total_chapters }} chapters
                          </small>
                        </div>
                        <div class="col-6">
                          <small class="text-muted">
                            <i class="bi bi-question-circle me-1"></i>{{ subject.total_quizzes }} quizzes
                          </small>
                        </div>
                      </div>
                      <!-- Progress indicator -->
                      <div v-if="subject.user_progress" class="mt-2">
                        <div class="progress" style="height: 4px;">
                          <div
                            class="progress-bar bg-success"
                            :style="{ width: subject.user_progress + '%' }"
                          ></div>
                        </div>
                        <small class="text-muted">{{ subject.user_progress }}% complete</small>
                      </div>
                    </div>
                    <div class="ms-2">
                      <i class="bi bi-chevron-right text-muted"></i>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'
import { formatDateTime, truncateText, getScoreClass } from '@/utils/helpers'

export default {
  name: 'Dashboard',
  components: {
    AppLayout
  },
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const stats = ref({
      total_attempts: 0,
      average_score: 0,
      best_score: 0,
      subjects_available: 0
    })
    const recentAttempts = ref([])
    const subjects = ref([])

    const userName = computed(() => authStore.userName)

    const loadDashboardData = async () => {
      try {
        loading.value = true

        // Load dashboard data
        const response = await fetch('/api/user/dashboard', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          stats.value = data.stats
          recentAttempts.value = data.recent_attempts || []
          subjects.value = data.subjects || []
        }
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        notificationStore.error('Failed to load dashboard data')
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    const refreshAttempts = async () => {
      try {
        const response = await fetch('/api/user/quiz-attempts/recent', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          recentAttempts.value = data.attempts || []
        }
      } catch (error) {
        console.error('Error refreshing attempts:', error)
        notificationStore.error('Failed to refresh attempts')
      }
    }

    const exportData = async () => {
      try {
        const response = await fetch('/api/user/export-data', {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          // Create a blob from the response and trigger download
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `quiz_data_${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)

          notificationStore.success('Quiz data exported successfully!')
        } else {
          throw new Error('Export failed')
        }
      } catch (error) {
        console.error('Export error:', error)
        notificationStore.error('Failed to export data')
      }
    }

    const findRecommendedQuiz = async () => {
      try {
        const response = await fetch('/api/user/recommended-quiz', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.quiz) {
            router.push(`/subjects/${data.quiz.subject_id}/chapters`)
          } else {
            notificationStore.info('No recommended quiz found. Try browsing subjects!')
          }
        }
      } catch (error) {
        console.error('Error finding recommended quiz:', error)
        notificationStore.error('Failed to find recommended quiz')
      }
    }

    const viewResult = (quizId, attemptId) => {
      router.push(`/quiz/${quizId}/result/${attemptId}`)
    }

    const resumeQuiz = (quizId) => {
      router.push(`/quiz/${quizId}/take`)
    }

    const retakeQuiz = (quizId) => {
      router.push(`/quiz/${quizId}/take`)
    }

    const exploreSubject = (subjectId) => {
      router.push(`/subjects/${subjectId}/chapters`)
    }

    const canRetakeQuiz = (attempt) => {
      return attempt.status === 'completed' && attempt.retakes_allowed
    }

    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'completed': return 'bg-success'
        case 'in_progress': return 'bg-warning'
        case 'failed': return 'bg-danger'
        case 'passed': return 'bg-success'
        default: return 'bg-secondary'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'completed': return 'Completed'
        case 'in_progress': return 'In Progress'
        case 'failed': return 'Failed'
        case 'passed': return 'Passed'
        default: return 'Unknown'
      }
    }

    const getScoreTextClass = (score) => {
      if (score >= 90) return 'text-success fw-bold'
      if (score >= 75) return 'text-primary fw-bold'
      if (score >= 60) return 'text-warning fw-bold'
      return 'text-danger fw-bold'
    }

    const getProgressBarClass = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 75) return 'bg-primary'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    const formatDuration = (seconds) => {
      if (!seconds) return '--'

      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = seconds % 60

      if (hours > 0) {
        return `${hours}h ${minutes}m`
      } else if (minutes > 0) {
        return `${minutes}m ${secs}s`
      } else {
        return `${secs}s`
      }
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      authStore,
      loading,
      stats,
      recentAttempts,
      subjects,
      userName,
      refreshData,
      refreshAttempts,
      exportData,
      findRecommendedQuiz,
      viewResult,
      resumeQuiz,
      retakeQuiz,
      exploreSubject,
      canRetakeQuiz,
      getStatusBadgeClass,
      getStatusText,
      getScoreTextClass,
      getProgressBarClass,
      formatDateTime,
      formatDuration,
      truncateText,
      getScoreClass
    }
  }
}
</script>

<style scoped>
.stats-card-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.card {
  border: none;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.08);
  border-radius: 10px;
}

.card-header {
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
  border-radius: 10px 10px 0 0 !important;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-outline-primary:hover,
.btn-outline-success:hover,
.btn-outline-info:hover,
.btn-outline-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

/* New Quiz Attempts Styling */
.attempt-card {
  padding: 15px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s ease;
}

.attempt-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  background: #ffffff;
}

.attempt-info h6 {
  color: #2c3e50;
  font-weight: 600;
}

.attempt-actions .btn {
  width: 35px;
  height: 35px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

/* Subject List Styling */
.subjects-list .subject-item {
  padding: 12px 0;
  border-bottom: 1px solid #f1f3f4;
  cursor: pointer;
  transition: all 0.2s ease;
}

.subjects-list .subject-item:hover {
  background-color: #f8f9fa;
  border-radius: 6px;
  padding-left: 8px;
  padding-right: 8px;
}

.subjects-list .subject-item:last-child {
  border-bottom: none;
}

.subjects-list h6 {
  font-weight: 600;
  color: #2c3e50;
}

/* Loading Spinner */
.loading-spinner {
  width: 1.5rem;
  height: 1.5rem;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Progress Bars */
.progress {
  height: 6px;
  border-radius: 10px;
}

.progress-bar {
  border-radius: 10px;
}

/* Responsive Design */
@media (max-width: 768px) {
  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
  }

  .attempt-actions {
    margin-top: 10px;
    text-align: center;
  }

  .attempt-actions .btn-group-vertical {
    flex-direction: row;
    gap: 5px;
  }
}

/* Chart container styles */
canvas {
  max-height: 300px !important;
}

.card-body canvas {
  width: 100% !important;
  height: 300px !important;
}

/* Chart card styling */
.card-header h5 {
  font-size: 1rem;
  font-weight: 600;
}

.card-header i {
  font-size: 1.1rem;
}

/* Quick Actions Button Styling */
.btn {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:hover {
  transform: translateY(-1px);
}

/* Badge Styling */
.badge {
  font-size: 0.75rem;
  padding: 4px 8px;
  border-radius: 4px;
}

/* Status indicators */
.text-success.fw-bold,
.text-primary.fw-bold,
.text-warning.fw-bold,
.text-danger.fw-bold {
  font-size: 1.1rem;
}
</style>
