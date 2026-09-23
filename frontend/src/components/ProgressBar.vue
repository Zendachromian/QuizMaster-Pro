<template>
  <div class="progress-container">
    <div class="progress" :style="{ height: height + 'px' }">
      <div
        class="progress-bar"
        :class="getProgressClass(percentage)"
        role="progressbar"
        :style="{ width: percentage + '%' }"
        :aria-valuenow="percentage"
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <span v-if="showLabel" class="progress-label">{{ percentage }}%</span>
      </div>
    </div>
    <small v-if="showText" class="progress-text text-muted mt-1">
      {{ getProgressText(percentage) }}
    </small>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    percentage: {
      type: Number,
      default: 0,
      validator: (value) => value >= 0 && value <= 100
    },
    height: {
      type: Number,
      default: 20
    },
    showLabel: {
      type: Boolean,
      default: true
    },
    showText: {
      type: Boolean,
      default: false
    }
  },
  setup (props) {
    const getProgressClass = (percentage) => {
      if (percentage >= 80) return 'bg-success'
      if (percentage >= 60) return 'bg-primary'
      if (percentage >= 40) return 'bg-warning'
      return 'bg-danger'
    }

    const getProgressText = (percentage) => {
      if (percentage >= 80) return 'Excellent'
      if (percentage >= 60) return 'Good'
      if (percentage >= 40) return 'Average'
      if (percentage > 0) return 'Needs Improvement'
      return 'No Data'
    }

    return {
      getProgressClass,
      getProgressText
    }
  }
}
</script>

<style scoped>
.progress-container {
  display: flex;
  flex-direction: column;
}

.progress {
  border-radius: 10px;
  background-color: #e9ecef;
  overflow: hidden;
}

.progress-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  transition: width 0.6s ease;
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.progress-label {
  font-size: 10px;
  font-weight: 600;
}

.progress-text {
  font-size: 10px;
  text-align: center;
}

/* Custom colors for better visibility */
.bg-success {
  background: linear-gradient(45deg, #28a745, #20c997) !important;
}

.bg-primary {
  background: linear-gradient(45deg, #007bff, #6f42c1) !important;
}

.bg-warning {
  background: linear-gradient(45deg, #ffc107, #fd7e14) !important;
  color: #212529 !important;
}

.bg-danger {
  background: linear-gradient(45deg, #dc3545, #e83e8c) !important;
}
</style>
