// Simple toast notification utility
class ToastUtility {
  constructor () {
    this.createContainer()
  }

  createContainer () {
    if (!document.getElementById('toast-container')) {
      const container = document.createElement('div')
      container.id = 'toast-container'
      container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        pointer-events: none;
      `
      document.body.appendChild(container)
    }
  }

  show (message, type = 'info', duration = 3000) {
    const toast = document.createElement('div')
    const colors = {
      success: '#28a745',
      error: '#dc3545',
      warning: '#ffc107',
      info: '#17a2b8'
    }

    toast.style.cssText = `
      background: ${colors[type] || colors.info};
      color: white;
      padding: 12px 16px;
      border-radius: 4px;
      margin-bottom: 8px;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      pointer-events: auto;
      cursor: pointer;
      transform: translateX(100%);
      transition: transform 0.3s ease;
      max-width: 300px;
      word-wrap: break-word;
    `

    toast.textContent = message
    toast.onclick = () => this.hide(toast)

    const container = document.getElementById('toast-container')
    container.appendChild(toast)

    // Animate in
    setTimeout(() => {
      toast.style.transform = 'translateX(0)'
    }, 10)

    // Auto remove
    setTimeout(() => {
      this.hide(toast)
    }, duration)

    return toast
  }

  hide (toast) {
    if (toast && toast.parentElement) {
      toast.style.transform = 'translateX(100%)'
      setTimeout(() => {
        if (toast.parentElement) {
          toast.parentElement.removeChild(toast)
        }
      }, 300)
    }
  }

  success (message, duration = 3000) {
    return this.show(message, 'success', duration)
  }

  error (message, duration = 4000) {
    return this.show(message, 'error', duration)
  }

  warning (message, duration = 3500) {
    return this.show(message, 'warning', duration)
  }

  info (message, duration = 3000) {
    return this.show(message, 'info', duration)
  }
}

// Create global instance
const toast = new ToastUtility()

// Export both toast instance and showToast function for convenience
export { toast }
export const showToast = (message, type = 'info', duration = 3000) => {
  return toast.show(message, type, duration)
}
