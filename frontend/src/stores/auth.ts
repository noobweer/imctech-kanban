import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { AuthUser, LoginCredentials, SignUpData } from '@/types/auth'
import { authApi } from '@/api/auth'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => user.value !== null)

  async function login(credentials: LoginCredentials) {
    loading.value = true
    error.value = null

    try {
      const tokens = await authApi.login(credentials)
      localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access)
      localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh)

      user.value = await authApi.getCurrentUser()
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
      await authApi.register(data)
      await login({ username: data.username, password: data.password })
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Sign up failed'
      throw e
    } finally {
      loading.value = false
    }
  }

  async function refreshAccessToken() {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
    if (!refreshToken) {
      throw new Error('No refresh token')
    }

    try {
      const { access } = await authApi.refreshToken(refreshToken)
      localStorage.setItem(ACCESS_TOKEN_KEY, access)
      return access
    } catch (e) {
      logout()
      throw e
    }
  }

  async function initializeAuth() {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
    if (!accessToken) return

    try {
      user.value = await authApi.getCurrentUser()
    } catch (e) {
      // onResponseError already tried refresh, if we're here - it failed
      logout()
    }
  }

  function logout() {
    user.value = null
    error.value = null
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }

  function updateProfile(name: string) {
    if (user.value) {
      user.value.name = name
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    signUp,
    logout,
    refreshAccessToken,
    initializeAuth,
    updateProfile,
  }
})
