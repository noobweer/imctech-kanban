export interface LoginCredentials {
  username: string
  password: string
}

export interface SignUpData {
  username: string
  password: string
  name: string
  role: 'student' | 'mentor'
}

export interface AuthUser {
  username: string
  name: string
  role: 'student' | 'mentor'
  created_at: string
  updated_at: string
}

export interface TokenPair {
  access: string
  refresh: string
}

export interface AuthState {
  user: AuthUser | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}
