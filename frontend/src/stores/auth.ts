import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { AuthUser, LoginCredentials, SignUpData } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        throw new Error('Login failed')
      }

      user.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Login failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function signUp(data: SignUpData) {
    loading.value = true
    error.value = null

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        throw new Error('Sign up failed')
      }

      user.value = await response.json()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Sign up failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value = null
    error.value = null
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    signUp,
    logout,
  }
})
