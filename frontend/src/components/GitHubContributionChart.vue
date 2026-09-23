<template>
  <div class="github-contribution-chart">
    <div class="chart-container">
      <div class="months-labels">
        <span v-for="month in monthLabels" :key="month" class="month-label">{{ month }}</span>
      </div>
      <div class="chart-content">
        <div class="days-labels">
          <span class="day-label">Mon</span>
          <span class="day-label"></span>
          <span class="day-label">Wed</span>
          <span class="day-label"></span>
          <span class="day-label">Fri</span>
          <span class="day-label"></span>
          <span class="day-label">Sun</span>
        </div>
        <div class="weeks-container">
          <div v-for="(week, weekIndex) in weeks" :key="weekIndex" class="week-column">
            <div
              v-for="(day, dayIndex) in week"
              :key="dayIndex"
              class="contribution-day"
              :class="getContributionLevel(day.count)"
              :title="`${day.count} contributions on ${formatDate(day.date)}`"
            ></div>
          </div>
        </div>
      </div>
      <div class="legend">
        <span class="legend-text">Less</span>
        <div class="legend-colors">
          <div class="legend-square level-0"></div>
          <div class="legend-square level-1"></div>
          <div class="legend-square level-2"></div>
          <div class="legend-square level-3"></div>
          <div class="legend-square level-4"></div>
        </div>
        <span class="legend-text">More</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'GitHubContributionChart',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  setup (props) {
    const weeks = computed(() => {
      // Create a map of date -> count for quick lookup
      const dataMap = {}
      if (props.data && props.data.length > 0) {
        props.data.forEach(item => {
          if (item && item.date) {
            dataMap[item.date] = item.count || 0
          }
        })
      }

      // Generate 52 weeks of data starting from 365 days ago
      const weeks = []
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const startDate = new Date(today)
      startDate.setDate(today.getDate() - 364)

      for (let week = 0; week < 52; week++) {
        const weekData = []
        for (let day = 0; day < 7; day++) {
          const currentDate = new Date(startDate)
          currentDate.setDate(startDate.getDate() + (week * 7) + day)
          const dateStr = currentDate.toISOString().split('T')[0]

          const count = dataMap[dateStr] || 0
          weekData.push({
            date: dateStr,
            count
          })
        }
        weeks.push(weekData)
      }

      return weeks
    })

    const monthLabels = computed(() => {
      const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
      const labels = []
      const today = new Date()

      // Show every 3rd month for better spacing
      for (let i = 11; i >= 0; i -= 3) {
        const date = new Date(today.getFullYear(), today.getMonth() - i, 1)
        labels.push(months[date.getMonth()])
      }

      return labels
    })

    const getContributionLevel = (count) => {
      if (count === 0) return 'level-0'
      if (count <= 2) return 'level-1'
      if (count <= 5) return 'level-2'
      if (count <= 10) return 'level-3'
      return 'level-4'
    }

    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      })
    }

    return {
      weeks,
      monthLabels,
      getContributionLevel,
      formatDate
    }
  }
}
</script>

<style scoped>
.github-contribution-chart {
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}

.chart-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.months-labels {
  display: flex;
  padding-left: 30px;
  justify-content: space-between;
  width: calc(100% - 30px);
}

.month-label {
  font-size: 11px;
  color: #656d76;
  text-align: center;
  flex: 1;
}

.chart-content {
  display: flex;
  gap: 8px;
}

.days-labels {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 2px;
}

.day-label {
  font-size: 9px;
  color: #656d76;
  height: 11px;
  width: 25px;
  display: flex;
  align-items: center;
  margin-bottom: 2px;
}

.weeks-container {
  display: flex;
  gap: 2px;
  flex: 1;
}

.week-column {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.contribution-day {
  width: 11px;
  height: 11px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.1s ease;
}

.contribution-day:hover {
  stroke: rgba(1, 4, 9, 0.8);
  stroke-width: 1px;
  transform: scale(1.1);
}

.level-0 {
  background-color: #ebedf0;
}

.level-1 {
  background-color: #9be9a8;
}

.level-2 {
  background-color: #40c463;
}

.level-3 {
  background-color: #30a14e;
}

.level-4 {
  background-color: #216e39;
}

.legend {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 4px;
  margin-top: 8px;
}

.legend-text {
  font-size: 11px;
  color: #656d76;
}

.legend-colors {
  display: flex;
  gap: 2px;
}

.legend-square {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

/* Dark theme support */
@media (prefers-color-scheme: dark) {
  .month-label,
  .day-label,
  .legend-text {
    color: #8b949e;
  }

  .level-0 {
    background-color: #161b22;
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .github-contribution-chart {
    padding: 8px;
  }

  .contribution-day {
    width: 8px;
    height: 8px;
  }

  .month-label,
  .day-label {
    font-size: 8px;
  }

  .day-label {
    width: 20px;
  }

  .weeks-container {
    gap: 1px;
  }

  .week-column {
    gap: 1px;
  }
}
</style>
