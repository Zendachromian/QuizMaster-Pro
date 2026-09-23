<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-3 text-muted">Loading quiz...</p>
      </div>

      <div v-else>
        <!-- Quiz Header -->
        <div class="card mb-4" v-if="quiz">
          <div class="card-body">
            <div class="row">
              <div class="col-md-8">
                <h3>{{ quiz.title }}</h3>
                <p class="text-muted">{{ quiz.description }}</p>
                <p><strong>Subject:</strong> {{ quiz.chapter?.subject?.name }}</p>
                <p><strong>Chapter:</strong> {{ quiz.chapter?.name }}</p>
              </div>
              <div class="col-md-4 text-end">
                <div class="alert alert-info">
                  <strong>Time Remaining:</strong><br>
                  <span class="h4" :class="timeWarning">{{ formattedTimeLeft }}</span>
                </div>
                <div class="mt-2">
                  <strong>Progress:</strong> {{ answersCount }}/{{ questions.length }}
                </div>
              </div>
            </div>
          </div>
        </div>

    <!-- Questions -->
    <div v-if="currentQuestion" class="card mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Question {{ currentQuestionIndex + 1 }} of {{ questions.length }}</h5>
        <div>
          <span class="badge bg-primary me-2">{{ currentQuestion.marks }} marks</span>
          <button
            class="btn btn-outline-secondary btn-sm"
            @click="toggleBookmark"
            :class="{ 'active': bookmarkedQuestions.has(currentQuestion.id) }"
          >
            <i class="fas" :class="bookmarkedQuestions.has(currentQuestion.id) ? 'fa-bookmark' : 'fa-bookmark-o'"></i>
          </button>
        </div>
      </div>
      <div class="card-body">
        <div class="question-text mb-4">
          <p class="h5">{{ currentQuestion.question_text }}</p>
        </div>

        <div class="options">
          <div
            v-for="option in ['A', 'B', 'C', 'D']"
            :key="option"
            class="form-check mb-3"
          >
            <input
              class="form-check-input"
              type="radio"
              :name="`question_${currentQuestion.id}`"
              :id="`option_${currentQuestion.id}_${option}`"
              :value="option"
              v-model="answers[currentQuestion.id]"
              @change="saveAnswer"
            >
            <label
              class="form-check-label w-100"
              :for="`option_${currentQuestion.id}_${option}`"
              style="cursor: pointer;"
            >
              <strong>{{ option }}.</strong> {{ getOptionText(option) }}
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <button
              class="btn btn-outline-primary me-2"
              @click="previousQuestion"
              :disabled="currentQuestionIndex === 0"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            <button
              class="btn btn-outline-primary"
              @click="nextQuestion"
              :disabled="currentQuestionIndex === questions.length - 1"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
          <div class="col-md-6 text-end">
                        <button
              type="button"
              class="btn btn-warning me-2"
              @click="console.log('🟡 Yellow Submit button clicked!'); showSubmitModal = true"
              :disabled="answersCount === 0"
            >
              <i class="fas fa-paper-plane"></i> Submit Quiz
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Question Navigator -->
    <div class="card">
      <div class="card-header">
        <h6 class="mb-0">Question Navigator</h6>
      </div>
      <div class="card-body">
        <div class="row">
          <div
            v-for="(question, index) in questions"
            :key="question.id"
            class="col-md-1 col-sm-2 col-3 mb-2"
          >
            <button
              class="btn btn-sm w-100"
              :class="getQuestionButtonClass(question, index)"
              @click="goToQuestion(index)"
            >
              {{ index + 1 }}
              <i
                v-if="bookmarkedQuestions.has(question.id)"
                class="fas fa-bookmark ms-1"
              ></i>
            </button>
          </div>
        </div>
        <div class="mt-3">
          <small class="text-muted">
            <span class="badge bg-success me-2">Answered</span>
            <span class="badge bg-warning me-2">Current</span>
            <span class="badge bg-light text-dark me-2">Not Answered</span>
            <span class="badge bg-info">Bookmarked</span>
          </small>
        </div>
      </div>
    </div>

    <!-- Submit Confirmation Modal -->
    <div class="modal fade show" style="display: block; background: rgba(0,0,0,0.5);" tabindex="-1" v-if="showSubmitModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Submit Quiz</h5>
            <button type="button" class="btn-close" @click="showSubmitModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="alert alert-warning">
              <strong>Are you sure you want to submit?</strong>
            </div>
            <div class="row">
              <div class="col-4 text-center">
                <div class="h4 text-success">{{ answersCount }}</div>
                <small>Answered</small>
              </div>
              <div class="col-4 text-center">
                <div class="h4 text-warning">{{ questions.length - answersCount }}</div>
                <small>Not Answered</small>
              </div>
              <div class="col-4 text-center">
                <div class="h4 text-info">{{ bookmarkedQuestions.size }}</div>
                <small>Bookmarked</small>
              </div>
            </div>
            <p class="mt-3 mb-0">
              <strong>Time Remaining:</strong> {{ formattedTimeLeft }}
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showSubmitModal = false">
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-success"
              @click="console.log('🟢 Modal Submit button clicked!'); submitQuiz()"
              :disabled="submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              Submit Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'TakeQuiz',
  components: { AppLayout },
  setup () {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    // Data
    const quiz = ref(null)
    const questions = ref([])
    const attempt = ref(null)
    const currentQuestionIndex = ref(0)
    const answers = ref({})
    const bookmarkedQuestions = ref(new Set())
    const timeLeft = ref(0)
    const timer = ref(null)
    const showSubmitModal = ref(false)
    const submitting = ref(false)
    const loading = ref(true)

    // Local storage helpers
    const getStorageKey = () => {
      const quizId = route.params.id
      const userId = authStore.user?.id
      return `quiz_answers_${userId}_${quizId}`
    }

    const getTimerStorageKey = () => {
      const quizId = route.params.id
      const userId = authStore.user?.id
      return `quiz_timer_${userId}_${quizId}`
    }

    const saveAnswersToStorage = () => {
      try {
        const quizData = {
          answers: answers.value,
          timeLeft: timeLeft.value,
          startTime: Date.now()
        }
        localStorage.setItem(getStorageKey(), JSON.stringify(quizData))
      } catch (error) {
        console.warn('Failed to save answers to localStorage:', error)
      }
    }

    const loadAnswersFromStorage = () => {
      try {
        const saved = localStorage.getItem(getStorageKey())
        if (saved) {
          const parsedData = JSON.parse(saved)

          // Handle both old format (just answers) and new format (with timer)
          if (parsedData.answers) {
            answers.value = { ...parsedData.answers }
            console.log('Loaded answers from localStorage:', parsedData.answers)

            // Restore timer if available
            if (parsedData.timeLeft && parsedData.startTime) {
              const timeElapsed = Math.floor((Date.now() - parsedData.startTime) / 1000)
              const adjustedTimeLeft = parsedData.timeLeft - timeElapsed

              if (adjustedTimeLeft > 0) {
                timeLeft.value = adjustedTimeLeft
                console.log('Restored timer with adjusted time:', adjustedTimeLeft)
              } else {
                console.log('Timer expired during absence, auto-submitting')
                autoSubmit()
              }
            }
          } else {
            // Old format - just answers
            answers.value = { ...parsedData }
            console.log('Loaded answers from localStorage (old format):', parsedData)
          }
        }
      } catch (error) {
        console.warn('Failed to load answers from localStorage:', error)
      }
    }

    const clearAnswersFromStorage = () => {
      try {
        localStorage.removeItem(getStorageKey())
      } catch (error) {
        console.warn('Failed to clear answers from localStorage:', error)
      }
    }

    // Computed
    const currentQuestion = computed(() =>
      questions.value[currentQuestionIndex.value] || null
    )

    const answersCount = computed(() =>
      Object.keys(answers.value).filter(key => answers.value[key]).length
    )

    const formattedTimeLeft = computed(() => {
      const hours = Math.floor(timeLeft.value / 3600)
      const minutes = Math.floor((timeLeft.value % 3600) / 60)
      const seconds = timeLeft.value % 60

      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      }
      return `${minutes}:${seconds.toString().padStart(2, '0')}`
    })

    const timeWarning = computed(() => {
      if (timeLeft.value < 300) return 'text-danger' // 5 minutes
      if (timeLeft.value < 600) return 'text-warning' // 10 minutes
      return 'text-info'
    })

    // Watch for changes in answers and save to localStorage
    watch(answers, () => {
      saveAnswersToStorage()
    }, { deep: true })

    // Methods
    const loadQuiz = async () => {
      try {
        const quizId = route.params.id
        console.log('🎯 Loading quiz with ID:', quizId)

        const response = await fetch(`/api/user/quiz/${quizId}/start`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          console.log('📊 Quiz load response:', data)

          if (data.success) {
            quiz.value = data.quiz
            questions.value = data.questions
            attempt.value = data.attempt

            // Calculate time left
            const durationMinutes = data.time_duration || quiz.value.time_duration

            // Load saved answers and timer from localStorage first
            loadAnswersFromStorage()

            // Only set initial timer if no saved timer was restored
            if (timeLeft.value === 0 && durationMinutes) {
              console.log('⏰ Setting initial timer for', durationMinutes, 'minutes')
              timeLeft.value = durationMinutes * 60 // Convert to seconds
            }

            // Start the timer
            if (timeLeft.value > 0) {
              console.log('▶️ Starting timer with', timeLeft.value, 'seconds remaining')
              startTimer()
            }
          } else {
            throw new Error(data.error || 'Failed to start quiz')
          }
        } else {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Failed to start quiz')
        }
      } catch (error) {
        console.error('Error loading quiz:', error)
        notificationStore.error(error.message || 'Error loading quiz')
        router.push('/quiz')
      } finally {
        loading.value = false
      }
    }

    const startTimer = () => {
      timer.value = setInterval(() => {
        timeLeft.value--

        // Auto-save answers every 30 seconds
        if (timeLeft.value % 30 === 0) {
          autoSaveProgress()
        }

        if (timeLeft.value <= 0) {
          clearInterval(timer.value)
          autoSubmit()
        }
      }, 1000)
    }

    const autoSaveProgress = async () => {
      // Save to localStorage first
      saveAnswersToStorage()

      // Save all current answers to server
      for (const questionId in answers.value) {
        if (answers.value[questionId]) {
          try {
            await fetch(`/api/user/attempt/${attempt.value.id}/save-answer`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${authStore.token}`
              },
              body: JSON.stringify({
                question_id: parseInt(questionId),
                selected_option: answers.value[questionId]
              })
            })
          } catch (error) {
            console.error('Auto-save error:', error)
          }
        }
      }
    }

    const saveAnswer = async () => {
      if (!currentQuestion.value || !answers.value[currentQuestion.value.id]) return

      // Save to localStorage immediately
      saveAnswersToStorage()

      try {
        const response = await fetch(`/api/user/attempt/${attempt.value.id}/save-answer`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          },
          body: JSON.stringify({
            question_id: currentQuestion.value.id,
            selected_option: answers.value[currentQuestion.value.id]
          })
        })

        if (!response.ok) {
          throw new Error('Failed to save answer')
        }
      } catch (error) {
        console.error('Error saving answer:', error)
      }
    }

    const nextQuestion = () => {
      if (currentQuestionIndex.value < questions.value.length - 1) {
        currentQuestionIndex.value++
      }
    }

    const previousQuestion = () => {
      if (currentQuestionIndex.value > 0) {
        currentQuestionIndex.value--
      }
    }

    const goToQuestion = (index) => {
      currentQuestionIndex.value = index
    }

    const toggleBookmark = () => {
      const questionId = currentQuestion.value.id
      if (bookmarkedQuestions.value.has(questionId)) {
        bookmarkedQuestions.value.delete(questionId)
      } else {
        bookmarkedQuestions.value.add(questionId)
      }
    }

    const getOptionText = (option) => {
      const question = currentQuestion.value
      if (!question) return ''

      switch (option) {
        case 'A': return question.option_a
        case 'B': return question.option_b
        case 'C': return question.option_c
        case 'D': return question.option_d
        default: return ''
      }
    }

    const getQuestionButtonClass = (question, index) => {
      const classes = []

      if (index === currentQuestionIndex.value) {
        classes.push('btn-warning')
      } else if (answers.value[question.id]) {
        classes.push('btn-success')
      } else {
        classes.push('btn-outline-secondary')
      }

      return classes.join(' ')
    }

    const submitQuiz = async () => {
      console.log('🚀 Starting quiz submission for quiz ID:', route.params.id)
      console.log('📝 Current attempt object:', attempt.value)
      console.log('📊 Current answers being submitted:', answers.value)
      console.log('🔑 Auth token available:', !!authStore.token)
      console.log('👤 Current user:', authStore.user)
      submitting.value = true

      try {
        console.log('💾 Auto-saving progress before submit...')
        // Save all current answers before submitting
        await autoSaveProgress()

        if (!attempt.value || !attempt.value.id) {
          throw new Error('No valid attempt found for this quiz')
        }

        console.log('🌐 Making submit API call for attempt ID:', attempt.value.id)
        console.log('🔗 Full submit URL:', `/api/user/attempt/${attempt.value.id}/submit`)

        const response = await fetch(`/api/user/attempt/${attempt.value.id}/submit`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          }
        })

        console.log('📡 Submit response status:', response.status)
        console.log('📡 Submit response headers:', Object.fromEntries(response.headers.entries()))

        const responseText = await response.text()
        console.log('📡 Raw response text:', responseText)

        let data
        try {
          data = JSON.parse(responseText)
        } catch (parseError) {
          console.error('❌ Failed to parse response JSON:', parseError)
          console.error('❌ Response text was:', responseText)
          throw new Error('Invalid response from server')
        }

        console.log('📊 Submit response data:', data)

        if (response.ok) {
          if (data.success) {
            // Clear saved answers from localStorage after successful submission
            clearAnswersFromStorage()

            console.log('✅ Quiz submitted successfully, navigating to dashboard...')

            // Small delay to ensure backend processing is complete
            await new Promise(resolve => setTimeout(resolve, 500))

            // Navigate to dashboard and show success message
            router.push('/dashboard')

            // Show success notification after navigation
            setTimeout(() => {
              notificationStore.success('Quiz submitted successfully! Check your results in Quiz History.')
            }, 100)
          } else {
            throw new Error(data.error || data.message || 'Failed to submit quiz')
          }
        } else {
          console.error('❌ Submit error response:', data)
          throw new Error(data.error || data.message || `Server error: ${response.status}`)
        }
      } catch (error) {
        console.error('💥 Error submitting quiz:', error)
        console.error('💥 Error stack:', error.stack)
        notificationStore.error(error.message || 'Error submitting quiz')
      } finally {
        submitting.value = false
        showSubmitModal.value = false
      }
    }

    const autoSubmit = async () => {
      notificationStore.warning('Time up! Quiz submitted automatically.')
      await submitQuiz()
    }

    // Lifecycle
    onMounted(() => {
      loadQuiz()
    })

    onUnmounted(() => {
      if (timer.value) {
        clearInterval(timer.value)
      }
    })

    return {
      // Data
      quiz,
      questions,
      attempt,
      currentQuestionIndex,
      answers,
      bookmarkedQuestions,
      timeLeft,
      showSubmitModal,
      submitting,
      loading,

      // Computed
      currentQuestion,
      answersCount,
      formattedTimeLeft,
      timeWarning,

      // Methods
      nextQuestion,
      previousQuestion,
      goToQuestion,
      toggleBookmark,
      getOptionText,
      getQuestionButtonClass,
      saveAnswer,
      submitQuiz,
      autoSaveProgress
    }
  }
}
</script>

<style scoped>
.form-check-input:checked + .form-check-label {
  background-color: rgba(13, 110, 253, 0.1);
  border-radius: 5px;
  padding: 10px;
}

.form-check-label {
  padding: 10px;
  border-radius: 5px;
  transition: background-color 0.2s;
}

.form-check-label:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.question-text {
  line-height: 1.6;
}

.modal {
  display: block;
  background-color: rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .container {
    padding: 10px;
  }

  .card-body {
    padding: 15px;
  }
}
</style>
