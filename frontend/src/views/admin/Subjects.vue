<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="mb-0">
                <i class="bi bi-book-fill me-2 text-primary"></i>
                Subject Management
              </h2>
              <p class="text-muted mb-0">Create and manage educational subjects</p>
            </div>
            <button
              class="btn btn-primary"
              @click="openCreateModal"
            >
              <i class="bi bi-plus-lg me-1"></i>
              Add Subject
            </button>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-4">
          <div class="card border-0 shadow-sm bg-primary text-white no-hover-effect">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-collection display-4 me-3"></i>
                <div>
                  <h4 class="mb-0">{{ subjects.length }}</h4>
                  <p class="mb-0">Total Subjects</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm bg-success text-white no-hover-effect">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-journal-bookmark display-4 me-3"></i>
                <div>
                  <h4 class="mb-0">{{ totalChapters }}</h4>
                  <p class="mb-0">Total Chapters</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card border-0 shadow-sm bg-info text-white no-hover-effect">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-patch-question display-4 me-3"></i>
                <div>
                  <h4 class="mb-0">{{ totalQuizzes }}</h4>
                  <p class="mb-0">Total Quizzes</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Subjects Table -->
      <div class="card border-0 shadow-sm no-hover-effect">
        <div class="card-header bg-light no-hover-effect">
          <h5 class="mb-0 no-hover-effect text-white">
            <i class="bi bi-table me-2"></i>
            Subjects List
          </h5>
        </div>
        <div class="card-body">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading subjects...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="subjects.length === 0" class="text-center py-5">
            <i class="bi bi-inbox display-1 text-muted mb-3"></i>
            <h5 class="text-muted">No subjects found</h5>
            <p class="text-muted">Create your first subject to get started.</p>
            <button class="btn btn-primary" @click="openCreateModal">
              <i class="bi bi-plus-lg me-1"></i>
              Add Subject
            </button>
          </div>

          <!-- Subjects List -->
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Subject</th>
                  <th>Description</th>
                  <th>Chapters</th>
                  <th>Quizzes</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="subject in subjects" :key="subject.id">
                  <td>
                    <div class="fw-semibold text-white">{{ subject.name }}</div>
                  </td>
                  <td>
                    <div class="text-white small">{{ subject.description || 'No description' }}</div>
                  </td>
                  <td>
                    <span class="badge bg-primary">{{ subject.total_chapters || 0 }}</span>
                  </td>
                  <td>
                    <span class="badge bg-success">{{ subject.total_quizzes || 0 }}</span>
                  </td>
                  <td>
                    <small class="text-muted">
                      {{ formatDate(subject.created_at) }}
                    </small>
                  </td>
                  <td>
                    <div class="btn-group" role="group">
                      <button
                        class="btn btn-sm btn-outline-info"
                        @click="viewChapters(subject)"
                        title="View Chapters"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                      <button
                        class="btn btn-sm btn-outline-primary"
                        @click="editSubject(subject)"
                        title="Edit Subject"
                      >
                        <i class="bi bi-pencil"></i>
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger"
                        @click="confirmDelete(subject)"
                        title="Delete Subject"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Create/Edit Subject Modal -->
      <div class="modal fade" id="subjectModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {{ editingSubject ? 'Edit Subject' : 'Create New Subject' }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form @submit.prevent="saveSubject">
              <div class="modal-body">
                <div class="mb-3">
                  <label for="subjectName" class="form-label">Subject Name *</label>
                  <input
                    id="subjectName"
                    v-model="form.name"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': errors.name }"
                    placeholder="Enter subject name"
                    required
                  >
                  <div v-if="errors.name" class="invalid-feedback">
                    {{ errors.name }}
                  </div>
                </div>
                <div class="mb-3">
                  <label for="subjectDescription" class="form-label">Description</label>
                  <textarea
                    id="subjectDescription"
                    v-model="form.description"
                    class="form-control"
                    :class="{ 'is-invalid': errors.description }"
                    rows="3"
                    placeholder="Enter subject description (optional)"
                  ></textarea>
                  <div v-if="errors.description" class="invalid-feedback">
                    {{ errors.description }}
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingSubject ? 'Update' : 'Create' }} Subject
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
              <p>Are you sure you want to delete the subject <strong>{{ subjectToDelete?.name }}</strong>?</p>
              <p class="text-danger small">
                <i class="bi bi-exclamation-triangle me-1"></i>
                This action will also affect all chapters and quizzes under this subject.
              </p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" @click="deleteSubject" :disabled="deleting">
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                Delete Subject
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
import { useRouter } from 'vue-router'
import { Modal } from 'bootstrap'
import { toast } from '@/utils/toast'
import { useAdminStore } from '@/stores/admin'
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'AdminSubjects',
  components: { AppLayout },
  setup () {
    const router = useRouter()
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const subjects = ref([])
    const editingSubject = ref(null)
    const subjectToDelete = ref(null)

    // Form data
    const form = ref({
      name: '',
      description: ''
    })

    const errors = ref({})

    // Modals
    let subjectModal = null
    let deleteModal = null

    // Computed
    const totalChapters = computed(() => {
      return subjects.value.reduce((sum, subject) => sum + (subject.total_chapters || 0), 0)
    })

    const totalQuizzes = computed(() => {
      return subjects.value.reduce((sum, subject) => sum + (subject.total_quizzes || 0), 0)
    })

    // Methods
    const loadSubjects = async () => {
      try {
        loading.value = true
        await adminStore.fetchSubjects()
        subjects.value = adminStore.subjects
      } catch (error) {
        toast.error('Failed to load subjects')
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      editingSubject.value = null
      form.value = { name: '', description: '' }
      errors.value = {}
      subjectModal.show()
    }

    const editSubject = (subject) => {
      editingSubject.value = subject
      form.value = {
        name: subject.name,
        description: subject.description || ''
      }
      errors.value = {}
      subjectModal.show()
    }

    const saveSubject = async () => {
      try {
        saving.value = true
        errors.value = {}

        let result
        if (editingSubject.value) {
          result = await adminStore.updateSubject(editingSubject.value.id, form.value)
        } else {
          result = await adminStore.createSubject(form.value)
        }

        if (result.success) {
          toast.success(result.message)
          subjectModal.hide()
          await loadSubjects()
        } else {
          toast.error(result.message)
          // Handle field-specific errors if needed
          if (result.errors) {
            errors.value = result.errors
          }
        }
      } catch (error) {
        console.error('Save subject error:', error)
        toast.error('An error occurred while saving the subject')
      } finally {
        saving.value = false
      }
    }

    const confirmDelete = (subject) => {
      subjectToDelete.value = subject
      deleteModal.show()
    }

    const deleteSubject = async () => {
      try {
        deleting.value = true
        const result = await adminStore.deleteSubject(subjectToDelete.value.id)

        if (result.success) {
          toast.success(result.message)
          deleteModal.hide()
          await loadSubjects()
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('Failed to delete subject')
      } finally {
        deleting.value = false
      }
    }

    const viewChapters = (subject) => {
      router.push(`/admin/subjects/${subject.id}/chapters`)
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Lifecycle
    onMounted(async () => {
      await loadSubjects()

      // Initialize modals
      subjectModal = new Modal(document.getElementById('subjectModal'))
      deleteModal = new Modal(document.getElementById('deleteModal'))
    })

    return {
      // State
      loading,
      saving,
      deleting,
      subjects,
      editingSubject,
      subjectToDelete,
      form,
      errors,

      // Computed
      totalChapters,
      totalQuizzes,

      // Methods
      openCreateModal,
      editSubject,
      saveSubject,
      confirmDelete,
      deleteSubject,
      viewChapters,
      formatDate
    }
  }
}
</script>

<style scoped>
.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.btn-group .btn {
  border-radius: 0.25rem;
  margin-right: 0.25rem;
}

.btn-group .btn:last-child {
  margin-right: 0;
}

.table td {
  vertical-align: middle;
}

.badge {
  font-size: 0.75em;
}
</style>
