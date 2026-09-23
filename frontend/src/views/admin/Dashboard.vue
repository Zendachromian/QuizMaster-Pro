<template>
  <AppLayout>
    <div class="container-fluid">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">Admin Dashboard</h1>
              <p class="text-muted">Monitor system activity and manage your platform</p>
            </div>
            <div>
              <button class="btn btn-outline-primary me-2" @click="refreshData" :disabled="loading">
                <i class="bi bi-arrow-clockwise me-1"></i>
                {{ loading ? 'Loading...' : 'Refresh' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistics Cards -->
      <div class="row mb-4">
        <div class="col-md-2-4 mb-3">
          <div class="card h-100 stats-card-no-hover border-primary">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-primary">
                <i class="bi bi-people"></i>
              </div>
              <h3 class="mb-1 text-primary">{{ stats.total_users || 0 }}</h3>
              <p class="mb-0 small text-muted">Active Users</p>
            </div>
          </div>
        </div>

        <div class="col-md-2-4 mb-3">
          <div class="card h-100 stats-card-no-hover border-success">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-success">
                <i class="bi bi-book"></i>
              </div>
              <h3 class="mb-1 text-success">{{ stats.total_subjects || 0 }}</h3>
              <p class="mb-0 small text-muted">Subjects</p>
            </div>
          </div>
        </div>

        <div class="col-md-2-4 mb-3">
          <div class="card h-100 stats-card-no-hover border-info">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-info">
                <i class="bi bi-bookmark"></i>
              </div>
              <h3 class="mb-1 text-info">{{ stats.total_chapters || 0 }}</h3>
              <p class="mb-0 small text-muted">Chapters</p>
            </div>
          </div>
        </div>

                <div class="col-xl-2-4 col-md-6 mb-4">
          <div class="card h-100 stats-card-no-hover border-warning">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-warning">
                <i class="bi bi-clock-history"></i>
              </div>
              <h3 class="mb-1 text-warning">{{ stats.averageCompletionTime || 0 }}m</h3>
              <p class="mb-0 small text-muted">Avg. Completion Time</p>
            </div>
          </div>
        </div>

        <div class="col-md-2-4 mb-3">
          <div class="card h-100 stats-card-no-hover border-danger">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-danger">
                <i class="bi bi-graph-up"></i>
              </div>
              <h3 class="mb-1 text-danger">{{ stats.total_attempts || 0 }}</h3>
              <p class="mb-0 small text-muted">Total Attempts</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div class="row mb-4">
        <!-- User Registration Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white text-dark">
              <h5 class="mb-0 text-dark">
                <i class="bi bi-graph-up me-2 text-primary"></i>User Registration Trends
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="userRegistrationChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Quiz Completion Rate Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white text-dark">
              <h5 class="mb-0 text-dark">
                <i class="bi bi-pie-chart me-2 text-success"></i>Quiz Completion Rates
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="completionRateChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Subject Popularity Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white text-dark">
              <h5 class="mb-0 text-dark">
                <i class="bi bi-bar-chart me-2 text-warning"></i>Subject Popularity
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="subjectPopularityChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Score Distribution Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white">
              <h5 class="mb-0">
                <i class="bi bi-speedometer2 me-2 text-info"></i>Score Distribution
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="scoreDistributionChart" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Additional Charts Section -->
      <div class="row mb-4">
        <!-- Activity Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white">
              <h5 class="mb-0">
                <i class="bi bi-activity me-2 text-primary"></i>Daily Activity Overview
              </h5>
              <small class="text-muted">Quiz attempts over the last 30 days</small>
            </div>
            <div class="card-body">
              <canvas ref="dailyActivityChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Performance Distribution Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white">
              <h5 class="mb-0">
                <i class="bi bi-graph-down me-2 text-success"></i>Performance Distribution
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="performanceDistributionChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Qualification Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white">
              <h5 class="mb-0">
                <i class="bi bi-mortarboard me-2 text-warning"></i>User Qualifications
              </h5>
              <small class="text-muted">Distribution of user educational backgrounds</small>
            </div>
            <div class="card-body">
              <canvas ref="qualificationChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Quiz Results Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 chart-white-bg">
            <div class="card-header bg-white">
              <h5 class="mb-0">
                <i class="bi bi-trophy me-2 text-success"></i>Quiz Results Overview
              </h5>
              <small class="text-muted">Pass/fail distribution of quiz attempts</small>
            </div>
            <div class="card-body">
              <canvas ref="quizResultsChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Subject Performance Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100">
            <div class="card-header bg-white">
              <h5 class="mb-0">
                <i class="bi bi-trophy me-2 text-info"></i>Subject Performance Metrics
              </h5>
            </div>
            <div class="card-body">
              <canvas ref="subjectPerformanceChart" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Recent Quiz Attempts -->
        <div class="col-lg-8 mb-4">
          <div class="card h-100">
            <div class="card-header bg-white">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 text-white">
                  <i class="bi bi-activity me-2 text-primary"></i>Recent Quiz Attempts
                </h5>
                <router-link to="/admin/quizzes" class="btn btn-sm btn-outline-primary">
                  View All
                </router-link>
              </div>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="mt-2 text-muted">Loading recent attempts...</p>
              </div>

              <div v-else-if="recentAttempts.length === 0" class="text-center py-4">
                <i class="bi bi-inbox display-4 text-muted"></i>
                <p class="mt-3 text-muted">No quiz attempts yet.</p>
              </div>

              <div v-else class="table-responsive">
                <table class="table table-hover">
                  <thead class="table-light">
                    <tr>
                      <th>User</th>
                      <th>Quiz</th>
                      <th>Score</th>
                      <th>Date</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="attempt in recentAttempts" :key="attempt.id">
                      <td>
                        <strong class="text-white">{{ attempt.user?.full_name || 'Unknown User' }}</strong>
                        <br>
                        <small class="text-muted">{{ attempt.user?.email }}</small>
                      </td>
                      <td>
                        <strong class="text-white">{{ truncateText(attempt.quiz_title, 25) }}</strong>
                        <br>
                        <small class="text-white">{{ attempt.subject_name }}</small>
                      </td>
                      <td>
                        <span :class="`badge ${getScoreClass(attempt.score_percentage)}`">
                          {{ attempt.score_percentage }}%
                        </span>
                      </td>
                      <td>
                        <small class="text-white">{{ formatDateTime(attempt.end_time) }}</small>
                      </td>
                      <td>
                        <span :class="`badge ${attempt.score_percentage >= 60 ? 'bg-success' : 'bg-danger'}`">
                          {{ attempt.score_percentage >= 60 ? 'Passed' : 'Failed' }}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Users -->
        <div class="col-lg-4 mb-4">
          <div class="card h-100 no-hover-effect">
            <div class="card-header bg-white no-hover-effect">
              <div class="d-flex justify-content-between align-items-center">
                <h5 class="mb-0 text-white">
                  <i class="bi bi-person-plus me-2 text-success"></i>Recent Users
                </h5>
                <router-link to="/admin/users" class="btn btn-sm btn-outline-success">
                  View All
                </router-link>
              </div>
            </div>
            <div class="card-body">
              <div v-if="loading" class="text-center py-4">
                <div class="loading-spinner"></div>
                <p class="mt-2 text-muted">Loading recent users...</p>
              </div>

              <div v-else-if="recentUsers.length === 0" class="text-center py-4">
                <i class="bi bi-people display-4 text-muted"></i>
                <p class="mt-3 text-muted">No users registered yet.</p>
              </div>

              <div v-else>
                <div
                  v-for="user in recentUsers.slice(0, 6)"
                  :key="user.id"
                  class="d-flex justify-content-between align-items-center border-bottom py-3"
                >
                  <div>
                    <strong class="text-white">{{ user.full_name }}</strong>
                    <br>
                    <small class="text-muted">{{ user.email }}</small>
                    <br>
                    <small class="text-white">
                      {{ user.qualification || 'No qualification' }}
                    </small>
                    <br>
                    <small class="text-white">
                      Joined {{ formatDate(user.created_at) }}
                    </small>
                  </div>
                  <div class="text-end">
                    <span :class="`badge ${user.is_active ? 'bg-success' : 'bg-danger'} mb-1`">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                    <br>
                    <small class="text-muted">
                      {{ (user.quiz_attempts || 0) }} attempts
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header bg-white">
              <h5 class="mb-0 text-white">
                <i class="bi bi-lightning me-2 text-warning"></i>Quick Actions
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-3 mb-3">
                  <router-link to="/admin/subjects" class="btn btn-outline-success w-100 h-100 d-flex flex-column justify-content-center text-decoration-none">
                    <i class="bi bi-book display-6 mb-2"></i>
                    <span>Manage Subjects</span>
                  </router-link>
                </div>
                <div class="col-md-3 mb-3">
                  <router-link to="/admin/users" class="btn btn-outline-info w-100 h-100 d-flex flex-column justify-content-center text-decoration-none">
                    <i class="bi bi-people display-6 mb-2"></i>
                    <span>Manage Users</span>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'
import { formatDateTime, formatDate, truncateText, getScoreClass } from '@/utils/helpers'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
)

export default {
  name: 'AdminDashboard',
  components: {
    AppLayout
  },
  setup () {
    const adminStore = useAdminStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const stats = ref({})
    const recentAttempts = ref([])
    const recentUsers = ref([])
    const chartData = ref({})

    // Chart references
    const userRegistrationChart = ref(null)
    const completionRateChart = ref(null)
    const subjectPopularityChart = ref(null)
    const scoreDistributionChart = ref(null)
    const performanceDistributionChart = ref(null)
    const qualificationChart = ref(null)
    const quizResultsChart = ref(null)
    const subjectPerformanceChart = ref(null)
    const dailyActivityChart = ref(null)

    // Chart instances
    let userRegistrationChartInstance = null
    let completionRateChartInstance = null
    let subjectPopularityChartInstance = null
    let scoreDistributionChartInstance = null
    let performanceDistributionChartInstance = null
    let qualificationChartInstance = null
    let quizResultsChartInstance = null
    let subjectPerformanceChartInstance = null
    let dailyActivityChartInstance = null

    const loadDashboardData = async () => {
      try {
        loading.value = true
        await adminStore.fetchDashboardStats()

        stats.value = adminStore.stats
        recentAttempts.value = adminStore.recentAttempts
        recentUsers.value = adminStore.recentUsers
        chartData.value = adminStore.chartData

        // Create charts after data is loaded
        await createAllCharts()
      } catch (error) {
        console.error('Error loading dashboard data:', error)
        notificationStore.error('Failed to load dashboard data')
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadDashboardData()
    }

    // Chart creation functions
    const createUserRegistrationChart = () => {
      if (!userRegistrationChart.value) return

      const ctx = userRegistrationChart.value.getContext('2d')

      // Destroy existing chart if it exists
      if (userRegistrationChartInstance) {
        userRegistrationChartInstance.destroy()
      }

      // Sample data - you can replace this with real data from your API
      if (!chartData.value?.user_registration) return

      userRegistrationChartInstance = new ChartJS(ctx, {
        type: 'line',
        data: {
          labels: chartData.value.user_registration.labels,
          datasets: [{
            label: 'New Users',
            data: chartData.value.user_registration.data,
            borderColor: 'rgb(54, 162, 235)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            tension: 0.4,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    const createDailyActivityChart = () => {
      if (!dailyActivityChart.value) return

      const ctx = dailyActivityChart.value.getContext('2d')

      if (dailyActivityChartInstance) {
        dailyActivityChartInstance.destroy()
      }

      if (!chartData.value?.activity?.data) return

      // Get last 30 days of activity data
      const activityData = chartData.value.activity.data
      const recentData = activityData.slice(-30)

      const labels = recentData.map(item => {
        const date = new Date(item.date)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      })
      const data = recentData.map(item => item.count)

      dailyActivityChartInstance = new ChartJS(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Quiz Attempts',
            data,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(59, 130, 246)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          scales: {
            x: {
              display: true,
              grid: {
                display: false
              }
            },
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1,
                callback: function (value) {
                  return Math.floor(value) === value ? value : ''
                }
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                title: function (context) {
                  const dataIndex = context[0].dataIndex
                  const originalDate = recentData[dataIndex].date
                  const date = new Date(originalDate)
                  return date.toLocaleDateString('en-US', {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  })
                },
                label: function (context) {
                  const attempts = context.parsed.y
                  return `Quiz Attempts: ${attempts}`
                }
              }
            }
          }
        }
      })
    }

    const createCompletionRateChart = () => {
      if (!completionRateChart.value) return

      const ctx = completionRateChart.value.getContext('2d')

      if (completionRateChartInstance) {
        completionRateChartInstance.destroy()
      }

      if (!chartData.value?.completion_rates) return

      completionRateChartInstance = new ChartJS(ctx, {
        type: 'doughnut',
        data: {
          labels: chartData.value.completion_rates.labels,
          datasets: [{
            data: chartData.value.completion_rates.data,
            backgroundColor: [
              'rgba(34, 197, 94, 0.8)',
              'rgba(239, 68, 68, 0.8)',
              'rgba(251, 191, 36, 0.8)'
            ],
            borderColor: [
              'rgb(34, 197, 94)',
              'rgb(239, 68, 68)',
              'rgb(251, 191, 36)'
            ],
            borderWidth: 2
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

    const createSubjectPopularityChart = () => {
      if (!subjectPopularityChart.value) return

      const ctx = subjectPopularityChart.value.getContext('2d')

      if (subjectPopularityChartInstance) {
        subjectPopularityChartInstance.destroy()
      }

      if (!chartData.value?.subject_popularity) return

      subjectPopularityChartInstance = new ChartJS(ctx, {
        type: 'bar',
        data: {
          labels: chartData.value.subject_popularity.labels,
          datasets: [{
            label: 'Quiz Attempts',
            data: chartData.value.subject_popularity.data,
            backgroundColor: [
              'rgba(59, 130, 246, 0.8)',
              'rgba(34, 197, 94, 0.8)',
              'rgba(251, 191, 36, 0.8)',
              'rgba(168, 85, 247, 0.8)',
              'rgba(239, 68, 68, 0.8)'
            ],
            borderColor: [
              'rgb(59, 130, 246)',
              'rgb(34, 197, 94)',
              'rgb(251, 191, 36)',
              'rgb(168, 85, 247)',
              'rgb(239, 68, 68)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    const createScoreDistributionChart = () => {
      if (!scoreDistributionChart.value) return

      const ctx = scoreDistributionChart.value.getContext('2d')

      if (scoreDistributionChartInstance) {
        scoreDistributionChartInstance.destroy()
      }

      if (!chartData.value?.score_distribution) return

      scoreDistributionChartInstance = new ChartJS(ctx, {
        type: 'bar',
        data: {
          labels: chartData.value.score_distribution.labels,
          datasets: [{
            label: 'Number of Students',
            data: chartData.value.score_distribution.data,
            backgroundColor: [
              'rgba(239, 68, 68, 0.8)',
              'rgba(251, 191, 36, 0.8)',
              'rgba(59, 130, 246, 0.8)',
              'rgba(34, 197, 94, 0.8)',
              'rgba(16, 185, 129, 0.8)'
            ],
            borderColor: [
              'rgb(239, 68, 68)',
              'rgb(251, 191, 36)',
              'rgb(59, 130, 246)',
              'rgb(34, 197, 94)',
              'rgb(16, 185, 129)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 5
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    const createAllCharts = async () => {
      await nextTick()
      createUserRegistrationChart()
      createDailyActivityChart()
      createCompletionRateChart()
      createSubjectPopularityChart()
      createScoreDistributionChart()
      createPerformanceDistributionChart()
      createQualificationChart()
      createQuizResultsChart()
      createSubjectPerformanceChart()
    }

    // Additional chart creation functions
    const createQualificationChart = () => {
      if (!qualificationChart.value) return

      const ctx = qualificationChart.value.getContext('2d')

      if (qualificationChartInstance) {
        qualificationChartInstance.destroy()
      }

      if (!chartData.value?.qualifications) return

      qualificationChartInstance = new ChartJS(ctx, {
        type: 'doughnut',
        data: {
          labels: chartData.value.qualifications.labels,
          datasets: [{
            data: chartData.value.qualifications.data,
            backgroundColor: [
              'rgba(59, 130, 246, 0.8)',
              'rgba(34, 197, 94, 0.8)',
              'rgba(251, 191, 36, 0.8)',
              'rgba(239, 68, 68, 0.8)',
              'rgba(168, 85, 247, 0.8)',
              'rgba(16, 185, 129, 0.8)',
              'rgba(245, 101, 101, 0.8)',
              'rgba(139, 92, 246, 0.8)'
            ],
            borderColor: [
              'rgb(59, 130, 246)',
              'rgb(34, 197, 94)',
              'rgb(251, 191, 36)',
              'rgb(239, 68, 68)',
              'rgb(168, 85, 247)',
              'rgb(16, 185, 129)',
              'rgb(245, 101, 101)',
              'rgb(139, 92, 246)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 15,
                usePointStyle: true
              }
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || ''
                  const value = context.raw
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = ((value / total) * 100).toFixed(1)
                  return `${label}: ${value} users (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }

    const createQuizResultsChart = () => {
      if (!quizResultsChart.value) return

      const ctx = quizResultsChart.value.getContext('2d')

      if (quizResultsChartInstance) {
        quizResultsChartInstance.destroy()
      }

      if (!chartData.value?.quiz_qualifications) return

      quizResultsChartInstance = new ChartJS(ctx, {
        type: 'pie',
        data: {
          labels: chartData.value.quiz_qualifications.labels,
          datasets: [{
            data: chartData.value.quiz_qualifications.data,
            backgroundColor: [
              'rgba(34, 197, 94, 0.8)',
              'rgba(239, 68, 68, 0.8)'
            ],
            borderColor: [
              'rgb(34, 197, 94)',
              'rgb(239, 68, 68)'
            ],
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 15,
                usePointStyle: true
              }
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const label = context.label || ''
                  const value = context.raw
                  const total = context.dataset.data.reduce((a, b) => a + b, 0)
                  const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
                  return `${label}: ${value} attempts (${percentage}%)`
                }
              }
            }
          }
        }
      })
    }

    const createPerformanceDistributionChart = () => {
      if (!performanceDistributionChart.value) return

      const ctx = performanceDistributionChart.value.getContext('2d')

      if (performanceDistributionChartInstance) {
        performanceDistributionChartInstance.destroy()
      }

      if (!chartData.value?.performance_metrics) return

      performanceDistributionChartInstance = new ChartJS(ctx, {
        type: 'radar',
        data: {
          labels: chartData.value.performance_metrics.labels,
          datasets: [{
            label: 'Average Performance',
            data: chartData.value.performance_metrics.data,
            backgroundColor: 'rgba(168, 85, 247, 0.2)',
            borderColor: 'rgb(168, 85, 247)',
            pointBackgroundColor: 'rgb(168, 85, 247)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(168, 85, 247)'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            r: {
              beginAtZero: true,
              max: 100
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    const createSubjectPerformanceChart = () => {
      if (!subjectPerformanceChart.value) return

      const ctx = subjectPerformanceChart.value.getContext('2d')

      if (subjectPerformanceChartInstance) {
        subjectPerformanceChartInstance.destroy()
      }

      if (!chartData.value?.subject_performance) return

      subjectPerformanceChartInstance = new ChartJS(ctx, {
        type: 'bar',
        data: {
          labels: chartData.value.subject_performance.labels,
          datasets: [
            {
              label: 'Average Score',
              data: chartData.value.subject_performance.scores,
              backgroundColor: 'rgba(34, 197, 94, 0.8)',
              borderColor: 'rgb(34, 197, 94)',
              borderWidth: 2,
              yAxisID: 'y'
            },
            {
              label: 'Pass Rate (%)',
              data: chartData.value.subject_performance.pass_rates,
              backgroundColor: 'rgba(59, 130, 246, 0.8)',
              borderColor: 'rgb(59, 130, 246)',
              borderWidth: 2,
              yAxisID: 'y1'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              type: 'linear',
              display: true,
              position: 'left',
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: 'Average Score'
              }
            },
            y1: {
              type: 'linear',
              display: true,
              position: 'right',
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: 'Pass Rate (%)'
              },
              grid: {
                drawOnChartArea: false
              }
            }
          },
          plugins: {
            legend: {
              position: 'top'
            }
          }
        }
      })
    }

    onMounted(() => {
      loadDashboardData()
    })

    return {
      loading,
      stats,
      recentAttempts,
      recentUsers,
      chartData,
      refreshData,
      formatDateTime,
      formatDate,
      truncateText,
      getScoreClass,
      // Chart refs
      userRegistrationChart,
      completionRateChart,
      subjectPopularityChart,
      scoreDistributionChart,
      performanceDistributionChart,
      qualificationChart,
      quizResultsChart,
      subjectPerformanceChart,
      dailyActivityChart
    }
  }
}
</script>

<style scoped>
.col-md-2-4 {
  flex: 0 0 auto;
  width: 20%;
}

@media (max-width: 768px) {
  .col-md-2-4 {
    width: 100%;
  }
}

.stats-card-icon {
  font-size: 2rem;
  opacity: 0.8;
}

.card {
  border: none;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.08);
  border-radius: 10px;
}

.card-header {
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
  border-radius: 10px 10px 0 0 !important;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.btn-outline-primary:hover,
.btn-outline-success:hover,
.btn-outline-info:hover,
.btn-outline-warning:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
  }
}

/* Chart container styles */
canvas {
  max-height: 300px !important;
}

.card-body canvas {
  width: 100% !important;
  height: 300px !important;
}

/* Chart card styling */
.card-header h5 {
  font-size: 1rem;
  font-weight: 600;
}

.card-header i {
  font-size: 1.1rem;
}
</style>
