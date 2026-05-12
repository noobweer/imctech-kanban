import { apiClient } from './client'
import type { LoginCredentials, SignUpData, AuthUser, TokenPair } from '@/types/auth'

export const authApi = {
  async register(data: SignUpData): Promise<AuthUser> {
    return apiClient('/auth/register', {
      method: 'POST',
      body: data,
    })
  },

  async login(credentials: LoginCredentials): Promise<TokenPair> {
    return apiClient('/token/pair', {
      method: 'POST',
      body: credentials,
    })
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    return apiClient('/token/refresh', {
      method: 'POST',
      body: { refresh: refreshToken },
    })
  },

  async getCurrentUser(): Promise<AuthUser> {
    return apiClient('/auth/me')
  },
}
