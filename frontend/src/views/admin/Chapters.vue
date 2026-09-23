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
                  <li class="breadcrumb-item active">{{ subject?.name }}</li>
                </ol>
              </nav>
              <h2 class="mb-0">
                <i class="bi bi-journal-bookmark-fill me-2 text-info"></i>
                Chapter Management
              </h2>
              <p class="text-muted mb-0">Manage chapters for {{ subject?.name }}</p>
            </div>
            <button
              class="btn btn-primary"
              @click="openCreateModal"
            >
              <i class="bi bi-plus-lg me-1"></i>
              Add Chapter
            </button>
          </div>
        </div>
      </div>

      <!-- Subject Info Card -->
      <div class="row mb-4" v-if="subject">
        <div class="col-12">
          <div class="card border-0 shadow-sm bg-light">
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <h5 class="mb-1">{{ subject.name }}</h5>
                  <p class="text-muted mb-0">{{ subject.description || 'No description provided' }}</p>
                </div>
                <div class="col-md-4 text-md-end">
                  <div class="d-flex justify-content-md-end gap-3">
                    <div class="text-center">
                      <h4 class="mb-0 text-primary">{{ chapters?.length || 0 }}</h4>
                      <small class="text-muted">Chapters</small>
                    </div>
                    <div class="text-center">
                      <h4 class="mb-0 text-success">{{ totalQuizzes }}</h4>
                      <small class="text-muted">Total Quizzes</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Chapters List -->
      <div class="card border-0 shadow-sm">
        <div class="card-header bg-light">
          <h5 class="mb-0">
            <i class="bi bi-list-ul me-2"></i>
            Chapters List
          </h5>
        </div>
        <div class="card-body">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading chapters...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="!chapters || chapters.length === 0" class="text-center py-5">
            <i class="bi bi-journal-x display-1 text-muted mb-3"></i>
            <h5 class="text-muted">No chapters found</h5>
            <p class="text-muted">Create your first chapter for this subject.</p>
            <button class="btn btn-primary" @click="openCreateModal">
              <i class="bi bi-plus-lg me-1"></i>
              Add Chapter
            </button>
          </div>

          <!-- Chapters Grid -->
          <div v-else class="row">
            <div v-for="(chapter, index) in chapters" :key="chapter.id" class="col-md-6 col-lg-4 mb-4">
              <div class="card h-100 border-0 shadow-sm chapter-card">
                <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
                  <div>
                    <h6 class="mb-0">Chapter {{ chapter.order_index || (index + 1) }}</h6>
                  </div>
                  <div class="dropdown">
                    <button
                      class="btn btn-sm btn-outline-light"
                      type="button"
                      :id="'dropdown-' + chapter.id"
                      data-bs-toggle="dropdown"
                    >
                      <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu">
                      <li>
                        <a class="dropdown-item" href="#" @click.prevent="viewQuizzes(chapter)">
                          <i class="bi bi-eye me-2"></i>View Quizzes
                        </a>
                      </li>
                      <li>
                        <a class="dropdown-item" href="#" @click.prevent="editChapter(chapter)">
                          <i class="bi bi-pencil me-2"></i>Edit Chapter
                        </a>
                      </li>
                      <li><hr class="dropdown-divider"></li>
                      <li>
                        <a class="dropdown-item text-danger" href="#" @click.prevent="confirmDelete(chapter)">
                          <i class="bi bi-trash me-2"></i>Delete Chapter
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
                <div class="card-body">
                  <h5 class="card-title">{{ chapter.name }}</h5>
                  <p class="card-text text-muted">
                    {{ chapter.description || 'No description provided' }}
                  </p>
                  <div class="row text-center">
                    <div class="col-6">
                      <div class="badge bg-success fs-6">{{ chapter.quiz_count || 0 }}</div>
                      <div class="small text-muted">Quizzes</div>
                    </div>
                    <div class="col-6">
                      <div class="small text-muted">Created</div>
                      <div class="small">{{ formatDate(chapter.created_at) }}</div>
                    </div>
                  </div>
                </div>
                <div class="card-footer bg-transparent">
                  <div class="d-grid">
                    <button
                      class="btn btn-outline-primary btn-sm"
                      @click="viewQuizzes(chapter)"
                    >
                      <i class="bi bi-arrow-right me-1"></i>
                      Manage Quizzes
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Create/Edit Chapter Modal -->
      <div class="modal fade" id="chapterModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title">
                {{ editingChapter ? 'Edit Chapter' : 'Create New Chapter' }}
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <form @submit.prevent="saveChapter">
              <div class="modal-body">
                <div class="mb-3">
                  <label for="chapterName" class="form-label">Chapter Name *</label>
                  <input
                    id="chapterName"
                    v-model="form.name"
                    type="text"
                    class="form-control"
                    :class="{ 'is-invalid': errors.name }"
                    placeholder="Enter chapter name"
                    required
                  >
                  <div v-if="errors.name" class="invalid-feedback">
                    {{ errors.name }}
                  </div>
                </div>
                <div class="mb-3">
                  <label for="chapterDescription" class="form-label">Description</label>
                  <textarea
                    id="chapterDescription"
                    v-model="form.description"
                    class="form-control"
                    :class="{ 'is-invalid': errors.description }"
                    rows="3"
                    placeholder="Enter chapter description (optional)"
                  ></textarea>
                  <div v-if="errors.description" class="invalid-feedback">
                    {{ errors.description }}
                  </div>
                </div>
                <div class="mb-3">
                  <label for="orderIndex" class="form-label">Order Index</label>
                  <input
                    id="orderIndex"
                    v-model="form.order_index"
                    type="number"
                    class="form-control"
                    :class="{ 'is-invalid': errors.order_index }"
                    min="1"
                    placeholder="Chapter order"
                  >
                  <div class="form-text">Determines the display order of chapters</div>
                  <div v-if="errors.order_index" class="invalid-feedback">
                    {{ errors.order_index }}
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ editingChapter ? 'Update' : 'Create' }} Chapter
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
              <p>Are you sure you want to delete the chapter <strong>{{ chapterToDelete?.name }}</strong>?</p>
              <p class="text-danger small">
                <i class="bi bi-exclamation-triangle me-1"></i>
                This action will also delete all quizzes and questions in this chapter.
              </p>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="button" class="btn btn-danger" @click="deleteChapter" :disabled="deleting">
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                Delete Chapter
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
  name: 'AdminChapters',
  components: { AppLayout },
  setup () {
    const route = useRoute()
    const router = useRouter()
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const subject = ref(null)
    const chapters = ref([])
    const editingChapter = ref(null)
    const chapterToDelete = ref(null)

    // Form data
    const form = ref({
      name: '',
      description: '',
      order_index: 1
    })

    const errors = ref({})

    // Modals
    let chapterModal = null
    let deleteModal = null

    // Computed
    const totalQuizzes = computed(() => {
      if (!Array.isArray(chapters.value)) {
        return 0
      }
      return chapters.value.reduce((sum, chapter) => sum + (chapter.quiz_count || 0), 0)
    })

    // Methods
    const loadChapters = async () => {
      try {
        loading.value = true
        const subjectId = route.params.id
        const response = await adminStore.fetchChapters(subjectId)

        if (response.success) {
          // Get chapters from the admin store (they are set in the store)
          chapters.value = adminStore.chapters || []
          subject.value = response.subject
        } else {
          chapters.value = []
          toast.error(response.message || 'Failed to load chapters')
        }
      } catch (error) {
        console.error('Load chapters error:', error)
        chapters.value = []
        toast.error('Failed to load chapters')
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      editingChapter.value = null
      form.value = {
        name: '',
        description: '',
        order_index: chapters.value.length + 1
      }
      errors.value = {}
      chapterModal.show()
    }

    const editChapter = (chapter) => {
      editingChapter.value = chapter
      form.value = {
        name: chapter.name,
        description: chapter.description || '',
        order_index: chapter.order_index || 1
      }
      errors.value = {}
      chapterModal.show()
    }

    const saveChapter = async () => {
      try {
        saving.value = true
        errors.value = {}

        let result
        if (editingChapter.value) {
          // Update chapter - we need to add this to the admin store
          result = await adminStore.updateChapter(editingChapter.value.id, form.value)
        } else {
          const subjectId = route.params.id
          result = await adminStore.createChapter(subjectId, form.value)
        }

        if (result.success) {
          toast.success(result.message)
          chapterModal.hide()
          await loadChapters()
        } else {
          toast.error(result.message)
          if (result.errors) {
            errors.value = result.errors
          }
        }
      } catch (error) {
        toast.error('An error occurred while saving the chapter')
      } finally {
        saving.value = false
      }
    }

    const confirmDelete = (chapter) => {
      chapterToDelete.value = chapter
      deleteModal.show()
    }

    const deleteChapter = async () => {
      try {
        deleting.value = true
        const result = await adminStore.deleteChapter(chapterToDelete.value.id)

        if (result.success) {
          toast.success(result.message)
          deleteModal.hide()
          await loadChapters()
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('Failed to delete chapter')
      } finally {
        deleting.value = false
      }
    }

    const viewQuizzes = (chapter) => {
      router.push(`/admin/chapters/${chapter.id}/quizzes`)
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
      await loadChapters()

      // Initialize modals
      chapterModal = new Modal(document.getElementById('chapterModal'))
      deleteModal = new Modal(document.getElementById('deleteModal'))
    })

    return {
      // State
      loading,
      saving,
      deleting,
      subject,
      chapters,
      editingChapter,
      chapterToDelete,
      form,
      errors,

      // Computed
      totalQuizzes,

      // Methods
      openCreateModal,
      editChapter,
      saveChapter,
      confirmDelete,
      deleteChapter,
      viewQuizzes,
      formatDate
    }
  }
}
</script>

<style scoped>
.chapter-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.chapter-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}

.badge {
  font-size: 1rem;
  padding: 0.5em 0.8em;
}

.dropdown-menu {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-header {
  border-bottom: none;
}

.breadcrumb-item a:hover {
  text-decoration: underline !important;
}
</style>
