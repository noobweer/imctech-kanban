import { ofetch } from 'ofetch'
import type { LoginCredentials, SignUpData, AuthUser, TokenPair } from '@/types/auth'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

let isRefreshing = false
let refreshPromise: Promise<string> | null = null

const api = ofetch.create({
  baseURL: '/api',
  async onResponseError({ response, options }) {
    // Skip retry for auth endpoints
    if (options.url?.includes('/token/') || options.url?.includes('/auth/register')) {
      return
    }

    // Handle 401 - token expired
    if (response.status === 401) {
      const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
      if (!refreshToken) {
        // No refresh token - logout
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/auth'
        return
      }

      try {
        // Prevent multiple simultaneous refresh requests
        if (!isRefreshing) {
          isRefreshing = true
          refreshPromise = authApi.refreshToken(refreshToken).then(({ access }) => {
            localStorage.setItem(ACCESS_TOKEN_KEY, access)
            isRefreshing = false
            refreshPromise = null
            return access
          })
        }

        const newToken = await refreshPromise

        // Retry original request with new token
        if (options.headers) {
          options.headers = {
            ...options.headers,
            Authorization: `Bearer ${newToken}`,
          }
        }

        return ofetch(options.url as string, options)
      } catch (error) {
        // Refresh failed - logout
        isRefreshing = false
        refreshPromise = null
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        window.location.href = '/auth'
        throw error
      }
    }
  },
})

export const authApi = {
  async register(data: SignUpData): Promise<AuthUser> {
    return api('/auth/register', {
      method: 'POST',
      body: data,
    })
  },

  async login(credentials: LoginCredentials): Promise<TokenPair> {
    return api('/token/pair', {
      method: 'POST',
      body: credentials,
    })
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    return api('/token/refresh', {
      method: 'POST',
      body: { refresh: refreshToken },
    })
  },

  async getCurrentUser(accessToken: string): Promise<AuthUser> {
    return api('/auth/me', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    })
  },
}
