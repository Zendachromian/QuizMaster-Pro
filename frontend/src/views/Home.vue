<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero bg-primary text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-4">
              Master Your Knowledge with QuizMaster Pro
            </h1>
            <p class="lead mb-4">
              The ultimate quiz platform for students, professionals, and knowledge enthusiasts.
              Challenge yourself with interactive quizzes and track your progress.
            </p>
            <div class="d-flex gap-3">
              <router-link
                v-if="!isAuthenticated"
                to="/register"
                class="btn btn-light btn-lg px-4"
              >
                Get Started
              </router-link>
              <router-link
                v-if="!isAuthenticated"
                to="/login"
                class="btn btn-outline-light btn-lg px-4"
              >
                Login
              </router-link>
              <router-link
                v-if="isAuthenticated"
                :to="isAdmin ? '/admin' : '/dashboard'"
                class="btn btn-light btn-lg px-4"
              >
                Go to Dashboard
              </router-link>
            </div>
          </div>
          <div class="col-lg-6 text-center">
            <i class="bi bi-mortarboard" style="font-size: 12rem; opacity: 0.7;"></i>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features py-5">
      <div class="container">
        <div class="text-center mb-5">
          <h2 class="h1 fw-bold">Why Choose QuizMaster Pro?</h2>
          <p class="lead text-muted">Discover the features that make learning engaging and effective</p>
        </div>

        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body text-center p-4">
                <div class="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                     style="width: 80px; height: 80px;">
                  <i class="bi bi-graph-up text-primary" style="font-size: 2rem;"></i>
                </div>
                <h4 class="fw-bold mb-3">Track Progress</h4>
                <p class="text-muted">
                  Monitor your learning journey with detailed analytics and performance insights.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body text-center p-4">
                <div class="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                     style="width: 80px; height: 80px;">
                  <i class="bi bi-clock text-success" style="font-size: 2rem;"></i>
                </div>
                <h4 class="fw-bold mb-3">Timed Quizzes</h4>
                <p class="text-muted">
                  Challenge yourself with time-bound quizzes that simulate real exam conditions.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body text-center p-4">
                <div class="bg-info bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                     style="width: 80px; height: 80px;">
                  <i class="bi bi-award text-info" style="font-size: 2rem;"></i>
                </div>
                <h4 class="fw-bold mb-3">Instant Results</h4>
                <p class="text-muted">
                  Get immediate feedback with detailed explanations for each question.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body text-center p-4">
                <div class="bg-warning bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                     style="width: 80px; height: 80px;">
                  <i class="bi bi-people text-warning" style="font-size: 2rem;"></i>
                </div>
                <h4 class="fw-bold mb-3">Multiple Subjects</h4>
                <p class="text-muted">
                  Explore quizzes across various subjects and topics tailored to your interests.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body text-center p-4">
                <div class="bg-danger bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                     style="width: 80px; height: 80px;">
                  <i class="bi bi-shield-check text-danger" style="font-size: 2rem;"></i>
                </div>
                <h4 class="fw-bold mb-3">Secure Platform</h4>
                <p class="text-muted">
                  Your data and progress are safely stored with enterprise-grade security.
                </p>
              </div>
            </div>
          </div>

          <div class="col-md-4">
            <div class="card h-100 shadow-sm border-0">
              <div class="card-body text-center p-4">
                <div class="bg-purple bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3"
                     style="width: 80px; height: 80px;">
                  <i class="bi bi-phone text-primary" style="font-size: 2rem;"></i>
                </div>
                <h4 class="fw-bold mb-3">Mobile Friendly</h4>
                <p class="text-muted">
                  Take quizzes anywhere, anytime with our responsive design that works on all devices.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Statistics Section -->
    <section class="stats bg-light py-5">
      <div class="container">
        <div class="row text-center">
          <div class="col-md-3 mb-4">
            <div class="stat-item">
              <h2 class="display-4 fw-bold text-primary mb-2">1000+</h2>
              <p class="lead mb-0">Active Users</p>
            </div>
          </div>
          <div class="col-md-3 mb-4">
            <div class="stat-item">
              <h2 class="display-4 fw-bold text-success mb-2">500+</h2>
              <p class="lead mb-0">Quizzes Available</p>
            </div>
          </div>
          <div class="col-md-3 mb-4">
            <div class="stat-item">
              <h2 class="display-4 fw-bold text-warning mb-2">50+</h2>
              <p class="lead mb-0">Subject Areas</p>
            </div>
          </div>
          <div class="col-md-3 mb-4">
            <div class="stat-item">
              <h2 class="display-4 fw-bold text-info mb-2">10k+</h2>
              <p class="lead mb-0">Quiz Attempts</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta py-5">
      <div class="container text-center">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <h2 class="display-5 fw-bold mb-4">Ready to Start Learning?</h2>
            <p class="lead mb-4">
              Join thousands of learners who are already improving their knowledge with QuizMaster Pro.
            </p>
            <router-link
              v-if="!isAuthenticated"
              to="/register"
              class="btn btn-primary btn-lg px-5"
            >
              Join Now - It's Free!
            </router-link>
            <router-link
              v-if="isAuthenticated"
              :to="isAdmin ? '/admin/subjects' : '/subjects'"
              class="btn btn-primary btn-lg px-5"
            >
              Explore Subjects
            </router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'Home',
  setup () {
    const authStore = useAuthStore()

    const isAuthenticated = computed(() => authStore.isAuthenticated)
    const isAdmin = computed(() => authStore.isAdmin)

    return {
      isAuthenticated,
      isAdmin
    }
  }
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, var(--bs-primary), #0056b3);
}

.stat-item {
  position: relative;
}

.stat-item::before {
  content: '';
  position: absolute;
  top: 50%;
  right: 0;
  width: 1px;
  height: 60%;
  background: #dee2e6;
  transform: translateY(-50%);
}

.stat-item:last-child::before {
  display: none;
}

@media (max-width: 768px) {
  .stat-item::before {
    display: none;
  }
}
</style>
