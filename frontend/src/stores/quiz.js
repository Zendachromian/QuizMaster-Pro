import { defineStore } from 'pinia'
import axios from '@/utils/axios'

export const useQuizStore = defineStore('quiz', {
  state: () => ({
    subjects: [],
    currentSubject: null,
    chapters: [],
    currentChapter: null,
    quizzes: [],
    currentQuiz: null,
    questions: [],
    currentQuestion: 0,
    answers: {},
    timeLeft: 0,
    quizStarted: false,
    quizCompleted: false,
    result: null,
    history: [],
    loading: false
  }),

  getters: {
    totalQuestions: (state) => state.questions.length,
    answeredQuestions: (state) => Object.keys(state.answers).length,
    unansweredQuestions: (state) => state.questions.length - Object.keys(state.answers).length,
    progressPercentage: (state) => {
      if (state.questions.length === 0) return 0
      return Math.round((Object.keys(state.answers).length / state.questions.length) * 100)
    }
  },

  actions: {
    // Subjects
    async fetchSubjects () {
      try {
        this.loading = true
        const response = await axios.get('/subjects')
        this.subjects = response.data.subjects
      } catch (error) {
        console.error('Error fetching subjects:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchSubject (id) {
      try {
        const response = await axios.get(`/subjects/${id}`)
        this.currentSubject = response.data.subject
      } catch (error) {
        console.error('Error fetching subject:', error)
        throw error
      }
    },

    // Chapters
    async fetchChapters (subjectId) {
      try {
        this.loading = true
        const response = await axios.get(`/subjects/${subjectId}/chapters`)
        this.chapters = response.data.chapters
      } catch (error) {
        console.error('Error fetching chapters:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchChapter (id) {
      try {
        const response = await axios.get(`/chapters/${id}`)
        this.currentChapter = response.data.chapter
      } catch (error) {
        console.error('Error fetching chapter:', error)
        throw error
      }
    },

    // Quizzes
    async fetchQuizzes (chapterId) {
      try {
        this.loading = true
        const response = await axios.get(`/chapters/${chapterId}/quizzes`)
        this.quizzes = response.data.quizzes
      } catch (error) {
        console.error('Error fetching quizzes:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async fetchQuiz (id) {
      try {
        const response = await axios.get(`/quizzes/${id}`)
        this.currentQuiz = response.data.quiz
      } catch (error) {
        console.error('Error fetching quiz:', error)
        throw error
      }
    },

    async startQuiz (quizId) {
      try {
        const response = await axios.post(`/quiz/${quizId}/start`)
        const { quiz, questions, attempt_id, time_duration } = response.data

        this.currentQuiz = quiz
        this.questions = questions
        this.currentAttemptId = attempt_id
        this.timeLeft = time_duration * 60 // Convert minutes to seconds
        this.answers = {}
        this.currentQuestion = 0
        this.quizStarted = true
        this.quizCompleted = false

        // Start timer
        this.startTimer()

        return { success: true }
      } catch (error) {
        const message = error.response?.data?.message || 'Failed to start quiz'
        return { success: false, message }
      }
    },

    // Quiz Actions
    selectAnswer (questionId, answer) {
      this.answers[questionId] = answer
    },

    nextQuestion () {
      if (this.currentQuestion < this.questions.length - 1) {
        this.currentQuestion++
      }
    },

    prevQuestion () {
      if (this.currentQuestion > 0) {
        this.currentQuestion--
      }
    },

    goToQuestion (index) {
      if (index >= 0 && index < this.questions.length) {
        this.currentQuestion = index
      }
    },

    async saveAnswer (questionId, selectedOption) {
      try {
        await axios.post(`/attempt/${this.currentAttemptId}/save-answer`, {
          question_id: questionId,
          selected_option: selectedOption
        })

        this.selectAnswer(questionId, selectedOption)
      } catch (error) {
        console.error('Error saving answer:', error)
      }
    },

    async submitQuiz () {
      try {
        const response = await axios.post(`/attempt/${this.currentAttemptId}/submit`)

        this.result = response.data.result
        this.quizCompleted = true
        this.quizStarted = false
        this.stopTimer()

        return { success: true, result: this.result }
      } catch (error) {
        const message = error.response?.data?.message || 'Failed to submit quiz'
        return { success: false, message }
      }
    },

    // Timer functions
    startTimer () {
      this.timer = setInterval(() => {
        if (this.timeLeft > 0) {
          this.timeLeft--
        } else {
          this.submitQuiz()
        }
      }, 1000)
    },

    stopTimer () {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
    },

    // History
    async fetchHistory () {
      try {
        this.loading = true
        const response = await axios.get('/history')
        this.history = response.data.attempts
      } catch (error) {
        console.error('Error fetching history:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    // Analytics
    async fetchAnalytics () {
      try {
        const response = await axios.get('/analytics')
        return response.data.analytics
      } catch (error) {
        console.error('Error fetching analytics:', error)
        throw error
      }
    },

    // Reset quiz state
    resetQuizState () {
      this.currentQuiz = null
      this.questions = []
      this.currentQuestion = 0
      this.answers = {}
      this.timeLeft = 0
      this.quizStarted = false
      this.quizCompleted = false
      this.result = null
      this.stopTimer()
    }
  }
})
