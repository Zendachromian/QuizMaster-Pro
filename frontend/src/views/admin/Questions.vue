<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <nav aria-label="breadcrumb">
                <ol class="breadcrumb">
                  <li class="breadcrumb-item">
                    <router-link to="/admin/subjects" class="text-decoration-none">
                      Subjects
                    </router-link>
                  </li>
                  <li class="breadcrumb-item">
                    <a href="#" class="text-decoration-none">{{ quiz?.chapter_name }}</a>
                  </li>
                  <li class="breadcrumb-item">
                    <a href="#" @click.prevent="goToQuizzes" class="text-decoration-none">Quizzes</a>
                  </li>
                  <li class="breadcrumb-item active">{{ quiz?.title }}</li>
                </ol>
              </nav>
              <h2 class="mb-0">
                <i class="bi bi-question-circle-fill me-2 text-warning"></i>
                Questions Management
              </h2>
              <p class="text-muted mb-0">Manage questions for {{ quiz?.title }}</p>
            </div>
            <button
              class="btn btn-primary"
              @click="openCreateModal"
            >
              <i class="bi bi-plus-lg me-1"></i>
              Add Question
            </button>
          </div>
        </div>
      </div>

      <!-- Quiz Info Card -->
      <div class="row mb-4" v-if="quiz">
        <div class="col-12">
          <div class="card border-0 shadow-sm bg-light">
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <h5 class="mb-1">{{ quiz.title }}</h5>
                  <p class="text-muted mb-0">{{ quiz.description || 'No description provided' }}</p>
                  <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>{{ quiz.time_duration }} minutes
                    <i class="bi bi-trophy ms-3 me-1"></i>{{ quiz.passing_score }}% to pass
                  </small>
                </div>
                <div class="col-md-4 text-md-end">
                  <div class="d-flex justify-content-md-end gap-3">
                    <div class="text-center">
                      <h4 class="mb-0 text-warning">{{ questions.length }}</h4>
                      <small class="text-muted">Questions</small>
                    </div>
                    <div class="text-center">
                      <h4 class="mb-0 text-success">{{ totalMarks }}</h4>
                      <small class="text-muted">Total Marks</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Questions List -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-light">
          <div class="d-flex justify-content-between align-items-center">
            <h5 class="mb-0">
              <i class="bi bi-list-ol me-2"></i>
              Questions List
            </h5>
            <div v-if="questions.length > 0" class="text-muted">
              <small>{{ questions.length }} question(s) • {{ totalMarks }} mark(s)</small>
            </div>
          </div>
        </div>
        <div class="card-body">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading questions...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="questions.length === 0" class="text-center py-5">
            <i class="bi bi-question-circle display-1 text-muted mb-3"></i>
            <h5 class="text-muted">No questions found</h5>
            <p class="text-muted">Create your first question for this quiz.</p>
            <button class="btn btn-primary" @click="openCreateModal">
              <i class="bi bi-plus-lg me-1"></i>
              Add Question
            </button>
          </div>

          <!-- Questions List -->
          <div v-else class="accordion" id="questionsAccordion">
            <div v-for="(question, index) in questions" :key="question.id" class="accordion-item mb-3">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed"
                  type="button"
                  data-bs-toggle="collapse"
                  :data-bs-target="'#collapse' + question.id"
                >
                  <div class="d-flex justify-content-between align-items-center w-100 me-3">
                    <div>
                      <strong>Question {{ index + 1 }}</strong>
                      <span class="ms-2 text-muted">{{ truncateText(question.question_text, 60) }}</span>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                      <span class="badge bg-primary">{{ question.marks }} mark(s)</span>
                      <span class="badge bg-success">{{ question.correct_option }}</span>
                    </div>
                  </div>
                </button>
              </h2>
              <div
                :id="'collapse' + question.id"
                class="accordion-collapse collapse"
                data-bs-parent="#questionsAccordion"
              >
                <div class="accordion-body">
                  <div class="row">
                    <div class="col-md-8">
                      <!-- Question Text -->
                      <div class="mb-3">
                        <h6 class="text-primary">Question:</h6>
                        <p class="mb-0">{{ question.question_text }}</p>
                      </div>

                      <!-- Options -->
                      <div class="mb-3">
                        <h6 class="text-primary">Options:</h6>
                        <div class="row g-2">
                          <div class="col-sm-6">
                            <div class="d-flex align-items-center">
                              <span class="badge me-2" :class="question.correct_option === 'A' ? 'bg-success' : 'bg-light text-dark'">A</span>
                              <span>{{ question.option_a }}</span>
                            </div>
                          </div>
                          <div class="col-sm-6">
                            <div class="d-flex align-items-center">
                              <span class="badge me-2" :class="question.correct_option === 'B' ? 'bg-success' : 'bg-light text-dark'">B</span>
                              <span>{{ question.option_b }}</span>
                            </div>
                          </div>
                          <div class="col-sm-6">
                            <div class="d-flex align-items-center">
                              <span class="badge me-2" :class="question.correct_option === 'C' ? 'bg-success' : 'bg-light text-dark'">C</span>
                              <span>{{ question.option_c }}</span>
                            </div>
                          </div>
                          <div class="col-sm-6">
                            <div class="d-flex align-items-center">
                              <span class="badge me-2" :class="question.correct_option === 'D' ? 'bg-success' : 'bg-light text-dark'">D</span>
                              <span>{{ question.option_d }}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- Explanation -->
                      <div v-if="question.explanation" class="mb-3">
                        <h6 class="text-primary">Explanation:</h6>
                        <p class="mb-0 text-muted">{{ question.explanation }}</p>
                      </div>
                    </div>

                    <div class="col-md-4">
                      <div class="card bg-light">
                        <div class="card-body">
                          <div class="text-center mb-3">
                            <div class="h4 text-success mb-1">{{ question.correct_option }}</div>
                            <small class="text-muted">Correct Answer</small>
                          </div>
                          <div class="text-center mb-3">
                            <div class="h4 text-primary mb-1">{{ question.marks }}</div>
                            <small class="text-muted">Mark(s)</small>
                          </div>
                          <div class="d-grid gap-2">
                            <button class="btn btn-sm btn-outline-primary" @click="editQuestion(question)">
                              <i class="bi bi-pencil me-1"></i>Edit
                            </button>
                            <button class="btn btn-sm btn-outline-danger" @click="confirmDelete(question)">
                              <i class="bi bi-trash me-1"></i>Delete
                            </button>
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
      </div>

      <!-- Create/Edit Question Modal -->
      <div class="modal fade" id="questionModal" tabindex="-1">
        <div class="modal-dialog modal-xl">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {{ editingQuestion ? 'Edit Question' : 'Create New Question' }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form @submit.prevent="saveQuestion">
              <div class="modal-body">
                <div class="row">
                  <div class="col-12">
                    <div class="mb-3">
                      <label for="questionText" class="form-label">Question Text *</label>
                      <textarea
                        id="questionText"
                        v-model="form.question_text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.question_text }"
                        rows="3"
                        placeholder="Enter the question text"
                        required
                      ></textarea>
                      <div v-if="errors.question_text" class="invalid-feedback">
                        {{ errors.question_text }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="optionA" class="form-label">Option A *</label>
                      <input
                        id="optionA"
                        v-model="form.option_a"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.option_a }"
                        placeholder="Enter option A"
                        required
                      >
                      <div v-if="errors.option_a" class="invalid-feedback">
                        {{ errors.option_a }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="optionB" class="form-label">Option B *</label>
                      <input
                        id="optionB"
                        v-model="form.option_b"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.option_b }"
                        placeholder="Enter option B"
                        required
                      >
                      <div v-if="errors.option_b" class="invalid-feedback">
                        {{ errors.option_b }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="optionC" class="form-label">Option C *</label>
                      <input
                        id="optionC"
                        v-model="form.option_c"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.option_c }"
                        placeholder="Enter option C"
                        required
                      >
                      <div v-if="errors.option_c" class="invalid-feedback">
                        {{ errors.option_c }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="optionD" class="form-label">Option D *</label>
                      <input
                        id="optionD"
                        v-model="form.option_d"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.option_d }"
                        placeholder="Enter option D"
                        required
                      >
                      <div v-if="errors.option_d" class="invalid-feedback">
                        {{ errors.option_d }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="correctOption" class="form-label">Correct Answer *</label>
                      <select
                        id="correctOption"
                        v-model="form.correct_option"
                        class="form-select"
                        :class="{ 'is-invalid': errors.correct_option }"
                        required
                      >
                        <option value="">Select correct option</option>
                        <option value="A">A</option>
                        <option value="B">B</option>
                        <option value="C">C</option>
                        <option value="D">D</option>
                      </select>
                      <div v-if="errors.correct_option" class="invalid-feedback">
                        {{ errors.correct_option }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="marks" class="form-label">Marks</label>
                      <input
                        id="marks"
                        v-model="form.marks"
                        type="number"
                        class="form-control"
                        :class="{ 'is-invalid': errors.marks }"
                        min="1"
                        max="10"
                        placeholder="1"
                      >
                      <div v-if="errors.marks" class="invalid-feedback">
                        {{ errors.marks }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="row">
                  <div class="col-12">
                    <div class="mb-3">
                      <label for="explanation" class="form-label">Explanation (Optional)</label>
                      <textarea
                        id="explanation"
                        v-model="form.explanation"
                        class="form-control"
                        :class="{ 'is-invalid': errors.explanation }"
                        rows="2"
                        placeholder="Provide an explanation for the correct answer"
                      ></textarea>
                      <div v-if="errors.explanation" class="invalid-feedback">
                        {{ errors.explanation }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingQuestion ? 'Update' : 'Create' }} Question
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div class="modal fade" id="deleteModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">Confirm Delete</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
              <p>Are you sure you want to delete this question?</p>
              <div class="bg-light p-3 rounded">
                <small class="text-muted">Question preview:</small>
                <p class="mb-0 mt-1"><strong>{{ truncateText(questionToDelete?.question_text, 100) }}</strong></p>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" @click="deleteQuestion" :disabled="deleting">
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                Delete Question
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import { toast } from '@/utils/toast'
import { useAdminStore } from '@/stores/admin'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'AdminQuestions',
  components: { AppLayout },
  setup () {
    const route = useRoute()
    const router = useRouter()
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const quiz = ref(null)
    const questions = ref([])
    const editingQuestion = ref(null)
    const questionToDelete = ref(null)

    // Form data
    const form = ref({
      question_text: '',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      correct_option: '',
      explanation: '',
      marks: 1
    })

    const errors = ref({})

    // Modals
    let questionModal = null
    let deleteModal = null

    // Computed
    const totalMarks = computed(() => {
      return questions.value.reduce((sum, question) => sum + (question.marks || 1), 0)
    })

    // Methods
    const loadQuestions = async () => {
      try {
        loading.value = true
        const quizId = route.params.id
        await adminStore.fetchQuestions(quizId)

        // Get data from store after successful fetch
        quiz.value = adminStore.quizInfo
        questions.value = adminStore.questions || []
      } catch (error) {
        toast.error('Failed to load questions')
        console.error('Error loading questions:', error)
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      editingQuestion.value = null
      form.value = {
        question_text: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_option: '',
        explanation: '',
        marks: 1
      }
      errors.value = {}
      questionModal.show()
    }

    const editQuestion = (question) => {
      editingQuestion.value = question
      form.value = {
        question_text: question.question_text,
        option_a: question.option_a,
        option_b: question.option_b,
        option_c: question.option_c,
        option_d: question.option_d,
        correct_option: question.correct_option,
        explanation: question.explanation || '',
        marks: question.marks || 1
      }
      errors.value = {}
      questionModal.show()
    }

    const saveQuestion = async () => {
      try {
        saving.value = true
        errors.value = {}

        let result
        if (editingQuestion.value) {
          // Update question - we need to add this to the admin store
          result = await adminStore.updateQuestion(editingQuestion.value.id, form.value)
        } else {
          const quizId = route.params.id
          result = await adminStore.createQuestion(quizId, form.value)
        }

        if (result.success) {
          toast.success(result.message)
          questionModal.hide()
          await loadQuestions()
        } else {
          toast.error(result.message)
          if (result.errors) {
            errors.value = result.errors
          }
        }
      } catch (error) {
        toast.error('An error occurred while saving the question')
      } finally {
        saving.value = false
      }
    }

    const confirmDelete = (question) => {
      questionToDelete.value = question
      deleteModal.show()
    }

    const deleteQuestion = async () => {
      try {
        deleting.value = true
        const result = await adminStore.deleteQuestion(questionToDelete.value.id)

        if (result.success) {
          toast.success(result.message)
          deleteModal.hide()
          await loadQuestions()
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('Failed to delete question')
      } finally {
        deleting.value = false
      }
    }

    const goToQuizzes = () => {
      // Navigate back to quizzes - you'll need to determine the chapter ID
      router.push('/admin/subjects')
    }

    const truncateText = (text, maxLength) => {
      if (!text) return ''
      if (text.length <= maxLength) return text
      return text.substring(0, maxLength) + '...'
    }

    // Lifecycle
    onMounted(async () => {
      await loadQuestions()

      // Initialize modals
      questionModal = new Modal(document.getElementById('questionModal'))
      deleteModal = new Modal(document.getElementById('deleteModal'))
    })

    return {
      // State
      loading,
      saving,
      deleting,
      quiz,
      questions,
      editingQuestion,
      questionToDelete,
      form,
      errors,

      // Computed
      totalMarks,

      // Methods
      openCreateModal,
      editQuestion,
      saveQuestion,
      confirmDelete,
      deleteQuestion,
      goToQuizzes,
      truncateText
    }
  }
}
</script>

<style scoped>
.accordion-button:not(.collapsed) {
  color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

.accordion-item {
  border: 1px solid rgba(0,0,0,0.125);
  border-radius: 0.375rem !important;
}

.accordion-header button {
  border-radius: 0.375rem !important;
}

.breadcrumb-item a:hover {
  text-decoration: underline !important;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.modal-xl .modal-body {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
