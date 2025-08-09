import { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../lib/api'

const AuthContext = createContext({})

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  // 初始化时检查本地存储的用户信息
  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser))
      } catch (error) {
        console.error('Failed to parse saved user:', error)
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  // 登录函数
  const login = async (usernameOrEmail, password) => {
    try {
      const response = await api.post('/users/login', {
        username_or_email: usernameOrEmail,
        password
      })

      if (response.success) {
        const userData = response.data
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
        return { success: true, user: userData }
      } else {
        return { success: false, error: response.message || '登录失败' }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { 
        success: false, 
        error: error.response?.data?.message || '网络错误，请稍后重试' 
      }
    }
  }

  // 注册函数
  const register = async (username, email, password, displayName) => {
    try {
      const response = await api.post('/users/', {
        username,
        email,
        password,
        display_name: displayName
      })

      if (response.success) {
        const userData = response.data
        setUser(userData)
        localStorage.setItem('user', JSON.stringify(userData))
        return { success: true, user: userData }
      } else {
        return { success: false, error: response.message || '注册失败' }
      }
    } catch (error) {
      console.error('Register error:', error)
      return { 
        success: false, 
        error: error.response?.data?.message || '网络错误，请稍后重试' 
      }
    }
  }

  // 登出函数
  const logout = () => {
    setUser(null)
    localStorage.removeItem('user')
  }

  // 更新用户信息
  const updateUser = async (userData) => {
    try {
      const response = await api.put(`/users/${user.id}`, userData)
      
      if (response.success) {
        const updatedUser = response.data
        setUser(updatedUser)
        localStorage.setItem('user', JSON.stringify(updatedUser))
        return { success: true, user: updatedUser }
      } else {
        return { success: false, error: response.message || '更新失败' }
      }
    } catch (error) {
      console.error('Update user error:', error)
      return { 
        success: false, 
        error: error.response?.data?.message || '网络错误，请稍后重试' 
      }
    }
  }

  // 修改密码
  const changePassword = async (oldPassword, newPassword) => {
    try {
      const response = await api.post(`/users/${user.id}/change-password`, {
        old_password: oldPassword,
        new_password: newPassword
      })

      if (response.success) {
        return { success: true }
      } else {
        return { success: false, error: response.message || '密码修改失败' }
      }
    } catch (error) {
      console.error('Change password error:', error)
      return { 
        success: false, 
        error: error.response?.data?.message || '网络错误，请稍后重试' 
      }
    }
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    changePassword
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

