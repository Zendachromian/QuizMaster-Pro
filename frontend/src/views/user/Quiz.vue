<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">
                <i class="bi bi-search text-primary me-2"></i>
                Find & Take Quizzes
              </h1>
              <p class="text-muted">Search for quizzes across all subjects and start learning!</p>
            </div>
            <div>
              <button class="btn btn-outline-primary" @click="refreshQuizzes" :disabled="loading">
                <i class="bi bi-arrow-clockwise me-1"></i>
                {{ loading ? 'Loading...' : 'Refresh' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Search and Filter Section -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="card no-hover-effect">
            <div class="card-body">
              <div class="row g-3">
                <!-- Search Input -->
                <div class="col-md-4">
                  <label class="form-label small text-muted">Search Quizzes</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-search"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control"
                      placeholder="Search by quiz title, subject, or chapter..."
                      v-model="searchQuery"
                    >
                  </div>
                </div>

                <!-- Subject Filter -->
                <div class="col-md-2">
                  <label class="form-label small text-muted">Subject</label>
                  <select class="form-select" v-model="selectedSubject">
                    <option value="">All Subjects</option>
                    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
                      {{ subject.name }}
                    </option>
                  </select>
                </div>

                <!-- Difficulty Filter -->
                <div class="col-md-2">
                  <label class="form-label small text-muted">Difficulty</label>
                  <select class="form-select" v-model="selectedDifficulty">
                    <option value="">All Levels</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <!-- Duration Filter -->
                <div class="col-md-2">
                  <label class="form-label small text-muted">Duration</label>
                  <select class="form-select" v-model="selectedDuration">
                    <option value="">Any Duration</option>
                    <option value="0-15">0-15 minutes</option>
                    <option value="15-30">15-30 minutes</option>
                    <option value="30-60">30-60 minutes</option>
                    <option value="60+">60+ minutes</option>
                  </select>
                </div>

                <!-- Sort By -->
                <div class="col-md-2">
                  <label class="form-label small text-muted">Sort By</label>
                  <select class="form-select" v-model="sortBy">
                    <option value="name">Quiz Name</option>
                    <option value="difficulty">Difficulty</option>
                    <option value="duration">Duration</option>
                    <option value="attempts">Most Attempted</option>
                    <option value="newest">Newest First</option>
                  </select>
                </div>
              </div>

              <!-- Active Filters -->
              <div v-if="hasActiveFilters" class="mt-3">
                <div class="d-flex align-items-center flex-wrap gap-2">
                  <small class="text-muted me-2">Active filters:</small>
                  <span v-if="searchQuery" class="badge bg-primary">
                    Search: "{{ searchQuery }}"
                    <button type="button" class="btn-close btn-close-white ms-1" @click="searchQuery = ''"></button>
                  </span>
                  <span v-if="selectedSubject" class="badge bg-success">
                    Subject: {{ getSubjectName(selectedSubject) }}
                    <button type="button" class="btn-close btn-close-white ms-1" @click="selectedSubject = ''"></button>
                  </span>
                  <span v-if="selectedDifficulty" class="badge bg-warning text-dark">
                    Difficulty: {{ selectedDifficulty }}
                    <button type="button" class="btn-close ms-1" @click="selectedDifficulty = ''"></button>
                  </span>
                  <span v-if="selectedDuration" class="badge bg-info">
                    Duration: {{ selectedDuration }}
                    <button type="button" class="btn-close btn-close-white ms-1" @click="selectedDuration = ''"></button>
                  </span>
                  <button class="btn btn-sm btn-outline-secondary" @click="clearAllFilters">
                    Clear All
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Summary -->
      <div class="row mb-3">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h5 class="mb-0">
                {{ filteredQuizzes.length }} quiz{{ filteredQuizzes.length !== 1 ? 'es' : '' }} found
              </h5>
              <small class="text-muted" v-if="filteredQuizzes.length !== totalQuizzes">
                Showing {{ filteredQuizzes.length }} of {{ totalQuizzes }} total quizzes
              </small>
            </div>
            <div class="d-flex gap-2">
              <button
                class="btn btn-sm"
                :class="viewMode === 'grid' ? 'btn-primary' : 'btn-outline-primary'"
                @click="viewMode = 'grid'"
              >
                <i class="bi bi-grid"></i>
              </button>
              <button
                class="btn btn-sm"
                :class="viewMode === 'list' ? 'btn-primary' : 'btn-outline-primary'"
                @click="viewMode = 'list'"
              >
                <i class="bi bi-list"></i>
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
        <p class="mt-3 text-muted">Searching for quizzes...</p>
      </div>

      <!-- No Results State -->
      <div v-else-if="filteredQuizzes.length === 0" class="text-center py-5">
        <i class="bi bi-search display-1 text-muted"></i>
        <h4 class="mt-3">No quizzes found</h4>
        <p class="text-muted">
          {{ hasActiveFilters ? 'Try adjusting your search criteria.' : 'No quizzes are available at the moment.' }}
        </p>
        <button v-if="hasActiveFilters" class="btn btn-primary" @click="clearAllFilters">
          Clear All Filters
        </button>
      </div>

      <!-- Quiz Results Grid View -->
      <div v-else-if="viewMode === 'grid'" class="row">
        <div
          v-for="quiz in paginatedQuizzes"
          :key="quiz.id"
          class="col-lg-4 col-md-6 mb-4"
        >
          <div class="card quiz-card h-100">
            <div class="card-header d-flex justify-content-between align-items-start">
              <div class="flex-grow-1">
                <h6 class="card-title mb-1">{{ quiz.title }}</h6>
                <div class="quiz-meta">
                  <small class="text-muted">
                    <i class="bi bi-book me-1"></i>{{ quiz.subject_name }}
                  </small>
                  <span class="mx-2">•</span>
                  <small class="text-muted">
                    <i class="bi bi-bookmark me-1"></i>{{ quiz.chapter_name }}
                  </small>
                </div>
              </div>
              <span class="badge" :class="getDifficultyClass(quiz.difficulty)">
                {{ quiz.difficulty || 'Medium' }}
              </span>
            </div>
            <div class="card-body">
              <p class="card-text text-muted small">{{ quiz.description }}</p>

              <!-- Quiz Stats -->
              <div class="quiz-stats mb-3">
                <div class="row text-center">
                  <div class="col-4">
                    <div class="stat-item">
                      <i class="bi bi-clock text-warning"></i>
                      <div class="small">{{ quiz.time_duration }}min</div>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="stat-item">
                      <i class="bi bi-question-circle text-info"></i>
                      <div class="small">{{ quiz.total_questions }}</div>
                    </div>
                  </div>
                  <div class="col-4">
                    <div class="stat-item">
                      <i class="bi bi-star text-success"></i>
                      <div class="small">{{ quiz.max_marks }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Quiz Status -->
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center">
                  <span class="small text-muted">Status:</span>
                  <span class="badge" :class="getStatusClass(quiz.status)">
                    <i :class="getStatusIcon(quiz.status)" class="me-1"></i>
                    {{ getStatusText(quiz.status) }}
                  </span>
                </div>
                <div v-if="quiz.status_message" class="small text-muted mt-1">
                  <i class="bi bi-info-circle me-1"></i>
                  {{ quiz.status_message }}
                </div>
              </div>

              <!-- Previous Attempts (if any) -->
              <div v-if="quiz.user_attempts && quiz.user_attempts.length > 0" class="mb-3">
                <h6 class="small text-muted mb-2">Your Best Score:</h6>
                <div class="d-flex justify-content-between align-items-center">
                  <span class="badge" :class="getScoreClass(quiz.best_score)">
                    {{ quiz.best_score }}%
                  </span>
                  <small class="text-muted">{{ quiz.user_attempts.length }} attempt(s)</small>
                </div>
              </div>
            </div>
            <div class="card-footer bg-transparent">
              <div class="d-grid">
                <button
                  v-if="authStore.user?.role !== 'admin'"
                  class="btn btn-primary"
                  @click="startQuiz(quiz)"
                  :disabled="!canTakeQuiz(quiz)"
                >
                  <i class="bi bi-play-circle me-1"></i>
                  {{ getQuizActionText(quiz) }}
                </button>
                <div v-else class="text-center text-muted">
                  <i class="bi bi-shield-check me-1"></i>
                  Admin access only for management
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quiz Results List View -->
      <div v-else class="card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Quiz</th>
                  <th>Subject/Chapter</th>
                  <th>Status</th>
                  <th>Difficulty</th>
                  <th>Duration</th>
                  <th>Questions</th>
                  <th>Your Best</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="quiz in paginatedQuizzes" :key="quiz.id">
                  <td>
                    <div>
                      <strong>{{ quiz.title }}</strong>
                      <div class="small text-muted">{{ truncateText(quiz.description, 50) }}</div>
                    </div>
                  </td>
                  <td>
                    <div class="small">
                      <div class="text-primary">{{ quiz.subject_name }}</div>
                      <div class="text-muted">{{ quiz.chapter_name }}</div>
                    </div>
                  </td>
                  <td>
                    <div>
                      <span class="badge" :class="getStatusClass(quiz.status)">
                        <i :class="getStatusIcon(quiz.status)" class="me-1"></i>
                        {{ getStatusText(quiz.status) }}
                      </span>
                      <div v-if="quiz.status_message" class="small text-muted mt-1">
                        {{ quiz.status_message }}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span class="badge" :class="getDifficultyClass(quiz.difficulty)">
                      {{ quiz.difficulty || 'Medium' }}
                    </span>
                  </td>
                  <td>
                    <span class="badge bg-light text-dark">
                      <i class="bi bi-clock me-1"></i>{{ quiz.time_duration }}min
                    </span>
                  </td>
                  <td>
                    <span class="badge bg-light text-dark">
                      {{ quiz.total_questions }} questions
                    </span>
                  </td>
                  <td>
                    <span v-if="quiz.best_score" class="badge" :class="getScoreClass(quiz.best_score)">
                      {{ quiz.best_score }}%
                    </span>
                    <span v-else class="text-muted small">Not attempted</span>
                  </td>
                  <td>
                    <button
                      v-if="authStore.user?.role !== 'admin'"
                      class="btn btn-sm btn-primary"
                      @click="startQuiz(quiz)"
                      :disabled="!canTakeQuiz(quiz)"
                    >
                      <i class="bi bi-play-circle me-1"></i>
                      {{ getQuizActionText(quiz) }}
                    </button>
                    <span v-else class="text-muted small">
                      <i class="bi bi-shield-check me-1"></i>
                      Admin only
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="row mt-4">
        <div class="col-12">
          <nav aria-label="Quiz pagination">
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

      <!-- Quiz Start Confirmation Modal -->
      <div
        class="modal fade"
        :class="{ show: showStartModal, 'd-block': showStartModal }"
        :style="{ display: showStartModal ? 'block' : 'none' }"
        tabindex="-1"
      >
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Start Quiz: {{ selectedQuiz?.title }}</h5>
              <button type="button" class="btn-close" @click="showStartModal = false"></button>
            </div>
            <div class="modal-body" v-if="selectedQuiz">
              <div class="alert alert-info">
                <h6><i class="bi bi-info-circle me-2"></i>Quiz Instructions</h6>
                <ul class="mb-0">
                  <li>Duration: <strong>{{ selectedQuiz.time_duration }} minutes</strong></li>
                  <li>Questions: <strong>{{ selectedQuiz.total_questions }}</strong></li>
                  <li>Total Marks: <strong>{{ selectedQuiz.max_marks }}</strong></li>
                  <li v-if="selectedQuiz.passing_score">Passing Score: <strong>{{ selectedQuiz.passing_score }}%</strong></li>
                  <li v-if="selectedQuiz.max_attempts">Attempts Allowed: <strong>{{ selectedQuiz.max_attempts }}</strong></li>
                </ul>
              </div>
              <div class="alert alert-warning">
                <strong>Important:</strong> Once you start, the timer will begin automatically.
                Make sure you have a stable internet connection and sufficient time to complete the quiz.
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="showStartModal = false">
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-success"
                @click="confirmStartQuiz"
                :disabled="starting"
              >
                <span v-if="starting" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-play-circle me-1"></i>
                Start Quiz Now
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal backdrop -->
      <div
        v-if="showStartModal"
        class="modal-backdrop fade show"
        @click="showStartModal = false"
      ></div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'
import { truncateText } from '@/utils/helpers'

export default {
  name: 'QuizSearch',
  components: { AppLayout },
  setup () {
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const starting = ref(false)
    const quizzes = ref([])
    const subjects = ref([])
    const searchQuery = ref('')
    const selectedSubject = ref('')
    const selectedDifficulty = ref('')
    const selectedDuration = ref('')
    const sortBy = ref('name')
    const viewMode = ref('grid')
    const currentPage = ref(1)
    const itemsPerPage = 12
    const showStartModal = ref(false)
    const selectedQuiz = ref(null)

    const totalQuizzes = computed(() => quizzes.value.length)

    const filteredQuizzes = computed(() => {
      let filtered = [...quizzes.value]

      // Apply search filter
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(quiz =>
          quiz.title.toLowerCase().includes(query) ||
          quiz.description.toLowerCase().includes(query) ||
          quiz.subject_name.toLowerCase().includes(query) ||
          quiz.chapter_name.toLowerCase().includes(query)
        )
      }

      // Apply subject filter
      if (selectedSubject.value) {
        filtered = filtered.filter(quiz => quiz.subject_id === parseInt(selectedSubject.value))
      }

      // Apply difficulty filter
      if (selectedDifficulty.value) {
        filtered = filtered.filter(quiz => quiz.difficulty === selectedDifficulty.value)
      }

      // Apply duration filter
      if (selectedDuration.value) {
        const [min, max] = selectedDuration.value.split('-').map(v => v.replace('+', ''))
        filtered = filtered.filter(quiz => {
          const duration = quiz.time_duration
          if (selectedDuration.value === '60+') return duration >= 60
          return duration >= parseInt(min) && duration <= parseInt(max)
        })
      }

      // Apply sorting
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'name':
            return a.title.localeCompare(b.title)
          case 'difficulty': {
            const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 }
            return (difficultyOrder[a.difficulty] || 2) - (difficultyOrder[b.difficulty] || 2)
          }
          case 'duration':
            return a.time_duration - b.time_duration
          case 'attempts':
            return (b.attempt_count || 0) - (a.attempt_count || 0)
          case 'newest':
            return new Date(b.created_at || 0) - new Date(a.created_at || 0)
          default:
            return 0
        }
      })

      return filtered
    })

    const paginatedQuizzes = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage
      const end = start + itemsPerPage
      return filteredQuizzes.value.slice(start, end)
    })

    const totalPages = computed(() => {
      return Math.ceil(filteredQuizzes.value.length / itemsPerPage)
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

    const hasActiveFilters = computed(() => {
      return searchQuery.value || selectedSubject.value || selectedDifficulty.value || selectedDuration.value
    })

    const loadQuizzes = async () => {
      try {
        loading.value = true
        const response = await fetch('/api/user/quizzes/search', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          quizzes.value = data.quizzes || []
          subjects.value = data.subjects || []
        } else {
          throw new Error('Failed to load quizzes')
        }
      } catch (error) {
        console.error('Error loading quizzes:', error)
        notificationStore.error('Failed to load quizzes')
      } finally {
        loading.value = false
      }
    }

    const refreshQuizzes = () => {
      loadQuizzes()
    }

    const startQuiz = (quiz) => {
      selectedQuiz.value = quiz
      showStartModal.value = true
    }

    const confirmStartQuiz = async () => {
      console.log('confirmStartQuiz called')
      if (!selectedQuiz.value) return

      try {
        starting.value = true
        console.log('Making API call to start quiz:', selectedQuiz.value.id)
        const response = await fetch(`/api/user/quiz/${selectedQuiz.value.id}/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          }
        })

        console.log('API response status:', response.status)
        if (response.ok) {
          const data = await response.json()
          console.log('API response data:', data)
          if (data.success) {
            console.log('Navigating to quiz taking page:', `/quiz/${selectedQuiz.value.id}/take`)
            router.push(`/quiz/${selectedQuiz.value.id}/take`)
          } else {
            throw new Error(data.message || data.error || 'Failed to start quiz')
          }
        } else {
          const errorData = await response.json()
          console.error('API error response:', errorData)
          throw new Error(errorData.message || errorData.error || 'Failed to start quiz')
        }
      } catch (error) {
        console.error('Error starting quiz:', error)
        notificationStore.error(error.message || 'Failed to start quiz')
      } finally {
        starting.value = false
        showStartModal.value = false
      }
    }

    const canTakeQuiz = (quiz) => {
      if (!quiz.max_attempts) return true
      return (quiz.user_attempts?.length || 0) < quiz.max_attempts
    }

    const getQuizActionText = (quiz) => {
      if (quiz.user_attempts && quiz.user_attempts.length > 0) return 'Retake Quiz'
      return 'Start Quiz'
    }

    const getStatusClass = (status) => {
      switch (status) {
        case 'ongoing': return 'bg-warning text-dark'
        case 'completed': return 'bg-success'
        case 'upcoming': return 'bg-info'
        case 'available': return 'bg-primary'
        default: return 'bg-secondary'
      }
    }

    const getStatusIcon = (status) => {
      switch (status) {
        case 'ongoing': return 'bi-play-circle-fill'
        case 'completed': return 'bi-check-circle-fill'
        case 'upcoming': return 'bi-clock-fill'
        case 'available': return 'bi-play-fill'
        default: return 'bi-question-circle'
      }
    }

    const getStatusText = (status) => {
      switch (status) {
        case 'ongoing': return 'In Progress'
        case 'completed': return 'Completed'
        case 'upcoming': return 'Upcoming'
        case 'available': return 'Available'
        default: return 'Unknown'
      }
    }

    const getDifficultyClass = (difficulty) => {
      switch (difficulty?.toLowerCase()) {
        case 'beginner': return 'bg-success'
        case 'intermediate': return 'bg-warning text-dark'
        case 'advanced': return 'bg-danger'
        default: return 'bg-primary'
      }
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 75) return 'bg-primary'
      if (score >= 60) return 'bg-warning text-dark'
      return 'bg-danger'
    }

    const getSubjectName = (subjectId) => {
      const subject = subjects.value.find(s => s.id === parseInt(subjectId))
      return subject ? subject.name : 'Unknown'
    }

    const clearAllFilters = () => {
      searchQuery.value = ''
      selectedSubject.value = ''
      selectedDifficulty.value = ''
      selectedDuration.value = ''
      currentPage.value = 1
    }

    const goToPage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page
      }
    }

    // Reset pagination when filters change
    watch([searchQuery, selectedSubject, selectedDifficulty, selectedDuration, sortBy], () => {
      currentPage.value = 1
    })

    onMounted(() => {
      loadQuizzes()
    })

    return {
      authStore,
      loading,
      starting,
      quizzes,
      subjects,
      searchQuery,
      selectedSubject,
      selectedDifficulty,
      selectedDuration,
      sortBy,
      viewMode,
      currentPage,
      showStartModal,
      selectedQuiz,
      totalQuizzes,
      filteredQuizzes,
      paginatedQuizzes,
      totalPages,
      visiblePages,
      hasActiveFilters,
      refreshQuizzes,
      startQuiz,
      confirmStartQuiz,
      canTakeQuiz,
      getQuizActionText,
      getStatusClass,
      getStatusIcon,
      getStatusText,
      getDifficultyClass,
      getScoreClass,
      getSubjectName,
      clearAllFilters,
      goToPage,
      truncateText
    }
  }
}
</script>

<style scoped>
.quiz-card {
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.quiz-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Make quiz title text dark on hover */
.quiz-card:hover .card-title {
  color: #2c3e50 !important;
  font-weight: 600;
}

/* Also apply to list view quiz titles */
.table tbody tr:hover td strong {
  color: #2c3e50 !important;
}

.stat-item {
  text-align: center;
}

.stat-item i {
  font-size: 1.2rem;
  margin-bottom: 2px;
}

.badge .btn-close {
  font-size: 0.6rem;
  margin-left: 4px;
}

.card {
  border: none;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.08);
  border-radius: 10px;
}

.card-header {
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid #dee2e6;
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

.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 15px;
  }

  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
  }

  .quiz-stats .row > div {
    margin-bottom: 10px;
  }
}
</style>
