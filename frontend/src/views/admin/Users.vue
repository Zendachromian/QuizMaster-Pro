<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h2 class="mb-0 text-white">
                <i class="bi bi-people-fill me-2 text-primary"></i>
                User Management
              </h2>
              <p class="text-white fw-semibold mb-0">Manage registered users and their activities</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card border-0 shadow-sm bg-primary text-white no-hover-effect stats-card-no-hover">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-people display-4 me-3 text-white"></i>
                <div>
                  <h4 class="mb-0 text-white">{{ pagination?.total || 0 }}</h4>
                  <p class="mb-0 text-white">Total Users</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm bg-success text-white no-hover-effect stats-card-no-hover">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-person-check display-4 me-3 text-white"></i>
                <div>
                  <h4 class="mb-0 text-white">{{ activeUsersCount }}</h4>
                  <p class="mb-0 text-white">Active Users</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm bg-warning text-white no-hover-effect stats-card-no-hover">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-person-x display-4 me-3 text-white"></i>
                <div>
                  <h4 class="mb-0 text-white">{{ inactiveUsersCount }}</h4>
                  <p class="mb-0 text-white">Inactive Users</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-0 shadow-sm bg-info text-white no-hover-effect stats-card-no-hover">
            <div class="card-body">
              <div class="d-flex align-items-center">
                <i class="bi bi-calendar-plus display-4 me-3 text-white"></i>
                <div>
                  <h4 class="mb-0 text-white">{{ newUsersThisMonth }}</h4>
                  <p class="mb-0 text-white">This Month</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Table -->
      <div class="card border-0 shadow-sm no-hover-effect">
        <div class="card-header bg-white no-hover-effect">
          <div class="row align-items-center">
            <div class="col">
              <h5 class="mb-0 text-white no-hover-effect">
                <i class="bi bi-table me-2 text-primary"></i>
                Users List
              </h5>
            </div>
            <div class="col-auto">
              <div class="input-group no-hover-effect">
                <input
                  v-model="searchQuery"
                  type="text"
                  class="form-control"
                  placeholder="Search users..."
                  @keyup.enter="searchUsers"
                >
                <button class="btn btn-outline-secondary no-hover-effect" type="button" @click="searchUsers">
                  <i class="bi bi-search"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="card-body">
          <!-- Loading -->
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2 text-muted">Loading users...</p>
          </div>

          <!-- Empty State -->
          <div v-else-if="users.length === 0" class="text-center py-5">
            <i class="bi bi-person-x display-1 text-muted mb-3"></i>
            <h5 class="text-muted">No users found</h5>
            <p class="text-muted">
              {{ searchQuery ? 'No users match your search criteria.' : 'No users have registered yet.' }}
            </p>
            <button v-if="searchQuery" class="btn btn-primary no-hover-effect" @click="clearSearch">
              <i class="bi bi-arrow-clockwise me-1"></i>
              Clear Search
            </button>
          </div>

          <!-- Users Table -->
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle table-no-hover">
              <thead class="table-light">
                <tr>
                  <th>User</th>
                  <th>Contact</th>
                  <th>Qualification</th>
                  <th>Registration</th>
                  <th>Status</th>
                  <th>Quiz Activity</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>
                    <div class="d-flex align-items-center">
                      <div class="avatar-circle me-3">
                        {{ getInitials(user.full_name) }}
                      </div>
                      <div>
                        <div class="fw-semibold text-white">{{ user.full_name }}</div>
                        <div class="text-muted small">@{{ user.username }}</div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="small">
                      <div class="text-white">{{ user.email }}</div>
                      <div class="text-white" v-if="user.phone">{{ user.phone }}</div>
                    </div>
                  </td>
                  <td>
                    <small class="text-white">
                      {{ user.qualification || 'Not provided' }}
                    </small>
                  </td>
                  <td>
                    <small class="text-white">
                      {{ formatDate(user.created_at) }}
                    </small>
                  </td>
                  <td>
                    <span
                      class="badge"
                      :class="user.is_active ? 'bg-success' : 'bg-danger'"
                    >
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td>
                    <div class="d-flex gap-2 align-items-center">
                      <span class="badge bg-info">
                        {{ user.quiz_attempts || 0 }} attempts
                      </span>
                      <div class="avg-score-container">
                        <ProgressBar
                          :percentage="user.avg_score || 0"
                          :height="16"
                          :show-label="true"
                          :show-text="false"
                        />
                      </div>
                    </div>
                  </td>
                  <td>
                    <div class="btn-group" role="group">
                      <button
                        class="btn btn-sm btn-outline-info no-hover-effect"
                        @click="viewUser(user)"
                        title="View Details"
                      >
                        <i class="bi bi-eye"></i>
                      </button>
                      <button
                        class="btn btn-sm no-hover-effect"
                        :class="user.is_active ? 'btn-outline-warning' : 'btn-outline-success'"
                        @click="toggleUserStatus(user)"
                        :title="user.is_active ? 'Deactivate User' : 'Activate User'"
                        :disabled="togglingUsers.includes(user.id)"
                      >
                        <span v-if="togglingUsers.includes(user.id)" class="spinner-border spinner-border-sm"></span>
                        <i v-else :class="user.is_active ? 'bi bi-person-dash' : 'bi bi-person-check'"></i>
                      </button>
                      <button
                        class="btn btn-sm btn-outline-danger no-hover-effect"
                        @click="confirmDeleteUser(user)"
                        title="Delete User"
                        :disabled="deletingUsers.includes(user.id)"
                      >
                        <span v-if="deletingUsers.includes(user.id)" class="spinner-border spinner-border-sm"></span>
                        <i v-else class="bi bi-trash"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Pagination -->
          <div v-if="pagination && pagination.pages > 1" class="row mt-4">
            <div class="col-sm-6">
              <small class="text-muted">
                Showing {{ (pagination.page - 1) * pagination.per_page + 1 }} to
                {{ Math.min(pagination.page * pagination.per_page, pagination.total) }} of
                {{ pagination.total }} users
              </small>
            </div>
            <div class="col-sm-6">
              <nav>
                <ul class="pagination pagination-sm justify-content-end mb-0">
                  <li class="page-item" :class="{ disabled: pagination.page === 1 }">
                    <button class="page-link no-hover-effect" @click="loadPage(pagination.page - 1)" :disabled="pagination.page === 1">
                      Previous
                    </button>
                  </li>
                  <li
                    v-for="page in getVisiblePages()"
                    :key="page"
                    class="page-item"
                    :class="{ active: page === pagination.page }"
                  >
                    <button class="page-link no-hover-effect" @click="loadPage(page)">{{ page }}</button>
                  </li>
                  <li class="page-item" :class="{ disabled: pagination.page === pagination.pages }">
                    <button
                      class="page-link no-hover-effect"
                      @click="loadPage(pagination.page + 1)"
                      :disabled="pagination.page === pagination.pages"
                    >
                      Next
                    </button>
                  </li>
                </ul>
              </nav>
            </div>
          </div>
        </div>
      </div>

      <!-- User Details Modal -->
      <div class="modal fade" id="userModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title text-dark">User Details</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" v-if="selectedUser">
              <div class="row">
                <div class="col-md-4 text-center">
                  <div class="avatar-circle-large mb-3">
                    {{ getInitials(selectedUser.full_name) }}
                  </div>
                  <h5>{{ selectedUser.full_name }}</h5>
                  <p class="text-muted">@{{ selectedUser.username }}</p>
                  <span
                    class="badge fs-6"
                    :class="selectedUser.is_active ? 'bg-success' : 'bg-danger'"
                  >
                    {{ selectedUser.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div class="col-md-8">
                  <div class="row g-3">
                    <div class="col-sm-6">
                      <strong>Email:</strong><br>
                      <span class="text-muted">{{ selectedUser.email }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Phone:</strong><br>
                      <span class="text-muted">{{ selectedUser.phone || 'Not provided' }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Date of Birth:</strong><br>
                      <span class="text-muted">{{ selectedUser.date_of_birth ? formatDate(selectedUser.date_of_birth) : 'Not provided' }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Qualification:</strong><br>
                      <span class="text-muted">{{ selectedUser.qualification || 'Not provided' }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Registration Date:</strong><br>
                      <span class="text-muted">{{ formatDate(selectedUser.created_at) }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Last Login:</strong><br>
                      <span class="text-muted">{{ selectedUser.last_login ? formatDate(selectedUser.last_login) : 'Never' }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Quiz Attempts:</strong><br>
                      <span class="text-muted">{{ selectedUser.quiz_attempts || 0 }}</span>
                    </div>
                    <div class="col-sm-6">
                      <strong>Average Score:</strong><br>
                      <div class="mt-1">
                        <ProgressBar
                          :percentage="selectedUser.avg_score || 0"
                          :height="24"
                          :show-label="true"
                          :show-text="true"
                        />
                      </div>
                    </div>
                    <div class="col-12">
                      <strong>Biography:</strong><br>
                      <span class="text-muted">{{ selectedUser.bio || 'No biography provided' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary no-hover-effect" data-bs-dismiss="modal">
                Close
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Modal -->
      <div class="modal fade" id="deleteUserModal" tabindex="-1">
        <div class="modal-dialog">
          <div class="modal-content">
            <div class="modal-header border-0">
              <h5 class="modal-title text-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Confirm User Deletion
              </h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" v-if="userToDelete">
              <div class="text-center">
                <div class="avatar-circle-large mb-3 bg-danger">
                  {{ getInitials(userToDelete.full_name) }}
                </div>
                <h6>{{ userToDelete.full_name }}</h6>
                <p class="text-muted">{{ userToDelete.email }}</p>
              </div>
              <div class="alert alert-warning border-0">
                <div class="d-flex">
                  <i class="bi bi-exclamation-triangle-fill me-2 text-warning"></i>
                  <div>
                    <strong>Warning:</strong> This action will deactivate the user account.
                    The user will no longer be able to access the system, but their data will be preserved.
                  </div>
                </div>
              </div>
              <p class="mb-0">Are you sure you want to delete this user?</p>
            </div>
            <div class="modal-footer border-0">
              <button type="button" class="btn btn-secondary no-hover-effect" data-bs-dismiss="modal">
                Cancel
              </button>
              <button
                type="button"
                class="btn btn-danger no-hover-effect"
                @click="deleteUser"
                :disabled="deleting"
              >
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-trash me-2"></i>
                {{ deleting ? 'Deleting...' : 'Delete User' }}
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
import { Modal } from 'bootstrap'
import { toast } from '@/utils/toast'
import { useAdminStore } from '@/stores/admin'
import AppLayout from '@/components/AppLayout.vue'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'AdminUsers',
  components: {
    AppLayout,
    ProgressBar
  },
  setup () {
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const users = ref([])
    const pagination = ref(null)
    const searchQuery = ref('')
    const selectedUser = ref(null)
    const togglingUsers = ref([])
    const deletingUsers = ref([])
    const userToDelete = ref(null)
    const deleting = ref(false)

    // Modals
    let userModal = null
    let deleteUserModal = null

    // Computed
    const activeUsersCount = computed(() => {
      return users.value.filter(user => user.is_active).length
    })

    const inactiveUsersCount = computed(() => {
      return users.value.filter(user => !user.is_active).length
    })

    const newUsersThisMonth = computed(() => {
      const now = new Date()
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      return users.value.filter(user => {
        const createdAt = new Date(user.created_at)
        return createdAt >= startOfMonth
      }).length
    })

    // Methods
    const loadUsers = async (page = 1, search = '') => {
      try {
        loading.value = true
        const paginationData = await adminStore.fetchUsers(page, search)
        users.value = adminStore.users
        pagination.value = paginationData
      } catch (error) {
        toast.error('Failed to load users')
      } finally {
        loading.value = false
      }
    }

    const loadPage = async (page) => {
      if (page < 1 || (pagination.value && page > pagination.value.pages)) return
      await loadUsers(page, searchQuery.value)
    }

    const searchUsers = async () => {
      await loadUsers(1, searchQuery.value)
    }

    const clearSearch = async () => {
      searchQuery.value = ''
      await loadUsers(1, '')
    }

    const toggleUserStatus = async (user) => {
      try {
        togglingUsers.value.push(user.id)
        const result = await adminStore.toggleUserStatus(user.id)

        if (result.success) {
          toast.success(result.message)
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('Failed to toggle user status')
      } finally {
        togglingUsers.value = togglingUsers.value.filter(id => id !== user.id)
      }
    }

    const viewUser = (user) => {
      selectedUser.value = user
      userModal.show()
    }

    const confirmDeleteUser = (user) => {
      userToDelete.value = user
      deleteUserModal.show()
    }

    const deleteUser = async () => {
      if (!userToDelete.value) return

      try {
        deleting.value = true
        const result = await adminStore.deleteUser(userToDelete.value.id)

        if (result.success) {
          toast.success(result.message)
          deleteUserModal.hide()
          // Refresh the user list
          await loadUsers(pagination.value?.page || 1, searchQuery.value)
        } else {
          toast.error(result.message)
        }
      } catch (error) {
        toast.error('Failed to delete user')
      } finally {
        deleting.value = false
        userToDelete.value = null
      }
    }

    const getInitials = (name) => {
      if (!name) return 'U'
      return name.split(' ')
        .map(word => word.charAt(0).toUpperCase())
        .slice(0, 2)
        .join('')
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const getVisiblePages = () => {
      if (!pagination.value) return []

      const current = pagination.value.page
      const total = pagination.value.pages
      const pages = []

      // Always show first page
      if (current > 3) pages.push(1)

      // Add ellipsis if needed
      if (current > 4) pages.push('...')

      // Add pages around current
      for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
        pages.push(i)
      }

      // Add ellipsis if needed
      if (current < total - 3) pages.push('...')

      // Always show last page
      if (current < total - 2) pages.push(total)

      return pages.filter(page => page !== '...' || true) // Keep ellipsis
    }

    // Lifecycle
    onMounted(async () => {
      await loadUsers()
      userModal = new Modal(document.getElementById('userModal'))
      deleteUserModal = new Modal(document.getElementById('deleteUserModal'))
    })

    return {
      // State
      loading,
      users,
      pagination,
      searchQuery,
      selectedUser,
      togglingUsers,
      deletingUsers,
      userToDelete,
      deleting,

      // Computed
      activeUsersCount,
      inactiveUsersCount,
      newUsersThisMonth,

      // Methods
      loadPage,
      searchUsers,
      clearSearch,
      toggleUserStatus,
      viewUser,
      confirmDeleteUser,
      deleteUser,
      getInitials,
      formatDate,
      getVisiblePages
    }
  }
}
</script>

<style scoped>
.avatar-circle {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.avatar-circle-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 24px;
  margin: 0 auto;
}

.avatar-circle-large.bg-danger {
  background: linear-gradient(135deg, #dc3545 0%, #e83e8c 100%);
}

.avg-score-container {
  min-width: 100px;
}

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

.input-group {
  width: 300px;
}

.page-link {
  cursor: pointer;
}
</style>
