import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Import views
import Home from '@/views/Home.vue'
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import Dashboard from '@/views/user/Dashboard.vue'
import AdminDashboard from '@/views/admin/Dashboard.vue'
import Subjects from '@/views/user/Subjects.vue'
import SubjectChapters from '@/views/user/SubjectChapters.vue'
import Quiz from '@/views/user/Quiz.vue'
import Analytics from '@/views/user/Analytics.vue'
import AdminSubjects from '@/views/admin/Subjects.vue'
import AdminUsers from '@/views/admin/Users.vue'
import Profile from '@/views/Profile.vue'
import TakeQuiz from '@/views/user/TakeQuiz.vue'
import QuizResult from '@/views/user/QuizResult.vue'
import QuizHistory from '@/views/user/QuizHistory.vue'

// Import placeholder components for routes not yet implemented
import {
  ChapterQuizzes,
  CreateSubject, CreateChapter, CreateQuiz
} from '@/components/PlaceholderViews.js'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: false }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false, hideForAuth: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresAuth: false, hideForAuth: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/subjects',
    name: 'Subjects',
    component: Subjects,
    meta: { requiresAuth: true }
  },
  {
    path: '/subjects/:id/chapters',
    name: 'SubjectChapters',
    component: SubjectChapters,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz',
    name: 'Quiz',
    component: Quiz,
    meta: { requiresAuth: true }
  },
  {
    path: '/analytics',
    name: 'Analytics',
    component: Analytics,
    meta: { requiresAuth: true }
  },
  {
    path: '/chapters/:id/quizzes',
    name: 'ChapterQuizzes',
    component: ChapterQuizzes,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz/:id/take',
    name: 'TakeQuiz',
    component: TakeQuiz,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz/:id/result',
    name: 'QuizResult',
    component: QuizResult,
    meta: { requiresAuth: true }
  },
  {
    path: '/quiz-history',
    name: 'QuizHistory',
    component: QuizHistory,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  // Admin routes
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects',
    name: 'AdminSubjects',
    component: AdminSubjects,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/subjects/:id/chapters',
    name: 'AdminChapters',
    component: () => import('@/views/admin/Chapters.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/chapters/:id/quizzes',
    name: 'AdminQuizzes',
    component: () => import('@/views/admin/Quizzes.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes',
    name: 'AdminQuizList',
    component: () => import('@/views/admin/Quizzes.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/:id/questions',
    name: 'AdminQuestions',
    component: () => import('@/views/admin/Questions.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/quizzes/:id/stats',
    name: 'QuizStats',
    component: () => import('@/views/admin/QuizStats.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: AdminUsers,
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  // Catch-all route for 404
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior (to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Wait for auth initialization to complete if not already done
  if (!authStore.initialized) {
    try {
      await authStore.initializeAuth()
    } catch (error) {
      console.error('Auth initialization failed in router:', error)
    }
  }

  // For routes that require authentication, check if we have at least a token
  // Even if user data failed to load, allow access if we have a token
  const hasValidToken = !!authStore.token
  const isFullyAuthenticated = authStore.isAuthenticated

  // Check if route requires authentication
  if (to.meta.requiresAuth && !hasValidToken) {
    next('/login')
    return
  }

  // Check if route requires admin access - need full authentication for this
  if (to.meta.requiresAdmin && (!isFullyAuthenticated || !authStore.isAdmin)) {
    // If we have a token but no user data, allow access and let the page handle it
    if (hasValidToken && !authStore.user) {
      next()
      return
    }
    next('/dashboard')
    return
  }

  // Hide auth pages from authenticated users
  if (to.meta.hideForAuth && (isFullyAuthenticated || hasValidToken)) {
    if (authStore.isAdmin || (hasValidToken && !authStore.user)) {
      next('/admin')
    } else {
      next('/dashboard')
    }
    return
  }

  next()
})

export default router
