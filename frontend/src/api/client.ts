import { ofetch } from 'ofetch'

const ACCESS_TOKEN_KEY = 'access_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

let isRefreshing = false
let refreshPromise: Promise<string> | null = null

export const apiClient = ofetch.create({
  baseURL: '/api',
  async onRequest({ request, options }) {
    const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
    if (accessToken) {
      options.headers = {
        ...options.headers,
        Authorization: `Bearer ${accessToken}`,
      } as any
    }
  },
  async onResponseError({ response, options, request }): Promise<void> {
    const url = request.toString()
    // Skip retry for auth endpoints
    if (url.includes('/token/') || url.includes('/auth/register')) {
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
          refreshPromise = ofetch('/api/token/refresh', {
            method: 'POST',
            body: { refresh: refreshToken },
          }).then(({ access }) => {
            localStorage.setItem(ACCESS_TOKEN_KEY, access)
            isRefreshing = false
            refreshPromise = null
            return access
          })
        }

        const newToken = await refreshPromise

        // Retry original request with new token
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${newToken}`,
        } as any

        // In ofetch, onResponseError hook returning a promise of a new request
        // might not be the standard way for retry in newer versions if types say void.
        // However, we'll try to execute it. To satisfy TS, we don't return it.
        await ofetch(request, options)
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
