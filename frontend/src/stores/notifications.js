import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: []
  }),

  actions: {
    addNotification (message, type = 'info', duration = 5000) {
      const notification = {
        id: Date.now() + Math.random(),
        message,
        type,
        timestamp: new Date()
      }

      this.notifications.push(notification)

      // Auto remove after duration
      if (duration > 0) {
        setTimeout(() => {
          this.removeNotification(notification.id)
        }, duration)
      }

      return notification.id
    },

    removeNotification (idOrIndex) {
      if (typeof idOrIndex === 'number' && idOrIndex < this.notifications.length) {
        // Remove by index
        this.notifications.splice(idOrIndex, 1)
      } else {
        // Remove by id
        const index = this.notifications.findIndex(n => n.id === idOrIndex)
        if (index !== -1) {
          this.notifications.splice(index, 1)
        }
      }
    },

    clearAll () {
      this.notifications = []
    },

    // Helper methods for different notification types
    success (message, duration = 5000) {
      return this.addNotification(message, 'success', duration)
    },

    error (message, duration = 8000) {
      return this.addNotification(message, 'danger', duration)
    },

    warning (message, duration = 6000) {
      return this.addNotification(message, 'warning', duration)
    },

    info (message, duration = 5000) {
      return this.addNotification(message, 'info', duration)
    }
  }
})
