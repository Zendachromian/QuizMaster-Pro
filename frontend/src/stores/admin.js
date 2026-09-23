import { defineStore } from 'pinia'
import axios from '@/utils/axios'

// Admin store: manage subjects, chapters, quizzes and questions
export const useAdminStore = defineStore('admin', {
  state: () => ({
    subjects: [], // list of all subjects
    chapters: [], // list of chapters for current subject
    quizzes: [], // list of all quizzes
    quizInfo: {}, // metadata for current quiz
    questions: [], // questions for current quiz
    users: [], // list of all users (for admin management)
    loading: false, // global loading spinner
    stats: {}, // dashboard statistics
    recentAttempts: [], // recent quiz attempts
    recentUsers: [], // recent users
    chartData: {} // chart data for dashboard
  }),
  actions: {
    // SUBJECT MANAGEMENT
    // Fetch all subjects
    async fetchSubjects () {
      this.loading = true
      try {
        const { data } = await axios.get('/admin/subjects')
        this.subjects = data.subjects
        return { success: true }
      } catch (error) {
        console.error('Failed to load subjects', error)
        return { success: false, message: error.response?.data?.error || 'Failed to load subjects' }
      } finally {
        this.loading = false
      }
    },

    // Create a new subject
    async createSubject (payload) {
      try {
        const { data } = await axios.post('/admin/subjects/create', payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to create subject', error)
        return { success: false, message: error.response?.data?.error || 'Failed to create subject' }
      }
    },

    // Update a subject
    async updateSubject (subjectId, payload) {
      try {
        const { data } = await axios.put(`/admin/subjects/${subjectId}/edit`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to update subject', error)
        return { success: false, message: error.response?.data?.error || 'Failed to update subject' }
      }
    },

    // Delete a subject
    async deleteSubject (subjectId) {
      try {
        const { data } = await axios.delete(`/admin/subjects/${subjectId}`)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to delete subject', error)
        return { success: false, message: error.response?.data?.error || 'Failed to delete subject' }
      }
    },

    // CHAPTER MANAGEMENT
    // Fetch chapters for a subject
    async fetchChapters (subjectId) {
      this.loading = true
      try {
        const { data } = await axios.get(`/admin/subjects/${subjectId}/chapters`)
        this.chapters = data.chapters
        return { success: true, subject: data.subject }
      } catch (error) {
        console.error('Failed to load chapters', error)
        return { success: false, message: error.response?.data?.error || 'Failed to load chapters' }
      } finally {
        this.loading = false
      }
    },

    // Create a new chapter
    async createChapter (subjectId, payload) {
      try {
        const { data } = await axios.post(`/admin/subjects/${subjectId}/chapters/create`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to create chapter', error)
        return { success: false, message: error.response?.data?.error || 'Failed to create chapter' }
      }
    },

    // Update a chapter
    async updateChapter (subjectId, chapterId, payload) {
      try {
        const { data } = await axios.put(`/admin/subjects/${subjectId}/chapters/${chapterId}`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to update chapter', error)
        return { success: false, message: error.response?.data?.error || 'Failed to update chapter' }
      }
    },

    // Delete a chapter
    async deleteChapter (subjectId, chapterId) {
      try {
        const { data } = await axios.delete(`/admin/subjects/${subjectId}/chapters/${chapterId}`)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to delete chapter', error)
        return { success: false, message: error.response?.data?.error || 'Failed to delete chapter' }
      }
    },

    // QUIZ MANAGEMENT
    // Fetch quizzes for a chapter
    async fetchQuizzes (chapterId) {
      this.loading = true
      try {
        const { data } = await axios.get(`/admin/chapters/${chapterId}/quizzes`)
        this.quizzes = data.quizzes
        return { success: true, chapter: data.chapter }
      } catch (error) {
        console.error('Failed to load quizzes', error)
        return { success: false, message: error.response?.data?.error || 'Failed to load quizzes' }
      } finally {
        this.loading = false
      }
    },

    // Fetch all quizzes
    async fetchAllQuizzes () {
      this.loading = true
      try {
        const { data } = await axios.get('/admin/quizzes')
        this.quizzes = data.quizzes || []
        return { success: true }
      } catch (error) {
        console.error('Failed to load quizzes', error)
        return { success: false, message: error.response?.data?.error || 'Failed to load quizzes' }
      } finally {
        this.loading = false
      }
    },

    // Create a new quiz
    async createQuiz (chapterId, payload) {
      try {
        const { data } = await axios.post(`/admin/chapters/${chapterId}/quizzes/create`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to create quiz', error)
        return { success: false, message: error.response?.data?.error || 'Failed to create quiz' }
      }
    },

    // Update a quiz
    async updateQuiz (quizId, payload) {
      try {
        const { data } = await axios.put(`/admin/quizzes/${quizId}`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to update quiz', error)
        return { success: false, message: error.response?.data?.error || 'Failed to update quiz' }
      }
    },

    // Delete a quiz
    async deleteQuiz (quizId) {
      try {
        const { data } = await axios.delete(`/admin/quizzes/${quizId}`)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to delete quiz', error)
        return { success: false, message: error.response?.data?.error || 'Failed to delete quiz' }
      }
    },

    // QUESTION MANAGEMENT
    // Fetch questions for a specific quiz
    async fetchQuestions (quizId) {
      this.loading = true
      try {
        const { data } = await axios.get(`/admin/quizzes/${quizId}/questions`)
        this.quizInfo = data.quiz
        this.questions = data.questions
      } catch (error) {
        console.error('Failed to load questions', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Create a question
    async createQuestion (quizId, payload) {
      try {
        const { data } = await axios.post(`/admin/quizzes/${quizId}/questions/create`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to create question', error)
        return { success: false, message: error.response?.data?.error || 'Failed to create question' }
      }
    },

    // Update a question
    async updateQuestion (questionId, payload) {
      try {
        const { data } = await axios.put(`/admin/questions/${questionId}`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to update question', error)
        return { success: false, message: error.response?.data?.error || 'Failed to update question' }
      }
    },

    // Delete a question
    async deleteQuestion (questionId) {
      try {
        const { data } = await axios.delete(`/admin/questions/${questionId}`)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to delete question', error)
        return { success: false, message: error.response?.data?.error || 'Failed to delete question' }
      }
    },

    // DASHBOARD MANAGEMENT
    // Fetch dashboard statistics
    async fetchDashboardStats () {
      this.loading = true
      try {
        const { data } = await axios.get('/admin/dashboard')
        this.stats = data.stats
        this.recentAttempts = data.recent_attempts
        this.recentUsers = data.recent_users
        this.chartData = data.chart_data
      } catch (error) {
        console.error('Failed to load dashboard stats', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // USER MANAGEMENT
    // Fetch all users with pagination
    async fetchUsers (page = 1, search = '') {
      this.loading = true
      try {
        const params = new URLSearchParams({
          page: page.toString(),
          per_page: '10'
        })

        if (search.trim()) {
          params.append('search', search.trim())
        }

        const { data } = await axios.get(`/admin/users?${params}`)
        this.users = data.users
        return data.pagination
      } catch (error) {
        console.error('Failed to load users', error)
        throw new Error(error.response?.data?.error || 'Failed to load users')
      } finally {
        this.loading = false
      }
    },

    // Toggle user status (active/inactive)
    async toggleUserStatus (userId) {
      try {
        const { data } = await axios.post(`/admin/users/${userId}/toggle-status`)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to toggle user status', error)
        return { success: false, message: error.response?.data?.error || 'Failed to toggle user status' }
      }
    },

    // Update user information
    async updateUser (userId, payload) {
      try {
        const { data } = await axios.put(`/admin/users/${userId}/edit`, payload)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to update user', error)
        return { success: false, message: error.response?.data?.error || 'Failed to update user' }
      }
    },

    // Delete user
    async deleteUser (userId) {
      try {
        const { data } = await axios.delete(`/admin/users/${userId}`)
        return { success: true, message: data.message }
      } catch (error) {
        console.error('Failed to delete user', error)
        return { success: false, message: error.response?.data?.error || 'Failed to delete user' }
      }
    },

    // Export users data
    async exportUsers () {
      try {
        const response = await axios.post('/admin/export/users')

        if (response.data.success) {
          return { success: true, message: response.data.message }
        } else {
          return { success: false, message: response.data.message || 'Export failed' }
        }
      } catch (error) {
        console.error('Failed to export users', error)
        return { success: false, message: error.response?.data?.error || 'Failed to export users' }
      }
    }
  }
})
