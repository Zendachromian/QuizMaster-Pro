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
                    <a href="#" class="text-decoration-none">Quizzes</a>
                  </li>
                  <li class="breadcrumb-item active">Statistics</li>
                </ol>
              </nav>
              <h2 class="mb-0">
                <i class="bi bi-bar-chart-fill me-2 text-success"></i>
                Quiz Statistics
              </h2>
              <p class="text-muted mb-0">Detailed analytics for {{ stats?.quiz?.title }}</p>
            </div>
            <button
              class="btn btn-outline-primary"
              @click="loadStats"
              :disabled="loading"
            >
              <i class="bi bi-arrow-clockwise me-1"></i>
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
        <p class="mt-2 text-muted">Loading quiz statistics...</p>
      </div>

      <!-- Statistics Content -->
      <div v-else-if="stats" class="row">
        <!-- Quiz Overview Card -->
        <div class="col-12 mb-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">
                <i class="bi bi-info-circle me-2"></i>
                Quiz Overview
              </h5>
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-8">
                  <h5>{{ stats.quiz.title }}</h5>
                  <p class="text-muted">{{ stats.quiz.description || 'No description provided' }}</p>
                  <div class="row g-3">
                    <div class="col-auto">
                      <small class="text-muted d-block">Duration</small>
                      <strong>{{ stats.quiz.time_duration }} minutes</strong>
                    </div>
                    <div class="col-auto">
                      <small class="text-muted d-block">Max Attempts</small>
                      <strong>{{ stats.quiz.max_attempts }}</strong>
                    </div>
                    <div class="col-auto">
                      <small class="text-muted d-block">Passing Score</small>
                      <strong>{{ stats.quiz.passing_score }}%</strong>
                    </div>
                    <div class="col-auto">
                      <small class="text-muted d-block">Questions</small>
                      <strong>{{ stats.quiz.question_count || 0 }}</strong>
                    </div>
                  </div>
                </div>
                <div class="col-md-4 text-md-end">
                  <small class="text-muted d-block">Quiz Date</small>
                  <strong>{{ formatDateTime(stats.quiz.date_of_quiz) }}</strong>
                  <div class="mt-2">
                    <span
                      class="badge fs-6"
                      :class="getQuizStatusBadgeClass(stats.quiz)"
                    >
                      {{ getQuizStatus(stats.quiz) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Key Metrics Cards -->
        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card border-0 shadow-sm bg-primary text-white">
            <div class="card-body text-center">
              <i class="bi bi-people display-4 mb-3"></i>
              <h3 class="mb-1">{{ stats.total_attempts }}</h3>
              <p class="mb-0">Total Attempts</p>
            </div>
          </div>
        </div>

        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card border-0 shadow-sm bg-success text-white">
            <div class="card-body text-center">
              <i class="bi bi-graph-up display-4 mb-3"></i>
              <h3 class="mb-1">{{ stats.average_score }}%</h3>
              <p class="mb-0">Average Score</p>
            </div>
          </div>
        </div>

        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card border-0 shadow-sm bg-warning text-white">
            <div class="card-body text-center">
              <i class="bi bi-trophy display-4 mb-3"></i>
              <h3 class="mb-1">{{ stats.pass_rate }}%</h3>
              <p class="mb-0">Pass Rate</p>
            </div>
          </div>
        </div>

        <div class="col-lg-3 col-md-6 mb-4">
          <div class="card border-0 shadow-sm bg-info text-white">
            <div class="card-body text-center">
              <i class="bi bi-award display-4 mb-3"></i>
              <h3 class="mb-1">{{ stats.highest_score }}%</h3>
              <p class="mb-0">Highest Score</p>
            </div>
          </div>
        </div>

        <!-- Score Distribution Chart -->
        <div class="col-lg-8 mb-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-light">
              <h5 class="mb-0">
                <i class="bi bi-bar-chart me-2"></i>
                Score Distribution
              </h5>
            </div>
            <div class="card-body">
              <div v-if="stats.total_attempts === 0" class="text-center py-4">
                <i class="bi bi-graph-up display-4 text-muted mb-3"></i>
                <p class="text-muted">No data available yet</p>
              </div>
              <div v-else>
                <canvas ref="scoreChart" width="400" height="200"></canvas>
              </div>
            </div>
          </div>
        </div>

        <!-- Performance Summary -->
        <div class="col-lg-4 mb-4">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-light">
              <h5 class="mb-0">
                <i class="bi bi-speedometer2 me-2"></i>
                Performance Summary
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <small class="text-muted">Highest Score</small>
                  <strong class="text-success">{{ stats.highest_score }}%</strong>
                </div>
                <div class="progress" style="height: 8px;">
                  <div
                    class="progress-bar bg-success"
                    :style="{ width: stats.highest_score + '%' }"
                  ></div>
                </div>
              </div>

              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <small class="text-muted">Average Score</small>
                  <strong class="text-primary">{{ stats.average_score }}%</strong>
                </div>
                <div class="progress" style="height: 8px;">
                  <div
                    class="progress-bar bg-primary"
                    :style="{ width: stats.average_score + '%' }"
                  ></div>
                </div>
              </div>

              <div class="mb-3">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <small class="text-muted">Lowest Score</small>
                  <strong class="text-danger">{{ stats.lowest_score }}%</strong>
                </div>
                <div class="progress" style="height: 8px;">
                  <div
                    class="progress-bar bg-danger"
                    :style="{ width: stats.lowest_score + '%' }"
                  ></div>
                </div>
              </div>

              <hr>

              <div class="row g-2">
                <div class="col-6 text-center">
                  <div class="h5 text-success mb-1">{{ passedStudents }}</div>
                  <small class="text-muted">Passed</small>
                </div>
                <div class="col-6 text-center">
                  <div class="h5 text-danger mb-1">{{ failedStudents }}</div>
                  <small class="text-muted">Failed</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Score Ranges Table -->
        <div class="col-12">
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-light">
              <h5 class="mb-0">
                <i class="bi bi-table me-2"></i>
                Detailed Score Breakdown
              </h5>
            </div>
            <div class="card-body">
              <div v-if="stats.total_attempts === 0" class="text-center py-4">
                <i class="bi bi-table display-4 text-muted mb-3"></i>
                <p class="text-muted">No quiz attempts to analyze</p>
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover align-middle">
                  <thead class="table-light">
                    <tr>
                      <th>Score Range</th>
                      <th>Number of Students</th>
                      <th>Percentage</th>
                      <th>Performance Level</th>
                      <th>Visual</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="range in stats.score_distribution" :key="range.range">
                      <td><strong>{{ range.range }}%</strong></td>
                      <td>{{ range.count }}</td>
                      <td>{{ range.percentage }}%</td>
                      <td>
                        <span
                          class="badge"
                          :class="getPerformanceBadgeClass(range.range)"
                        >
                          {{ getPerformanceLabel(range.range) }}
                        </span>
                      </td>
                      <td>
                        <div class="progress" style="height: 20px; width: 100px;">
                          <div
                            class="progress-bar"
                            :class="getPerformanceProgressClass(range.range)"
                            :style="{ width: range.percentage + '%' }"
                          >
                            <small>{{ range.percentage }}%</small>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-5">
        <i class="bi bi-graph-up display-1 text-muted mb-3"></i>
        <h5 class="text-muted">No statistics available</h5>
        <p class="text-muted">Statistics will appear here once students start taking the quiz.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { toast } from '@/utils/toast'
import { useAdminStore } from '@/stores/admin'
import AppLayout from '@/components/AppLayout.vue'
import Chart from 'chart.js/auto'

export default {
  name: 'QuizStats',
  components: { AppLayout },
  setup () {
    const route = useRoute()
    const adminStore = useAdminStore()

    // Reactive data
    const loading = ref(false)
    const stats = ref(null)
    const scoreChart = ref(null)
    let chartInstance = null

    // Computed
    const passedStudents = computed(() => {
      if (!stats.value) return 0
      return Math.round((stats.value.pass_rate / 100) * stats.value.total_attempts)
    })

    const failedStudents = computed(() => {
      if (!stats.value) return 0
      return stats.value.total_attempts - passedStudents.value
    })

    // Methods
    const loadStats = async () => {
      try {
        loading.value = true
        const quizId = route.params.id
        const data = await adminStore.fetchQuizStats(quizId)
        stats.value = data

        // Create chart after data is loaded
        await nextTick()
        createScoreChart()
      } catch (error) {
        toast.error('Failed to load quiz statistics')
      } finally {
        loading.value = false
      }
    }

    const createScoreChart = () => {
      if (!stats.value || !scoreChart.value) return

      // Destroy existing chart
      if (chartInstance) {
        chartInstance.destroy()
      }

      const ctx = scoreChart.value.getContext('2d')
      const distribution = stats.value.score_distribution

      chartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: distribution.map(d => d.range + '%'),
          datasets: [{
            label: 'Number of Students',
            data: distribution.map(d => d.count),
            backgroundColor: [
              '#dc3545', // 0-20 - Red
              '#fd7e14', // 21-40 - Orange
              '#ffc107', // 41-60 - Yellow
              '#28a745', // 61-80 - Green
              '#007bff' // 81-100 - Blue
            ],
            borderColor: [
              '#dc3545',
              '#fd7e14',
              '#ffc107',
              '#28a745',
              '#007bff'
            ],
            borderWidth: 1,
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                afterLabel: function (context) {
                  const percentage = distribution[context.dataIndex].percentage
                  return `${percentage}% of total attempts`
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              },
              title: {
                display: true,
                text: 'Number of Students'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Score Range'
              }
            }
          }
        }
      })
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

    const getQuizStatusBadgeClass = (quiz) => {
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

    const getPerformanceLabel = (range) => {
      const [start] = range.split('-').map(Number)
      if (start >= 81) return 'Excellent'
      if (start >= 61) return 'Good'
      if (start >= 41) return 'Average'
      if (start >= 21) return 'Poor'
      return 'Very Poor'
    }

    const getPerformanceBadgeClass = (range) => {
      const [start] = range.split('-').map(Number)
      if (start >= 81) return 'bg-primary'
      if (start >= 61) return 'bg-success'
      if (start >= 41) return 'bg-warning text-dark'
      if (start >= 21) return 'bg-orange'
      return 'bg-danger'
    }

    const getPerformanceProgressClass = (range) => {
      const [start] = range.split('-').map(Number)
      if (start >= 81) return 'bg-primary'
      if (start >= 61) return 'bg-success'
      if (start >= 41) return 'bg-warning'
      if (start >= 21) return 'bg-orange'
      return 'bg-danger'
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return 'Not set'
      return new Date(dateString).toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Lifecycle
    onMounted(async () => {
      await loadStats()
    })

    return {
      // State
      loading,
      stats,
      scoreChart,

      // Computed
      passedStudents,
      failedStudents,

      // Methods
      loadStats,
      getQuizStatus,
      getQuizStatusBadgeClass,
      getPerformanceLabel,
      getPerformanceBadgeClass,
      getPerformanceProgressClass,
      formatDateTime
    }
  }
}
</script>

<style scoped>
.breadcrumb-item a:hover {
  text-decoration: underline !important;
}

.card {
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-2px);
}

.progress {
  background-color: #e9ecef;
}

.table td {
  vertical-align: middle;
}

.bg-orange {
  background-color: #fd7e14 !important;
}

canvas {
  max-height: 300px;
}
</style>
