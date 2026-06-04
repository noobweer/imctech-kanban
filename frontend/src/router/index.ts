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
      component: () => import('@/views/BoardLayoutView.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'board-detail',
          component: () => import('@/views/BoardDetailView.vue'),
        },
        {
          path: 'backlog',
          name: 'board-backlog',
          component: () => import('@/views/BacklogTasksView.vue'),
        },
        {
          path: 'archive',
          name: 'board-archive',
          component: () => import('@/views/ArchiveView.vue'),
        },
        {
          path: 'overview',
          name: 'board-overview',
          component: () => import('@/components/board/OverviewTab.vue'),
        },
      ],
    },
    {
      path: '/join/:inviteId',
      name: 'join-board',
      component: () => import('@/views/JoinView.vue'),
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
    return { path: '/auth', query: { redirect: to.fullPath } }
  }

  if (to.path === '/auth' && authStore.isAuthenticated) {
    return '/boards'
  }
})

export default router
