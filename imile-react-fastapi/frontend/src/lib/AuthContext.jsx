/**
 * lib/AuthContext.jsx — Contexto de autenticação global
 */
import { createContext, useContext, useState, useEffect } from 'react'
import api from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Tenta restaurar sessão do localStorage
    const token = localStorage.getItem('access_token')
    const saved = localStorage.getItem('user')
    if (token && saved) {
      try {
        setUser(JSON.parse(saved))
      } catch { /* ignora */ }
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    const res = await api.post('/api/auth/login', { email, password })
    const { access_token, user: userData } = res.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setUser(userData)
    return userData
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    setUser(null)
  }

  const isAdmin = user?.role === 'admin'

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isAdmin }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
