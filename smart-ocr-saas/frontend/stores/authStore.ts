import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  username: string
  display_name?: string
  role: string
  auth_type: string
}

interface AuthState {
  token: string | null
  user: User | null
  isAuthenticated: boolean
  setAuth: (token: string) => void
  setUser: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      setAuth: (token: string) => {
        // Decode JWT to get user info (basic decode without verification)
        try {
          const payload = JSON.parse(atob(token.split('.')[1]))
          const user: User = {
            id: payload.sub,
            username: payload.username,
            role: payload.role,
            auth_type: payload.auth_type,
          }
          set({ token, user, isAuthenticated: true })
        } catch {
          set({ token, isAuthenticated: true })
        }
      },

      setUser: (user: User) => {
        set({ user })
      },

      logout: () => {
        set({ token: null, user: null, isAuthenticated: false })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
