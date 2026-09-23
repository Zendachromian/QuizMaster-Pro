<template>
  <AppLayout>
    <div class="container-fluid py-4">
      <!-- Page Header -->
      <div class="row mb-4">
        <div class="col-12">
          <div class="d-flex justify-content-between align-items-center">
            <div>
              <h1 class="h3 mb-1">
                <i class="bi bi-graph-up text-primary me-2"></i>
                Analytics Dashboard
              </h1>
              <p class="text-muted">Track your learning progress and performance insights</p>
            </div>
            <div>
              <button class="btn btn-outline-primary me-2" @click="refreshData" :disabled="loading">
                <i class="bi bi-arrow-clockwise me-1"></i>
                {{ loading ? 'Loading...' : 'Refresh' }}
              </button>
              <button v-if="!authStore.isAdmin" class="btn btn-outline-secondary" @click="exportData">
                <i class="bi bi-download me-1"></i>Export Analytics
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Stats Cards -->
      <div class="row mb-4">
        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-primary">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-primary">
                <i class="bi bi-list-check"></i>
              </div>
              <h3 class="mb-1 text-primary">{{ stats.total_attempts || 0 }}</h3>
              <p class="mb-0 small text-muted">Total Attempts</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-success">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-success">
                <i class="bi bi-trophy"></i>
              </div>
              <h3 class="mb-1 text-success">{{ stats.average_score || 0 }}%</h3>
              <p class="mb-0 small text-muted">Average Score</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-info">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-info">
                <i class="bi bi-star"></i>
              </div>
              <h3 class="mb-1 text-info">{{ stats.best_score || 0 }}%</h3>
              <p class="mb-0 small text-muted">Best Score</p>
            </div>
          </div>
        </div>

        <div class="col-md-3 mb-3">
          <div class="card h-100 stats-card-no-hover border-warning">
            <div class="card-body text-center">
              <div class="stats-card-icon mb-2 text-warning">
                <i class="bi bi-clock-history"></i>
              </div>
              <h3 class="mb-1 text-warning">{{ formatTime(stats.total_time_spent || 0) }}</h3>
              <p class="mb-0 small text-muted">Time Spent</p>
            </div>
          </div>
        </div>
      </div>

      <!-- No Data Message -->
      <div v-if="stats.total_attempts === 0" class="row mb-4">
        <div class="col-12">
          <div class="card">
            <div class="card-body text-center py-5">
              <div class="mb-4">
                <i class="bi bi-graph-up-arrow text-muted" style="font-size: 4rem;"></i>
              </div>
              <h4 class="text-muted mb-3">No Quiz Data Available</h4>
              <p class="text-muted mb-4">
                Start taking some quizzes to see your analytics and progress tracking here.
                <br>Your performance data, progress trends, and insights will appear once you complete some quizzes.
              </p>
              <a href="/subjects" class="btn btn-primary">
                <i class="bi bi-play-circle me-2"></i>Start Taking Quizzes
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Charts Section -->
      <div v-if="stats.total_attempts > 0" class="row mb-4">
        <!-- Activity Chart -->
        <div class="col-lg-12 mb-4">
          <div class="card h-100 no-hover-effect chart-white-bg">
            <div class="card-header bg-white text-dark no-hover-effect">
              <div class="d-flex justify-content-between align-items-center">
                <div>
                  <h5 class="mb-0 text-dark no-hover-effect">
                    <i class="bi bi-activity me-2 text-primary"></i>Daily Activity Overview
                  </h5>
                  <small class="text-muted">Quiz attempts over the last 30 days</small>
                </div>
                <div class="btn-group btn-group-sm" role="group">
                  <input type="radio" class="btn-check" id="activity-30d" v-model="activityPeriod" value="30d">
                  <label class="btn btn-outline-primary" for="activity-30d">30 Days</label>
                  <input type="radio" class="btn-check" id="activity-60d" v-model="activityPeriod" value="60d">
                  <label class="btn btn-outline-primary" for="activity-60d">60 Days</label>
                  <input type="radio" class="btn-check" id="activity-90d" v-model="activityPeriod" value="90d">
                  <label class="btn btn-outline-primary" for="activity-90d">90 Days</label>
                </div>
              </div>
            </div>
            <div class="card-body">
              <canvas ref="dailyActivityChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Performance Distribution Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 no-hover-effect chart-white-bg">
            <div class="card-header bg-white text-dark no-hover-effect">
              <h5 class="mb-0 text-dark no-hover-effect">
                <i class="bi bi-pie-chart me-2 text-success"></i>Score Distribution
              </h5>
              <small class="text-muted">Performance breakdown across all attempts</small>
            </div>
            <div class="card-body">
              <canvas ref="scoreDistributionChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Quiz Status Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 no-hover-effect chart-white-bg">
            <div class="card-header bg-white text-dark no-hover-effect">
              <h5 class="mb-0 text-dark no-hover-effect">
                <i class="bi bi-check-circle me-2 text-primary"></i>Quiz Status Overview
              </h5>
              <small class="text-muted">Attempted, not attempted, and upcoming quizzes</small>
            </div>
            <div class="card-body">
              <canvas ref="quizStatusChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Subject Performance Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 no-hover-effect chart-white-bg">
            <div class="card-header bg-white text-dark no-hover-effect">
              <h5 class="mb-0 text-dark no-hover-effect">
                <i class="bi bi-bar-chart me-2 text-warning"></i>Subject Performance
              </h5>
              <small class="text-muted">Average scores by subject</small>
            </div>
            <div class="card-body">
              <canvas ref="subjectPerformanceChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Progress Trend Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 no-hover-effect chart-white-bg">
            <div class="card-header bg-white text-dark no-hover-effect">
              <h5 class="mb-0 text-dark no-hover-effect">
                <i class="bi bi-graph-up me-2 text-info"></i>Progress Trend
              </h5>
              <small class="text-muted">Score improvement over time</small>
            </div>
            <div class="card-body">
              <canvas ref="progressTrendChart" height="300"></canvas>
            </div>
          </div>
        </div>

        <!-- Time Spent Chart -->
        <div class="col-lg-6 mb-4">
          <div class="card h-100 no-hover-effect chart-white-bg">
            <div class="card-header bg-white text-dark no-hover-effect">
              <h5 class="mb-0 text-dark no-hover-effect">
                <i class="bi bi-bar-chart me-2 text-purple"></i>Monthly Activity
              </h5>
              <small class="text-muted">Time spent by subject and day</small>
            </div>
            <div class="card-body">
              <canvas ref="timeAnalysisChart" height="300"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Statistics -->
      <div class="row mb-4">
        <div class="col-lg-12">
          <div class="card no-hover-effect">
            <div class="card-header bg-white text-dark no-hover-effect">
              <h5 class="mb-0 text-dark no-hover-effect">
                <i class="bi bi-table me-2 text-primary"></i>Performance Summary
              </h5>
            </div>
            <div class="card-body">
              <div v-if="performanceData.length === 0" class="text-center text-muted py-4">
                <i class="bi bi-graph-up-arrow fs-1 mb-3"></i>
                <p>No performance data available yet.<br>Complete some quizzes to see your analytics!</p>
              </div>
              <div v-else class="table-responsive no-hover-effect">
                <table class="table performance-summary-table no-hover-effect">
                  <thead class="table-light no-hover-effect">
                    <tr>
                      <th>Subject</th>
                      <th>Attempts</th>
                      <th>Avg Score</th>
                      <th>Best Score</th>
                      <th>Time Spent</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="subject in performanceData" :key="subject.subject || subject.name">
                      <td>
                        <strong>{{ subject.subject || subject.name }}</strong>
                      </td>
                      <td>
                        <span class="badge bg-primary">{{ subject.attempts }}</span>
                      </td>
                      <td>
                        <span class="badge" :class="getScoreClass(subject.average_score || subject.avg_score)">
                          {{ subject.average_score || subject.avg_score }}%
                        </span>
                      </td>
                      <td>
                        <span class="badge bg-success">{{ subject.best_score || subject.average_score || subject.avg_score }}%</span>
                      </td>
                      <td>{{ formatTime(subject.time_spent || 0) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import AppLayout from '@/components/AppLayout.vue'
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
  name: 'Analytics',
  components: {
    AppLayout
  },
  setup () {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()

    const loading = ref(false)
    const activityPeriod = ref('30d')
    const stats = ref({
      total_attempts: 0,
      average_score: 0,
      best_score: 0,
      total_time_spent: 0
    })
    const chartData = ref({})
    const performanceData = ref([])
    const quizStatusData = ref({
      attempted: { count: 0, quizzes: [] },
      not_attempted: { count: 0, quizzes: [] },
      upcoming: { count: 0, quizzes: [] }
    })

    // Chart references
    const dailyActivityChart = ref(null)
    const scoreDistributionChart = ref(null)
    const subjectPerformanceChart = ref(null)
    const progressTrendChart = ref(null)
    const timeAnalysisChart = ref(null)
    const quizStatusChart = ref(null)

    // Chart instances
    let dailyActivityChartInstance = null
    let scoreDistributionChartInstance = null
    let subjectPerformanceChartInstance = null
    let progressTrendChartInstance = null
    let timeAnalysisChartInstance = null
    let quizStatusChartInstance = null

    const loadAnalyticsData = async () => {
      try {
        loading.value = true

        const response = await fetch(`/api/user/analytics?period=${activityPeriod.value}`, {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        const data = await response.json()

        if (response.ok) {
          stats.value = data.stats || {}
          chartData.value = data.chartData || {}
          performanceData.value = data.performance || []

          await loadQuizStatusData()
          await createAllCharts()
        } else {
          notificationStore.error('Failed to load analytics data: ' + (data.error || 'Unknown error'))
        }
      } catch (error) {
        console.error('Error loading analytics data:', error)
        notificationStore.error('Failed to load analytics data')
      } finally {
        loading.value = false
      }
    }

    const loadQuizStatusData = async () => {
      try {
        const response = await fetch('/api/user/quiz-status', {
          headers: {
            Authorization: `Bearer ${authStore.token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          quizStatusData.value = data.data || {
            attempted: { count: 0, quizzes: [] },
            not_attempted: { count: 0, quizzes: [] },
            upcoming: { count: 0, quizzes: [] }
          }
        } else {
          console.error('Failed to load quiz status data')
        }
      } catch (error) {
        console.error('Error loading quiz status data:', error)
      }
    }

    const refreshData = () => {
      loadAnalyticsData()
    }

    const exportData = async () => {
      try {
        const response = await fetch('/api/user/export-analytics', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authStore.token}`
          },
          body: JSON.stringify({ period: activityPeriod.value })
        })

        if (response.ok) {
          // Create a blob from the response and trigger download
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = url
          link.download = `analytics_data_${new Date().toISOString().split('T')[0]}.csv`
          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)
          window.URL.revokeObjectURL(url)

          notificationStore.success('Analytics data exported successfully!')
        } else {
          throw new Error('Export failed')
        }
      } catch (error) {
        console.error('Export error:', error)
        notificationStore.error('Failed to export analytics')
      }
    }

    // Chart creation functions
    const createDailyActivityChart = () => {
      if (!dailyActivityChart.value) return

      const ctx = dailyActivityChart.value.getContext('2d')

      if (dailyActivityChartInstance) {
        dailyActivityChartInstance.destroy()
      }

      if (!chartData.value?.activity?.data) return

      // Process activity data based on selected period
      const activityData = chartData.value.activity.data
      const periodMap = { '30d': 30, '60d': 60, '90d': 90 }

      const daysToShow = periodMap[activityPeriod.value] || 30
      const recentData = activityData.slice(-daysToShow)

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
            pointHoverRadius: 4 // Same as pointRadius to disable hover effect
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          onHover: () => {}, // Disable hover events
            hover: { mode: null },
            scales: {
            x: {
              display: true,
              title: {
                display: true,
                text: 'Date'
              },
              grid: {
                display: false
              }
            },
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Attempts'
              },
              ticks: {
                stepSize: 1,
                callback: function (value) {
                  return Math.floor(value) === value ? value : ''
                }
              }
            }
          },
          plugins: {
            legend: { display: false },
            tooltip: { enabled: false }
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

      if (!chartData.value?.score_distribution?.data) return

      const distributionData = chartData.value.score_distribution.data

      // Clean up empty categories
      const filteredData = distributionData.filter(item => item.count > 0)

      if (filteredData.length === 0) {
        // Empty state chart
        scoreDistributionChartInstance = new ChartJS(ctx, {
          type: 'doughnut',
          data: {
            labels: ['No attempts yet'],
            datasets: [{
              data: [1],
              backgroundColor: ['rgba(229, 231, 235, 0.8)'],
              borderColor: ['rgb(229, 231, 235)'],
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
                  color: '#6b7280'
                }
              },
              tooltip: {
                enabled: false
              }
            }
          }
        })
        return
      }

      const labels = filteredData.map(item => item.range)
      const data = filteredData.map(item => item.count)
      const total = data.reduce((a, b) => a + b, 0)

      // Color scheme I prefer for score ranges
      const colorMap = {
        '90-100%': { bg: 'rgba(34, 197, 94, 0.8)', border: 'rgb(34, 197, 94)' },
        '80-89%': { bg: 'rgba(59, 130, 246, 0.8)', border: 'rgb(59, 130, 246)' },
        '70-79%': { bg: 'rgba(251, 191, 36, 0.8)', border: 'rgb(251, 191, 36)' },
        '60-69%': { bg: 'rgba(249, 115, 22, 0.8)', border: 'rgb(249, 115, 22)' },
        '50-59%': { bg: 'rgba(245, 101, 101, 0.8)', border: 'rgb(245, 101, 101)' },
        '<50%': { bg: 'rgba(239, 68, 68, 0.8)', border: 'rgb(239, 68, 68)' }
      }

      const backgroundColors = labels.map(label => colorMap[label]?.bg || 'rgba(156, 163, 175, 0.8)')
      const borderColors = labels.map(label => colorMap[label]?.border || 'rgb(156, 163, 175)')

      scoreDistributionChartInstance = new ChartJS(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 2,
            hoverOffset: 0 // Disable hover effect
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
          onHover: () => {}, // Disable hover events
          hover: {
            mode: null // Disable hover mode
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true,
                pointStyle: 'circle',
                generateLabels: function (chart) {
                  const data = chart.data
                  return data.labels.map((label, index) => {
                    const count = data.datasets[0].data[index]
                    const percentage = ((count / total) * 100).toFixed(1)
                    return {
                      text: `${label}: ${count} (${percentage}%)`,
                      fillStyle: data.datasets[0].backgroundColor[index],
                      strokeStyle: data.datasets[0].borderColor[index],
                      pointStyle: 'circle',
                      hidden: false,
                      index
                    }
                  })
                }
              }
            },
            tooltip: {
              enabled: false // Disable tooltips
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

      if (!chartData.value?.subject_performance?.data) return

      const performanceData = chartData.value.subject_performance.data
      const labels = performanceData.map(item => item.subject)
      const data = performanceData.map(item => item.average_score)

      subjectPerformanceChartInstance = new ChartJS(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Average Score (%)',
            data,
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
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  const subject = performanceData[context.dataIndex]
                  return [
                    `Average Score: ${context.parsed.y}%`,
                    `Attempts: ${subject.attempts}`
                  ]
                }
              }
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function (value) {
                  return value + '%'
                }
              }
            }
          }
        }
      })
    }

    const createProgressTrendChart = () => {
      if (!progressTrendChart.value) return

      const ctx = progressTrendChart.value.getContext('2d')

      if (progressTrendChartInstance) {
        progressTrendChartInstance.destroy()
      }

      if (!chartData.value?.monthly_performance?.data) return

      const monthlyData = chartData.value.monthly_performance.data
      const labels = monthlyData.map(item => item.month)
      const data = monthlyData.map(item => item.average_score)

      progressTrendChartInstance = new ChartJS(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Average Score (%)',
            data,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.4,
            fill: true,
            pointBackgroundColor: 'rgb(75, 192, 192)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              ticks: {
                callback: function (value) {
                  return value + '%'
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
                label: function (context) {
                  const monthData = monthlyData[context.dataIndex]
                  return [
                    `Average Score: ${context.parsed.y}%`,
                    `Attempts: ${monthData.attempts}`
                  ]
                }
              }
            }
          }
        }
      })
    }

    const createTimeAnalysisChart = () => {
      if (!timeAnalysisChart.value) return

      const ctx = timeAnalysisChart.value.getContext('2d')

      if (timeAnalysisChartInstance) {
        timeAnalysisChartInstance.destroy()
      }

      // For now, create a simple placeholder chart showing recent quiz attempts
      if (!chartData.value?.monthly_performance?.data) return

      const monthlyData = chartData.value.monthly_performance.data
      const labels = monthlyData.map(item => item.month)
      const data = monthlyData.map(item => item.attempts)

      timeAnalysisChartInstance = new ChartJS(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Quiz Attempts',
            data,
            backgroundColor: 'rgba(168, 85, 247, 0.8)',
            borderColor: 'rgb(168, 85, 247)',
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
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              callbacks: {
                label: function (context) {
                  return `Attempts: ${context.parsed.y}`
                }
              }
            }
          }
        }
      })
    }

    const createQuizStatusChart = () => {
      if (!quizStatusChart.value) return

      const ctx = quizStatusChart.value.getContext('2d')

      if (quizStatusChartInstance) {
        quizStatusChartInstance.destroy()
      }

      const data = [
        quizStatusData.value.attempted.count,
        quizStatusData.value.not_attempted.count,
        quizStatusData.value.upcoming.count
      ]

      const labels = ['Attempted', 'Not Attempted', 'Upcoming']
      const total = data.reduce((a, b) => a + b, 0)

      // If no data, show placeholder
      if (total === 0) {
        quizStatusChartInstance = new ChartJS(ctx, {
          type: 'doughnut',
          data: {
            labels: ['No quizzes available'],
            datasets: [{
              data: [1],
              backgroundColor: ['rgba(229, 231, 235, 0.8)'],
              borderColor: ['rgb(229, 231, 235)'],
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
                  color: '#6b7280'
                }
              },
              tooltip: {
                enabled: false
              }
            }
          }
        })
        return
      }

      const backgroundColors = [
        'rgba(34, 197, 94, 0.8)', // Green for attempted
        'rgba(249, 115, 22, 0.8)', // Orange for not attempted
        'rgba(59, 130, 246, 0.8)' // Blue for upcoming
      ]

      const borderColors = [
        'rgb(34, 197, 94)', // Green
        'rgb(249, 115, 22)', // Orange
        'rgb(59, 130, 246)' // Blue
      ]

      quizStatusChartInstance = new ChartJS(ctx, {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{
            data,
            backgroundColor: backgroundColors,
            borderColor: borderColors,
            borderWidth: 2,
            hoverOffset: 0 // Disable hover effect
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
          onHover: () => {}, // Disable hover events
          hover: {
            mode: null // Disable hover mode
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 20,
                usePointStyle: true,
                pointStyle: 'circle',
                generateLabels: function (chart) {
                  const data = chart.data
                  return data.labels.map((label, index) => {
                    const count = data.datasets[0].data[index]
                    const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0'
                    return {
                      text: `${label}: ${count} (${percentage}%)`,
                      fillStyle: data.datasets[0].backgroundColor[index],
                      strokeStyle: data.datasets[0].borderColor[index],
                      pointStyle: 'circle',
                      hidden: false,
                      index
                    }
                  })
                }
              }
            },
            tooltip: {
              callbacks: {
                title: function (context) {
                  return 'Quiz Status: ' + context[0].label
                },
                label: function (context) {
                  const count = context.parsed
                  const percentage = total > 0 ? ((count / total) * 100).toFixed(1) : '0.0'
                  return [
                    `Count: ${count}`,
                    `Percentage: ${percentage}%`
                  ]
                },
                afterLabel: function (context) {
                  const label = context.label
                  if (label === 'Attempted') return 'Great progress! 🎉'
                  else if (label === 'Not Attempted') return 'Opportunities to learn! 📚'
                  else if (label === 'Upcoming') return 'Get ready! ⏰'
                  return ''
                }
              }
            }
          }
        }
      })
    }

    const createAllCharts = async () => {
      await nextTick()
      createDailyActivityChart()
      createScoreDistributionChart()
      createQuizStatusChart()
      createSubjectPerformanceChart()
      createProgressTrendChart()
      createTimeAnalysisChart()
    }

    const formatTime = (seconds) => {
      if (!seconds) return '0h 0m'
      const hrs = Math.floor(seconds / 3600)
      const mins = Math.floor((seconds % 3600) / 60)
      // Personal preference: show minutes only if less than an hour
      return hrs > 0 ? `${hrs}h ${mins}m` : `${mins}m`
    }

    const getScoreClass = (score) => {
      // My scoring system - might be harsh but works well
      if (score >= 90) return 'bg-success'
      else if (score >= 75) return 'bg-primary' 
      else if (score >= 60) return 'bg-warning'
      else return 'bg-danger'
    }

    const getTrendIcon = (trend) => {
      if (trend > 0) return 'bi-trending-up'
      if (trend < 0) return 'bi-trending-down'
      return 'bi-dash'
    }

    const getTrendColor = (trend) => {
      if (trend > 0) return '#28a745'
      if (trend < 0) return '#dc3545'
      return '#6c757d'
    }

    // Watch for activity period changes
    watch(activityPeriod, () => {
      loadAnalyticsData()
    })

    onMounted(() => {
      loadAnalyticsData()
    })

    return {
      authStore,
      loading,
      activityPeriod,
      stats,
      chartData,
      performanceData,
      quizStatusData,
      refreshData,
      exportData,
      formatTime,
      getScoreClass,
      getTrendIcon,
      getTrendColor,
      // Chart refs
      dailyActivityChart,
      scoreDistributionChart,
      quizStatusChart,
      subjectPerformanceChart,
      progressTrendChart,
      timeAnalysisChart
    }
  }
}
</script>

<style scoped>
/* My preferred styling choices */
.bg-gradient-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
}

.bg-gradient-success {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
}

.stats-card-icon {
  font-size: 2.5rem;
  opacity: 0.9;
}

.card {
  border: none;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.08);
  border-radius: 12px;
}

.card-header {
  border-bottom: 1px solid #e9ecef;
  font-weight: 600;
  border-radius: 12px 12px 0 0 !important;
}

.achievement-icon {
  font-size: 1.5rem;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 123, 255, 0.1);
  border-radius: 50%;
}

.achievement-item {
  padding: 10px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.achievement-item:hover {
  background-color: #f8f9fa;
}

canvas {
  max-height: 300px !important;
  background-color: white !important;
  pointer-events: none !important; /* no hover */
}

.card-body canvas {
  width: 100% !important;
  height: 300px !important;
  background-color: white !important;
  pointer-events: none !important; 
}

/* White chart backgrounds */
.chart-white-bg {
  background-color: white !important;
}

.chart-white-bg .card-body {
  background-color: white !important;
}

.chart-white-bg .card-header {
  background-color: white !important;
  border-bottom: 1px solid #e9ecef !important;
}

.table th {
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: black !important;
}

.btn-outline-primary:hover,
.btn-outline-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

@media (max-width: 768px) {
  .container-fluid {
    padding: 15px;
  }

  .d-flex.justify-content-between {
    flex-direction: column;
    gap: 1rem;
  }

  .stats-card-icon {
    font-size: 2rem;
  }
}
</style>
