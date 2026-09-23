<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Back Navigation -->
      <div class="row mb-3">
        <div class="col-12">
          <button class="btn btn-outline-secondary" @click="$router.push('/subjects')">
            <i class="bi bi-arrow-left me-1"></i>
            Back to Subjects
          </button>
        </div>
      </div>

      <!-- Subject Header -->
      <div class="row mb-4" v-if="subject">
        <div class="col-12">
          <div class="card bg-gradient-primary text-white">
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <h1 class="h2 mb-2">
                    <i class="bi bi-book-fill me-2"></i>
                    {{ subject.name }}
                  </h1>
                  <p class="mb-3 opacity-90">{{ subject.description }}</p>
                  <div class="row">
                    <div class="col-sm-4 text-center text-sm-start">
                      <div class="h4 mb-0">{{ subject.total_chapters }}</div>
                      <small>Chapters</small>
                    </div>
                    <div class="col-sm-4 text-center">
                      <div class="h4 mb-0">{{ subject.total_quizzes }}</div>
                      <small>Total Quizzes</small>
                    </div>
                    <div class="col-sm-4 text-center text-sm-end">
                      <div class="h4 mb-0">{{ subject.user_attempts || 0 }}</div>
                      <small>Your Attempts</small>
                    </div>
                  </div>
                </div>
                <div class="col-md-4 text-center">
                  <div class="subject-stats">
                    <div v-if="subject.user_progress" class="mb-3">
                      <div class="progress-circle mx-auto" :data-progress="subject.user_progress">
                        <div class="progress-text">
                          <div class="h3 mb-0">{{ subject.user_progress }}%</div>
                          <small>Progress</small>
                        </div>
                      </div>
                    </div>
                    <div v-if="subject.best_score" class="mt-3">
                      <span class="badge bg-light text-dark fs-6">
                        Best Score: {{ subject.best_score }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading chapters and quizzes...</p>
      </div>

      <!-- Chapters and Quizzes -->
      <div v-else-if="chapters.length > 0">
        <div
          v-for="chapter in chapters"
          :key="chapter.id"
          class="card mb-4 chapter-card"
        >
          <div class="card-header">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5 class="mb-1">
                  <i class="bi bi-bookmark-fill text-primary me-2"></i>
                  {{ chapter.name }}
                </h5>
                <p class="mb-0 text-muted">{{ chapter.description }}</p>
              </div>
              <div class="text-end">
                <span class="badge bg-primary me-2">
                  {{ chapter.quizzes?.length || 0 }} quizzes
                </span>
                <span v-if="chapter.completion_percentage" class="badge bg-success">
                  {{ chapter.completion_percentage }}% complete
                </span>
              </div>
            </div>
          </div>
          <div class="card-body">
            <div v-if="chapter.quizzes && chapter.quizzes.length > 0" class="row">
              <div
                v-for="quiz in chapter.quizzes"
                :key="quiz.id"
                class="col-lg-4 col-md-6 mb-3"
              >
                <div class="card quiz-card h-100">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                      <h6 class="card-title mb-0">{{ quiz.title }}</h6>
                      <span
                        class="badge"
                        :class="getQuizStatusClass(quiz.status)"
                      >
                        {{ getQuizStatusText(quiz.status) }}
                      </span>
                    </div>
                    <p class="card-text text-muted small">{{ quiz.description }}</p>

                    <!-- Quiz Info -->
                    <div class="quiz-info mb-3">
                      <div class="row text-center">
                        <div class="col-4">
                          <div class="info-item">
                            <i class="bi bi-clock text-warning"></i>
                            <div class="small">{{ quiz.time_duration }}min</div>
                          </div>
                        </div>
                        <div class="col-4">
                          <div class="info-item">
                            <i class="bi bi-question-circle text-info"></i>
                            <div class="small">{{ quiz.total_questions }}</div>
                          </div>
                        </div>
                        <div class="col-4">
                          <div class="info-item">
                            <i class="bi bi-star text-success"></i>
                            <div class="small">{{ quiz.max_marks }}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Quiz Attempts History -->
                    <div v-if="quiz.attempts && quiz.attempts.length > 0" class="mb-3">
                      <h6 class="small text-muted mb-2">Previous Attempts:</h6>
                      <div class="attempts-list">
                        <div
                          v-for="(attempt, index) in quiz.attempts.slice(0, 3)"
                          :key="attempt.id"
                          class="attempt-item d-flex justify-content-between align-items-center"
                        >
                          <span class="small">Attempt {{ index + 1 }}</span>
                          <div>
                            <span class="badge" :class="getScoreClass(attempt.score_percentage)">
                              {{ attempt.score_percentage }}%
                            </span>
                            <button
                              class="btn btn-link btn-sm p-0 ms-2"
                              @click="viewResult(quiz.id, attempt.id)"
                              title="View Result"
                            >
                              <i class="bi bi-eye"></i>
                            </button>
                          </div>
                        </div>
                        <div v-if="quiz.attempts.length > 3" class="text-center mt-2">
                          <button
                            class="btn btn-link btn-sm"
                            @click="viewAllAttempts(quiz.id)"
                          >
                            View all {{ quiz.attempts.length }} attempts
                          </button>
                        </div>
                      </div>
                    </div>

                    <!-- Quiz Actions -->
                    <div class="d-grid gap-2">
                      <button
                        v-if="canTakeQuiz(quiz)"
                        class="btn btn-primary btn-sm"
                        @click="startQuiz(quiz.id)"
                        :disabled="quiz.status === 'in_progress'"
                      >
                        <i class="bi bi-play-circle me-1"></i>
                        {{ getQuizActionText(quiz) }}
                      </button>

                      <button
                        v-else
                        class="btn btn-outline-secondary btn-sm"
                        disabled
                      >
                        <i class="bi bi-lock me-1"></i>
                        Quiz Locked
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-4">
              <i class="bi bi-clipboard-x display-4 text-muted"></i>
              <p class="mt-3 text-muted">No quizzes available in this chapter yet.</p>
            </div>
          </div>
        </div>
      </div>

      <!-- No Chapters State -->
      <div v-else class="text-center py-5">
        <i class="bi bi-book display-1 text-muted"></i>
        <h4 class="mt-3">No chapters found</h4>
        <p class="text-muted">This subject doesn't have any chapters yet.</p>
        <button class="btn btn-primary" @click="$router.push('/subjects')">
          Browse Other Subjects
        </button>
      </div>

      <!-- Quiz Start Confirmation Modal -->
      <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" v-if="showStartModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Start Quiz</h5>
              <button type="button" class="btn-close" @click="showStartModal = false"></button>
            </div>
            <div class="modal-body" v-if="selectedQuiz">
              <div class="alert alert-info">
                <h6><i class="bi bi-info-circle me-2"></i>Quiz Instructions</h6>
                <ul class="mb-0">
                  <li>Total Time: <strong>{{ selectedQuiz.time_duration }} minutes</strong></li>
                  <li>Total Questions: <strong>{{ selectedQuiz.total_questions }}</strong></li>
                  <li>Maximum Marks: <strong>{{ selectedQuiz.max_marks }}</strong></li>
                  <li>Passing Score: <strong>{{ selectedQuiz.passing_score }}%</strong></li>
                  <li>Attempts Allowed: <strong>{{ selectedQuiz.max_attempts }}</strong></li>
                </ul>
              </div>
              <div class="alert alert-warning">
                <strong>Important:</strong> Once you start the quiz, the timer will begin automatically.
                Make sure you have a stable internet connection and enough time to complete it.
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
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'SubjectChapters',
  components: { AppLayout },
  setup () {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const starting = ref(false)
    const subject = ref(null)
    const chapters = ref([])
    const showStartModal = ref(false)
    const selectedQuiz = ref(null)

    const subjectId = computed(() => route.params.id)

    const loadSubjectData = async () => {
      try {
        loading.value = true
        const response = await fetch(`/api/user/subjects/${subjectId.value}/chapters`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          subject.value = data.subject
          chapters.value = data.chapters || []
        } else {
          throw new Error('Failed to load subject data')
        }
      } catch (error) {
        console.error('Error loading subject data:', error)
        notificationStore.error('Failed to load subject data')
        router.push('/subjects')
      } finally {
        loading.value = false
      }
    }

    const startQuiz = (quizId) => {
      const quiz = findQuizById(quizId)
      if (quiz) {
        selectedQuiz.value = quiz
        showStartModal.value = true
      }
    }

    const confirmStartQuiz = async () => {
      if (!selectedQuiz.value) return

      try {
        starting.value = true
        const response = await fetch(`/api/user/quiz/${selectedQuiz.value.id}/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            router.push(`/quiz/${selectedQuiz.value.id}/take`)
          } else {
            throw new Error(data.message || 'Failed to start quiz')
          }
        } else {
          throw new Error('Failed to start quiz')
        }
      } catch (error) {
        console.error('Error starting quiz:', error)
        notificationStore.error(error.message || 'Failed to start quiz')
      } finally {
        starting.value = false
        showStartModal.value = false
      }
    }

    const viewResult = (quizId, attemptId) => {
      router.push(`/quiz/${quizId}/result/${attemptId}`)
    }

    const viewAllAttempts = (quizId) => {
      router.push(`/quiz/${quizId}/attempts`)
    }

    const findQuizById = (quizId) => {
      for (const chapter of chapters.value) {
        if (chapter.quizzes) {
          const quiz = chapter.quizzes.find(q => q.id === quizId)
          if (quiz) return quiz
        }
      }
      return null
    }

    const canTakeQuiz = (quiz) => {
      if (!quiz.max_attempts) return true
      return (quiz.attempts?.length || 0) < quiz.max_attempts
    }

    const getQuizStatusClass = (status) => {
      switch (status) {
        case 'available': return 'bg-success'
        case 'in_progress': return 'bg-warning'
        case 'completed': return 'bg-primary'
        case 'locked': return 'bg-secondary'
        default: return 'bg-light text-dark'
      }
    }

    const getQuizStatusText = (status) => {
      switch (status) {
        case 'available': return 'Available'
        case 'in_progress': return 'In Progress'
        case 'completed': return 'Completed'
        case 'locked': return 'Locked'
        default: return 'Unknown'
      }
    }

    const getQuizActionText = (quiz) => {
      if (quiz.status === 'in_progress') return 'Resume Quiz'
      if (quiz.attempts && quiz.attempts.length > 0) return 'Retake Quiz'
      return 'Start Quiz'
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'bg-success'
      if (score >= 75) return 'bg-primary'
      if (score >= 60) return 'bg-warning'
      return 'bg-danger'
    }

    onMounted(() => {
      loadSubjectData()
    })

    return {
      loading,
      starting,
      subject,
      chapters,
      showStartModal,
      selectedQuiz,
      startQuiz,
      confirmStartQuiz,
      viewResult,
      viewAllAttempts,
      canTakeQuiz,
      getQuizStatusClass,
      getQuizStatusText,
      getQuizActionText,
      getScoreClass
    }
  }
}
</script>

<style scoped>
.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.chapter-card {
  border: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
}

.quiz-card {
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.quiz-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.progress-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: conic-gradient(
    #ffffff 0deg,
    #ffffff var(--progress, 0deg),
    rgba(255, 255, 255, 0.3) var(--progress, 0deg)
  );
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.progress-circle::before {
  content: '';
  width: 65px;
  height: 65px;
  border-radius: 50%;
  background: #007bff;
  position: absolute;
}

.progress-text {
  position: relative;
  z-index: 1;
  text-align: center;
  color: white;
}

.info-item {
  text-align: center;
}

.info-item i {
  font-size: 1.2rem;
  margin-bottom: 2px;
}

.attempts-list {
  max-height: 120px;
  overflow-y: auto;
}

.attempt-item {
  padding: 4px 0;
  border-bottom: 1px solid #f8f9fa;
}

.attempt-item:last-child {
  border-bottom: none;
}

.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 15px;
  }

  .subject-stats {
    margin-top: 2rem;
  }

  .progress-circle {
    width: 60px;
    height: 60px;
  }

  .progress-circle::before {
    width: 50px;
    height: 50px;
  }
}
</style>
