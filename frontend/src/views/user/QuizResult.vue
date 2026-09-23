<template>
  <div class="container mt-4">
    <div v-if="loading" class="text-center">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="result">
      <!-- Result Summary Card -->
      <div class="card mb-4">
        <div class="card-header" :class="headerClass">
          <div class="row align-items-center">
            <div class="col-md-8">
              <h3 class="mb-0">
                <i :class="resultIcon" class="me-2"></i>
                {{ result.attempt.result }}
              </h3>
              <p class="mb-0 mt-2">{{ result.quiz.title }}</p>
            </div>
            <div class="col-md-4 text-end">
              <div class="h2 mb-0">{{ result.attempt.score_percentage }}%</div>
              <small>{{ result.attempt.obtained_marks }}/{{ result.attempt.total_marks }} marks</small>
            </div>
          </div>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-3 text-center">
              <div class="h4 text-success">{{ result.attempt.correct_answers }}</div>
              <small class="text-muted">Correct</small>
            </div>
            <div class="col-md-3 text-center">
              <div class="h4 text-danger">{{ result.attempt.wrong_answers || (result.attempt.total_questions - result.attempt.correct_answers) }}</div>
              <small class="text-muted">Wrong</small>
            </div>
            <div class="col-md-3 text-center">
              <div class="h4 text-info">{{ result.attempt.time_spent || result.attempt.time_taken || 0 }}s</div>
              <small class="text-muted">Time Taken</small>
            </div>
            <div class="col-md-3 text-center">
              <div class="h4 text-warning">{{ result.attempt.total_questions }}</div>
              <small class="text-muted">Total Questions</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Chart -->
      <div class="card mb-4">
        <div class="card-header">
          <h5 class="mb-0">Performance Breakdown</h5>
        </div>
        <div class="card-body">
          <canvas ref="chartCanvas" width="400" height="200"></canvas>
        </div>
      </div>

      <!-- Detailed Results -->
      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Detailed Results</h5>
          <div class="btn-group btn-group-sm" role="group">
            <input type="radio" class="btn-check" id="all" v-model="filter" value="all">
            <label class="btn btn-outline-primary" for="all">All</label>

            <input type="radio" class="btn-check" id="correct" v-model="filter" value="correct">
            <label class="btn btn-outline-success" for="correct">Correct</label>

            <input type="radio" class="btn-check" id="wrong" v-model="filter" value="wrong">
            <label class="btn btn-outline-danger" for="wrong">Wrong</label>
          </div>
        </div>
        <div class="card-body">
          <div v-if="filteredAnswers.length === 0" class="text-center text-muted py-4">
            No questions match the selected filter.
          </div>

          <div v-else class="accordion" id="questionsAccordion">
            <div
              v-for="(answer, index) in filteredAnswers"
              :key="index"
              class="accordion-item"
            >
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed d-flex justify-content-between align-items-center"
                  type="button"
                  :data-bs-target="`#question-${index}`"
                  @click="toggleAccordion(index)"
                >
                  <div class="flex-grow-1">
                    <span class="me-3">
                      <i
                        :class="answer.is_correct ? 'fas fa-check-circle text-success' : 'fas fa-times-circle text-danger'"
                      ></i>
                    </span>
                    <span>Question {{ getQuestionNumber(answer) }}</span>
                    <span class="badge ms-2" :class="answer.is_correct ? 'bg-success' : 'bg-danger'">
                      {{ answer.marks_obtained }}/{{ answer.marks }} marks
                    </span>
                  </div>
                </button>
              </h2>
              <div
                :id="`question-${index}`"
                class="accordion-collapse collapse"
                :class="{ show: expandedQuestions.has(index) }"
              >
                <div class="accordion-body">
                  <div class="question-content">
                    <h6>{{ answer.question_text }}</h6>

                    <div class="options mt-3">
                      <div
                        v-for="option in ['A', 'B', 'C', 'D']"
                        :key="option"
                        class="option-row p-2 mb-2 rounded"
                        :class="getOptionClass(answer, option)"
                      >
                        <strong>{{ option }}.</strong> {{ answer.options[option] }}
                        <span class="float-end">
                          <i v-if="option === answer.correct_option" class="fas fa-check text-success"></i>
                          <i v-if="option === answer.selected_option && option !== answer.correct_option"
                             class="fas fa-times text-danger"></i>
                        </span>
                      </div>
                    </div>

                    <div class="mt-3">
                      <div class="row">
                        <div class="col-md-6">
                          <small class="text-muted">
                            <strong>Your Answer:</strong>
                            <span :class="answer.is_correct ? 'text-success' : 'text-danger'">
                              {{ answer.selected_option || 'Not answered' }}
                            </span>
                          </small>
                        </div>
                        <div class="col-md-6">
                          <small class="text-muted">
                            <strong>Correct Answer:</strong>
                            <span class="text-success">{{ answer.correct_option }}</span>
                          </small>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="card">
        <div class="card-body text-center">
          <button
            class="btn btn-primary me-3"
            @click="$router.push('/dashboard')"
          >
            <i class="fas fa-home"></i> Back to Dashboard
          </button>
          <button
            class="btn btn-outline-primary me-3"
            @click="$router.push('/history')"
          >
            <i class="fas fa-history"></i> View History
          </button>
          <button
            class="btn btn-outline-success"
            @click="retakeQuiz"
            v-if="canRetake"
          >
            <i class="fas fa-redo"></i> Retake Quiz
          </button>
        </div>
      </div>
    </div>

    <div v-else class="alert alert-danger">
      <h4>Error</h4>
      <p>Unable to load quiz results. Please try again later.</p>
      <button class="btn btn-primary" @click="$router.push('/dashboard')">
        Back to Dashboard
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/utils/axios'
import { showToast } from '@/utils/toast'
import Chart from 'chart.js/auto'

export default {
  name: 'QuizResult',
  setup () {
    const route = useRoute()
    const router = useRouter()

    // Data
    const result = ref(null)
    const loading = ref(true)
    const filter = ref('all')
    const expandedQuestions = ref(new Set())
    const chartCanvas = ref(null)
    const chart = ref(null)

    // Computed
    const headerClass = computed(() => {
      if (!result.value) return 'bg-light'

      const percentage = result.value.attempt.score_percentage
      if (percentage >= 80) return 'bg-success text-white'
      if (percentage >= 60) return 'bg-warning text-white'
      return 'bg-danger text-white'
    })

    const resultIcon = computed(() => {
      if (!result.value) return 'fas fa-question'

      const percentage = result.value.attempt.score_percentage
      if (percentage >= 80) return 'fas fa-trophy'
      if (percentage >= 60) return 'fas fa-medal'
      return 'fas fa-times-circle'
    })

    const filteredAnswers = computed(() => {
      if (!result.value || !result.value.answers) return []

      switch (filter.value) {
        case 'correct':
          return result.value.answers.filter(a => a.is_correct)
        case 'wrong':
          return result.value.answers.filter(a => !a.is_correct)
        default:
          return result.value.answers
      }
    })

    const canRetake = computed(() => {
      return result.value && result.value.quiz.allow_retake
    })

    // Methods
    const loadResult = async () => {
      try {
        const quizId = route.params.id
        console.log('Loading result for quiz ID:', quizId)

        const response = await axios.get(`/api/user/quiz/${quizId}/result`)

        console.log('Quiz result response:', response.data)
        if (response.data.success) {
          result.value = response.data
          await nextTick()
          createChart()
        } else {
          console.error('API returned error:', response.data.error)
          throw new Error(response.data.error || 'Failed to load quiz result')
        }
      } catch (error) {
        console.error('Error loading result:', error)

        // Handle specific error cases - redirect to dashboard instead of showing error
        if (error.response?.status === 404) {
          showToast('No completed quiz attempts found. Redirecting to dashboard...', 'info')
          setTimeout(() => {
            router.push('/dashboard')
          }, 1500)
        } else {
          showToast('Unable to load quiz results. Redirecting to dashboard...', 'warning')
          setTimeout(() => {
            router.push('/dashboard')
          }, 1500)
        }
      } finally {
        loading.value = false
      }
    }

    const createChart = () => {
      if (!chartCanvas.value || !result.value) return

      const ctx = chartCanvas.value.getContext('2d')
      const attempt = result.value.attempt

      const correctAnswers = attempt.correct_answers
      const wrongAnswers = (attempt.wrong_answers || (attempt.total_questions - correctAnswers))

      chart.value = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Correct', 'Wrong'],
          datasets: [{
            data: [correctAnswers, wrongAnswers],
            backgroundColor: [
              '#28a745',
              '#dc3545'
            ],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

    const toggleAccordion = (index) => {
      if (expandedQuestions.value.has(index)) {
        expandedQuestions.value.delete(index)
      } else {
        expandedQuestions.value.add(index)
      }
    }

    const getQuestionNumber = (answer) => {
      if (!result.value || !result.value.answers) return 1
      return result.value.answers.indexOf(answer) + 1
    }

    const getOptionClass = (answer, option) => {
      const classes = []

      if (option === answer.correct_option) {
        classes.push('bg-success', 'bg-opacity-25', 'border-success')
      } else if (option === answer.selected_option && option !== answer.correct_option) {
        classes.push('bg-danger', 'bg-opacity-25', 'border-danger')
      } else {
        classes.push('bg-light')
      }

      return classes.join(' ')
    }

    const retakeQuiz = () => {
      router.push(`/quiz/${route.params.id}/take`)
    }

    // Lifecycle
    onMounted(() => {
      loadResult()
    })

    return {
      // Data
      result,
      loading,
      filter,
      expandedQuestions,
      chartCanvas,

      // Computed
      headerClass,
      resultIcon,
      filteredAnswers,
      canRetake,

      // Methods
      toggleAccordion,
      getQuestionNumber,
      getOptionClass,
      retakeQuiz
    }
  }
}
</script>

<style scoped>
.option-row {
  border: 1px solid #dee2e6;
  transition: all 0.2s;
}

.option-row:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.accordion-button:not(.collapsed) {
  background-color: #f8f9fa;
  color: #495057;
}

.accordion-button:focus {
  box-shadow: none;
  border-color: #dee2e6;
}

.question-content {
  line-height: 1.6;
}

@media (max-width: 768px) {
  .container {
    padding: 10px;
  }

  .card-body {
    padding: 15px;
  }

  .row > div {
    margin-bottom: 15px;
  }
}
</style>
