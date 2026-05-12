import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/boards',
    },
    {
      path: '/auth',
      name: 'auth',
      component: () => import('@/views/AuthView.vue'),
    },
    {
      path: '/boards',
      name: 'boards',
      component: () => import('@/views/BoardsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/boards/create',
      name: 'create-board',
      component: () => import('@/views/CreateBoardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/boards/:id',
      name: 'board-detail',
      component: () => import('@/views/BoardDetailView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

let isAuthInitialized = false

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  // Initialize auth once on first navigation
  if (!isAuthInitialized) {
    await authStore.initializeAuth()
    isAuthInitialized = true
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return '/auth'
  }

  if (to.path === '/auth' && authStore.isAuthenticated) {
    return '/boards'
  }
})

export default router
