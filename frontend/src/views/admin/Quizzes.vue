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
                    <router-link :to="`/admin/subjects/${chapter?.subject_id}/chapters`" class="text-decoration-none">
                      {{ chapter?.subject_name }}
                    </router-link>
                  </li>
                  <li class="breadcrumb-item active">{{ chapter?.name }}</li>
                </ol>
              </nav>
              <h2 class="mb-0">
                <i class="bi bi-patch-question-fill me-2 text-success"></i>
                Quiz Management
              </h2>
              <p class="text-muted mb-0">Manage quizzes for {{ chapter?.name }}</p>
            </div>
            <button
              class="btn btn-primary"
              @click="openCreateModal"
            >
              <i class="bi bi-plus-lg me-1"></i>
              Create Quiz
            </button>
          </div>
        </div>
      </div>

      <!-- Chapter Info Card -->
      <div class="row mb-4" v-if="chapter">
        <div class="col-12">
          <div class="card border-0 shadow-sm bg-light">
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <h5 class="mb-1">{{ chapter.name }}</h5>
                  <p class="text-muted mb-0">{{ chapter.description || 'No description provided' }}</p>
                </div>
                <div class="col-md-4 text-md-end">
                  <div class="d-flex justify-content-md-end gap-3">
                    <div class="text-center">
                      <h4 class="mb-0 text-success">{{ quizzes?.length || 0 }}</h4>
                      <small class="text-muted">Quizzes</small>
                    </div>
                    <div class="text-center">
                      <h4 class="mb-0 text-info">{{ totalQuestions }}</h4>
                      <small class="text-muted">Questions</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quizzes List -->
      <div class="card border-0 shadow-sm no-hover-effect">
        <div class="card-header bg-light no-hover-effect">
          <h5 class="mb-0 no-hover-effect">
            <i class="bi bi-list-check me-2"></i>
            Quizzes List
          </h5>
        </div>
        <div class="card-body">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading quizzes...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="!quizzes || quizzes.length === 0" class="text-center py-5">
            <i class="bi bi-patch-question display-1 text-muted mb-3"></i>
            <h5 class="text-muted">No quizzes found</h5>
            <p class="text-muted">Create your first quiz for this chapter.</p>
            <button class="btn btn-primary" @click="openCreateModal">
              <i class="bi bi-plus-lg me-1"></i>
              Create Quiz
            </button>
          </div>

          <!-- Quizzes Grid -->
          <div v-else class="row">
            <div v-for="quiz in quizzes" :key="quiz.id" class="col-lg-6 col-xl-4 mb-4">
              <div class="card h-100 border-0 shadow-sm quiz-card">
                <div class="card-header d-flex justify-content-between align-items-center"
                     :class="getQuizHeaderClass(quiz)">
                  <div>
                    <h6 class="mb-0 text-white">
                      <i class="bi bi-patch-question me-1"></i>
                      Quiz
                    </h6>
                  </div>
                  <div class="dropdown">
                    <button
                      class="btn btn-sm btn-outline-light"
                      type="button"
                      :id="'dropdown-' + quiz.id"
                      data-bs-toggle="dropdown"
                    >
                      <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <a class="dropdown-item" href="#" @click.prevent="manageQuestions(quiz)">
                          <i class="bi bi-list-ol me-2"></i>Manage Questions
                        </a>
                      </li>
                      <li>
                        <a class="dropdown-item" href="#" @click.prevent="viewStats(quiz)">
                          <i class="bi bi-bar-chart me-2"></i>View Statistics
                        </a>
                      </li>
                      <li>
                        <a class="dropdown-item" href="#" @click.prevent="editQuiz(quiz)">
                          <i class="bi bi-pencil me-2"></i>Edit Quiz
                        </a>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <a class="dropdown-item text-danger" href="#" @click.prevent="confirmDelete(quiz)">
                          <i class="bi bi-trash me-2"></i>Delete Quiz
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="card-body">
                  <h5 class="card-title">{{ quiz.title }}</h5>
                  <p class="card-text text-muted small">
                    {{ quiz.description || 'No description provided' }}
                  </p>

                  <!-- Quiz Info -->
                  <div class="row g-2 mb-3">
                    <div class="col-6">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-clock text-primary me-1"></i>
                        <small>{{ quiz.time_duration }} min</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-arrow-repeat text-info me-1"></i>
                        <small>{{ quiz.max_attempts }} attempts</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-trophy text-warning me-1"></i>
                        <small>{{ quiz.passing_score }}% to pass</small>
                      </div>
                    </div>
                    <div class="col-6">
                      <div class="d-flex align-items-center">
                        <i class="bi bi-question-circle text-success me-1"></i>
                        <small>{{ quiz.total_questions || 0 }} questions</small>
                      </div>
                    </div>
                  </div>

                  <!-- Quiz Date -->
                  <div class="mb-2">
                    <small class="text-muted">
                      <i class="bi bi-calendar3 me-1"></i>
                      Scheduled: {{ formatDateTime(quiz.date_of_quiz) }}
                    </small>
                  </div>

                  <!-- Status Badge -->
                  <div class="mb-3">
                    <span class="badge" :class="getStatusBadgeClass(quiz)">
                      {{ getQuizStatus(quiz) }}
                    </span>
                  </div>
                </div>
                <div class="card-footer bg-transparent">
                  <div class="d-grid gap-2">
                    <button
                      class="btn btn-outline-primary btn-sm"
                      @click="manageQuestions(quiz)"
                    >
                      <i class="bi bi-list-ol me-1"></i>
                      Manage Questions ({{ quiz.total_questions || 0 }})
                    </button>
                    <div class="btn-group" role="group">
                      <button
                        class="btn btn-outline-info btn-sm"
                        @click="viewStats(quiz)"
                      >
                        <i class="bi bi-bar-chart me-1"></i>Stats
                      </button>
                      <button
                        class="btn btn-outline-secondary btn-sm"
                        @click="editQuiz(quiz)"
                      >
                        <i class="bi bi-pencil me-1"></i>Edit
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Quiz Modal -->
      <div class="modal fade" id="quizModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {{ editingQuiz ? 'Edit Quiz' : 'Create New Quiz' }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form @submit.prevent="saveQuiz">
              <div class="modal-body">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="quizTitle" class="form-label">Quiz Title *</label>
                      <input
                        id="quizTitle"
                        v-model="form.title"
                        type="text"
                        class="form-control"
                        :class="{ 'is-invalid': errors.title }"
                        placeholder="Enter quiz title"
                        required
                      >
                      <div v-if="errors.title" class="invalid-feedback">
                        {{ errors.title }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label for="quizDate" class="form-label">Quiz Date & Time *</label>
                      <input
                        id="quizDate"
                        v-model="form.date_of_quiz"
                        type="datetime-local"
                        class="form-control"
                        :class="{ 'is-invalid': errors.date_of_quiz }"
                        required
                      >
                      <div v-if="errors.date_of_quiz" class="invalid-feedback">
                        {{ errors.date_of_quiz }}
                      </div>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label for="quizDescription" class="form-label">Description</label>
                  <textarea
                    id="quizDescription"
                    v-model="form.description"
                    class="form-control"
                    :class="{ 'is-invalid': errors.description }"
                    rows="3"
                    placeholder="Enter quiz description (optional)"
                  ></textarea>
                  <div v-if="errors.description" class="invalid-feedback">
                    {{ errors.description }}
                  </div>
                </div>

                <div class="row">
                  <div class="col-md-4">
                    <div class="mb-3">
                      <label for="timeDuration" class="form-label">Duration (minutes) *</label>
                      <input
                        id="timeDuration"
                        v-model="form.time_duration"
                        type="number"
                        class="form-control"
                        :class="{ 'is-invalid': errors.time_duration }"
                        min="1"
                        max="300"
                        placeholder="60"
                        required
                      >
                      <div v-if="errors.time_duration" class="invalid-feedback">
                        {{ errors.time_duration }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="mb-3">
                      <label for="maxAttempts" class="form-label">Max Attempts</label>
                      <input
                        id="maxAttempts"
                        v-model="form.max_attempts"
                        type="number"
                        class="form-control"
                        :class="{ 'is-invalid': errors.max_attempts }"
                        min="1"
                        max="10"
                        placeholder="3"
                      >
                      <div v-if="errors.max_attempts" class="invalid-feedback">
                        {{ errors.max_attempts }}
                      </div>
                    </div>
                  </div>
                  <div class="col-md-4">
                    <div class="mb-3">
                      <label for="passingScore" class="form-label">Passing Score (%)</label>
                      <input
                        id="passingScore"
                        v-model="form.passing_score"
                        type="number"
                        class="form-control"
                        :class="{ 'is-invalid': errors.passing_score }"
                        min="1"
                        max="100"
                        placeholder="60"
                      >
                      <div v-if="errors.passing_score" class="invalid-feedback">
                        {{ errors.passing_score }}
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
                  {{ editingQuiz ? 'Update' : 'Create' }} Quiz
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
              <p>Are you sure you want to delete the quiz <strong>{{ quizToDelete?.title }}</strong>?</p>
              <p class="text-danger small">
                <i class="bi bi-exclamation-triangle me-1"></i>
                This action will delete all questions and student attempts for this quiz.
              </p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" @click="deleteQuiz" :disabled="deleting">
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                Delete Quiz
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
  name: 'AdminQuizzes',
  components: { AppLayout },
  setup () {
    const route = useRoute()
    const router = useRouter()
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const chapter = ref(null)
    const quizzes = ref([])
    const editingQuiz = ref(null)
    const quizToDelete = ref(null)

    // Form data
    const form = ref({
      title: '',
      description: '',
      date_of_quiz: '',
      time_duration: 60,
      max_attempts: 3,
      passing_score: 60
    })

    const errors = ref({})

    // Modals
    let quizModal = null
    let deleteModal = null

    // Computed
    const totalQuestions = computed(() => {
      if (!Array.isArray(quizzes.value)) {
        return 0
      }
      return quizzes.value.reduce((sum, quiz) => sum + (quiz.total_questions || 0), 0)
    })

    // Methods
    const loadQuizzes = async () => {
      try {
        loading.value = true
        const chapterId = route.params.id

        if (chapterId) {
          // Load quizzes for a specific chapter
          const response = await adminStore.fetchQuizzes(chapterId)

          if (response.success) {
            // Get quizzes from the admin store (they are set in the store)
            quizzes.value = adminStore.quizzes || []
            chapter.value = response.chapter
          } else {
            quizzes.value = []
            toast.error(response.message || 'Failed to load quizzes')
          }
        } else {
          // Load all quizzes (for /admin/quizzes route)
          const response = await adminStore.fetchAllQuizzes()

          if (response.success) {
            quizzes.value = adminStore.quizzes || []
            chapter.value = null // No specific chapter
          } else {
            quizzes.value = []
            toast.error(response.message || 'Failed to load quizzes')
          }
        }
      } catch (error) {
        console.error('Load quizzes error:', error)
        quizzes.value = []
        toast.error('Failed to load quizzes')
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      editingQuiz.value = null
      form.value = {
        title: '',
        description: '',
        date_of_quiz: '',
        time_duration: 60,
        max_attempts: 3,
        passing_score: 60
      }
      errors.value = {}
      quizModal.show()
    }

    const editQuiz = (quiz) => {
      editingQuiz.value = quiz
      form.value = {
        title: quiz.title,
        description: quiz.description || '',
        date_of_quiz: quiz.date_of_quiz ? new Date(quiz.date_of_quiz).toISOString().slice(0, 16) : '',
        time_duration: quiz.time_duration,
        max_attempts: quiz.max_attempts,
        passing_score: quiz.passing_score
      }
      errors.value = {}
      quizModal.show()
    }

    const saveQuiz = async () => {
      try {
        saving.value = true
        errors.value = {}

        let result
        if (editingQuiz.value) {
          // Update quiz - we need to add this to the admin store
          result = await adminStore.updateQuiz(editingQuiz.value.id, form.value)
        } else {
          const chapterId = route.params.id
          result = await adminStore.createQuiz(chapterId, form.value)
        }

        if (result.success) {
          toast.success(result.message)
          quizModal.hide()
          await loadQuizzes()
        } else {
          toast.error(result.message)
          if (result.errors) {
            errors.value = result.errors
          }
        }
      } catch (error) {
        toast.error('An error occurred while saving the quiz')
      } finally {
        saving.value = false
      }
    }

    const confirmDelete = (quiz) => {
      quizToDelete.value = quiz
      deleteModal.show()
    }

    const deleteQuiz = async () => {
      try {
        deleting.value = true
        const result = await adminStore.deleteQuiz(quizToDelete.value.id)

        if (result.success) {
          toast.success(result.message)
          deleteModal.hide()
          await loadQuizzes()
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('Failed to delete quiz')
      } finally {
        deleting.value = false
      }
    }

    const manageQuestions = (quiz) => {
      router.push(`/admin/quizzes/${quiz.id}/questions`)
    }

    const viewStats = (quiz) => {
      router.push(`/admin/quizzes/${quiz.id}/stats`)
    }

    const getQuizHeaderClass = (quiz) => {
      const now = new Date()
      const quizDate = new Date(quiz.date_of_quiz)

      if (quizDate < now) {
        return 'bg-secondary' // Past quiz
      } else if (quizDate.toDateString() === now.toDateString()) {
        return 'bg-warning' // Today's quiz
      } else {
        return 'bg-primary' // Future quiz
      }
    }

    const getStatusBadgeClass = (quiz) => {
      const now = new Date()
      const quizDate = new Date(quiz.date_of_quiz)

      if (quizDate < now) {
        return 'bg-secondary'
      } else if (quizDate.toDateString() === now.toDateString()) {
        return 'bg-warning text-dark'
      } else {
        return 'bg-success'
      }
    }

    const getQuizStatus = (quiz) => {
      const now = new Date()
      const quizDate = new Date(quiz.date_of_quiz)

      if (quizDate < now) {
        return 'Completed'
      } else if (quizDate.toDateString() === now.toDateString()) {
        return 'Today'
      } else {
        return 'Upcoming'
      }
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'Not set'
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Lifecycle
    onMounted(async () => {
      await loadQuizzes()

      // Initialize modals
      quizModal = new Modal(document.getElementById('quizModal'))
      deleteModal = new Modal(document.getElementById('deleteModal'))
    })

    return {
      // State
      loading,
      saving,
      deleting,
      chapter,
      quizzes,
      editingQuiz,
      quizToDelete,
      form,
      errors,

      // Computed
      totalQuestions,

      // Methods
      openCreateModal,
      editQuiz,
      saveQuiz,
      confirmDelete,
      deleteQuiz,
      manageQuestions,
      viewStats,
      getQuizHeaderClass,
      getStatusBadgeClass,
      getQuizStatus,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.quiz-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.quiz-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.card-header {
  border-bottom: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline !important;
}

.btn-group .btn {
  border-radius: 0.25rem;
  margin-right: 0.25rem;
}

.btn-group .btn:last-child {
  margin-right: 0;
}

.dropdown-menu {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
