<template>
  <AppLayout>
    <div class="container text-center py-5">
      <div class="row justify-content-center">
        <div class="col-lg-6">
          <div class="mb-4">
            <i class="bi bi-exclamation-triangle display-1 text-warning"></i>
          </div>
          <h1 class="display-4 fw-bold mb-3">404 - Page Not Found</h1>
          <p class="lead text-muted mb-4">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div class="d-flex justify-content-center gap-3">
            <router-link to="/" class="btn btn-primary btn-lg">
              <i class="bi bi-house me-1"></i>Go Home
            </router-link>
            <button @click="$router.go(-1)" class="btn btn-outline-secondary btn-lg">
              <i class="bi bi-arrow-left me-1"></i>Go Back
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script>
import AppLayout from '@/components/AppLayout.vue'

export default {
  name: 'NotFound',
  components: {
    AppLayout
  }
}
</script>
