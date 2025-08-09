import { useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Menu, 
  X, 
  Home, 
  FileText, 
  User, 
  Settings, 
  LogOut,
  Sun,
  Moon,
  Plus
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useAuth } from '../contexts/AuthContext'
import { useTheme } from '../contexts/ThemeContext'

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()

  // 导航菜单项
  const menuItems = [
    {
      name: '仪表板',
      path: '/dashboard',
      icon: Home
    },
    {
      name: 'Prompt 管理',
      path: '/prompts',
      icon: FileText
    },
    {
      name: '个人资料',
      path: '/profile',
      icon: User
    }
  ]

  // 处理登出
  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  // 侧边栏动画变体
  const sidebarVariants = {
    open: {
      x: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    },
    closed: {
      x: "-100%",
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 移动端遮罩 */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <motion.aside
        variants={sidebarVariants}
        animate={sidebarOpen ? "open" : "closed"}
        className="fixed left-0 top-0 h-full w-64 bg-card border-r border-border z-50 lg:translate-x-0 lg:static lg:z-auto"
      >
        <div className="flex flex-col h-full">
          {/* Logo 区域 */}
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between">
              <motion.h1 
                className="text-xl font-bold text-foreground"
                whileHover={{ scale: 1.05 }}
              >
                Prompt Manager
              </motion.h1>
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setSidebarOpen(false)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* 导航菜单 */}
          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path
              
              return (
                <motion.div
                  key={item.path}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Button
                    variant={isActive ? "default" : "ghost"}
                    className="w-full justify-start"
                    onClick={() => {
                      navigate(item.path)
                      setSidebarOpen(false)
                    }}
                  >
                    <Icon className="mr-3 h-4 w-4" />
                    {item.name}
                  </Button>
                </motion.div>
              )
            })}
            
            {/* 新建 Prompt 按钮 */}
            <motion.div
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="pt-4"
            >
              <Button
                className="w-full justify-start"
                onClick={() => {
                  navigate('/prompts/new')
                  setSidebarOpen(false)
                }}
              >
                <Plus className="mr-3 h-4 w-4" />
                新建 Prompt
              </Button>
            </motion.div>
          </nav>

          {/* 用户信息和设置 */}
          <div className="p-4 border-t border-border space-y-2">
            {/* 主题切换 */}
            <Button
              variant="ghost"
              className="w-full justify-start"
              onClick={toggleTheme}
            >
              {theme === 'dark' ? (
                <Sun className="mr-3 h-4 w-4" />
              ) : (
                <Moon className="mr-3 h-4 w-4" />
              )}
              {theme === 'dark' ? '浅色模式' : '深色模式'}
            </Button>

            {/* 用户信息 */}
            <div className="px-3 py-2 text-sm text-muted-foreground">
              <div className="font-medium text-foreground">
                {user?.display_name || user?.username}
              </div>
              <div className="text-xs">{user?.email}</div>
            </div>

            {/* 登出按钮 */}
            <Button
              variant="ghost"
              className="w-full justify-start text-destructive hover:text-destructive"
              onClick={handleLogout}
            >
              <LogOut className="mr-3 h-4 w-4" />
              退出登录
            </Button>
          </div>
        </div>
      </motion.aside>

      {/* 主内容区域 */}
      <div className="lg:ml-64">
        {/* 顶部导航栏 */}
        <header className="bg-card border-b border-border px-4 py-3 lg:px-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* 移动端菜单按钮 */}
              <Button
                variant="ghost"
                size="sm"
                className="lg:hidden"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="h-5 w-5" />
              </Button>

              {/* 页面标题 */}
              <h2 className="text-lg font-semibold text-foreground">
                {menuItems.find(item => item.path === location.pathname)?.name || 'Prompt Manager'}
              </h2>
            </div>

            {/* 右侧操作区 */}
            <div className="flex items-center space-x-2">
              {/* 可以添加搜索、通知等功能 */}
            </div>
          </div>
        </header>

        {/* 页面内容 */}
        <main className="p-4 lg:p-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Outlet />
          </motion.div>
        </main>
      </div>
    </div>
  )
}

export default Layout

