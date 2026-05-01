export interface LoginCredentials {
  email: string
  password: string
}

export interface SignUpData {
  email: string
  password: string
  displayName: string
  userType: 'student' | 'mentor'
}

export interface AuthUser {
  id: string
  email: string
  displayName: string
  userType: 'student' | 'mentor'
}

export interface AuthState {
  user: AuthUser | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}
