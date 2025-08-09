import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Mail, 
  Calendar, 
  Edit, 
  Save, 
  X,
  Key,
  Shield,
  Activity,
  FileText,
  Users,
  TrendingUp
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { Alert, AlertDescription } from '@/components/ui/alert'

import { useAuth } from '../contexts/AuthContext'

const Profile = () => {
  const { user, updateUser, changePassword } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState({ type: '', content: '' })

  const [profileData, setProfileData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    display_name: user?.display_name || '',
    bio: user?.bio || ''
  })

  const [passwordData, setPasswordData] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  // 用户统计数据（模拟）
  const userStats = {
    totalPrompts: 12,
    publicPrompts: 8,
    totalTests: 45,
    collaborations: 5
  }

  // 处理个人信息更新
  const handleProfileUpdate = async () => {
    setLoading(true)
    setMessage({ type: '', content: '' })

    try {
      const result = await updateUser(profileData)
      if (result.success) {
        setMessage({ type: 'success', content: '个人信息更新成功！' })
        setIsEditing(false)
      } else {
        setMessage({ type: 'error', content: result.error })
      }
    } catch (error) {
      setMessage({ type: 'error', content: '更新失败，请稍后重试' })
    } finally {
      setLoading(false)
    }
  }

  // 处理密码修改
  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', content: '两次输入的新密码不一致' })
      return
    }

    if (passwordData.newPassword.length < 6) {
      setMessage({ type: 'error', content: '新密码至少需要6个字符' })
      return
    }

    setLoading(true)
    setMessage({ type: '', content: '' })

    try {
      const result = await changePassword(passwordData.oldPassword, passwordData.newPassword)
      if (result.success) {
        setMessage({ type: 'success', content: '密码修改成功！' })
        setIsChangingPassword(false)
        setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' })
      } else {
        setMessage({ type: 'error', content: result.error })
      }
    } catch (error) {
      setMessage({ type: 'error', content: '密码修改失败，请稍后重试' })
    } finally {
      setLoading(false)
    }
  }

  // 取消编辑
  const handleCancelEdit = () => {
    setProfileData({
      username: user?.username || '',
      email: user?.email || '',
      display_name: user?.display_name || '',
      bio: user?.bio || ''
    })
    setIsEditing(false)
    setMessage({ type: '', content: '' })
  }

  // 取消密码修改
  const handleCancelPasswordChange = () => {
    setPasswordData({ oldPassword: '', newPassword: '', confirmPassword: '' })
    setIsChangingPassword(false)
    setMessage({ type: '', content: '' })
  }

  // 格式化注册时间
  const formatJoinDate = (dateString) => {
    if (!dateString) return '未知'
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 页面头部 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-3xl font-bold text-foreground">个人资料</h1>
        <p className="text-muted-foreground mt-2">
          管理您的账户信息和偏好设置
        </p>
      </motion.div>

      {/* 消息提示 */}
      {message.content && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <Alert variant={message.type === 'error' ? 'destructive' : 'default'}>
            <AlertDescription>{message.content}</AlertDescription>
          </Alert>
        </motion.div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 主要信息区域 */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* 基本信息 */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <User className="mr-2 h-5 w-5" />
                    基本信息
                  </CardTitle>
                  <CardDescription>
                    您的账户基本信息
                  </CardDescription>
                </div>
                {!isEditing && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit className="mr-2 h-4 w-4" />
                    编辑
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* 头像 */}
              <div className="flex items-center space-x-4">
                <Avatar className="h-16 w-16">
                  <AvatarImage src={user?.avatar} />
                  <AvatarFallback className="text-lg">
                    {(user?.display_name || user?.username || 'U').charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="font-semibold text-lg">
                    {user?.display_name || user?.username}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {user?.email}
                  </p>
                </div>
              </div>

              <Separator />

              {/* 表单字段 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="username">用户名</Label>
                  <Input
                    id="username"
                    value={profileData.username}
                    onChange={(e) => setProfileData(prev => ({ ...prev, username: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">邮箱</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profileData.email}
                    onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>

                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="display_name">显示名称</Label>
                  <Input
                    id="display_name"
                    value={profileData.display_name}
                    onChange={(e) => setProfileData(prev => ({ ...prev, display_name: e.target.value }))}
                    disabled={!isEditing}
                  />
                </div>
              </div>

              {/* 编辑模式按钮 */}
              {isEditing && (
                <div className="flex space-x-2 pt-4">
                  <Button
                    onClick={handleProfileUpdate}
                    disabled={loading}
                  >
                    <Save className="mr-2 h-4 w-4" />
                    {loading ? '保存中...' : '保存'}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={handleCancelEdit}
                    disabled={loading}
                  >
                    <X className="mr-2 h-4 w-4" />
                    取消
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 安全设置 */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center">
                    <Shield className="mr-2 h-5 w-5" />
                    安全设置
                  </CardTitle>
                  <CardDescription>
                    管理您的账户安全
                  </CardDescription>
                </div>
                {!isChangingPassword && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsChangingPassword(true)}
                  >
                    <Key className="mr-2 h-4 w-4" />
                    修改密码
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {isChangingPassword ? (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="oldPassword">当前密码</Label>
                    <Input
                      id="oldPassword"
                      type="password"
                      value={passwordData.oldPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, oldPassword: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="newPassword">新密码</Label>
                    <Input
                      id="newPassword"
                      type="password"
                      value={passwordData.newPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">确认新密码</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={passwordData.confirmPassword}
                      onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    />
                  </div>

                  <div className="flex space-x-2 pt-4">
                    <Button
                      onClick={handlePasswordChange}
                      disabled={loading || !passwordData.oldPassword || !passwordData.newPassword}
                    >
                      <Save className="mr-2 h-4 w-4" />
                      {loading ? '修改中...' : '修改密码'}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={handleCancelPasswordChange}
                      disabled={loading}
                    >
                      <X className="mr-2 h-4 w-4" />
                      取消
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-sm text-muted-foreground">
                  <p>定期更新密码有助于保护您的账户安全</p>
                  <p className="mt-2">上次修改时间：2024年1月15日</p>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* 侧边栏 */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="space-y-6"
        >
          {/* 账户统计 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="mr-2 h-5 w-5" />
                账户统计
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary">
                    {userStats.totalPrompts}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    总 Prompts
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-500">
                    {userStats.publicPrompts}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    公开 Prompts
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-500">
                    {userStats.totalTests}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    测试次数
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-500">
                    {userStats.collaborations}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    协作项目
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 账户信息 */}
          <Card>
            <CardHeader>
              <CardTitle>账户信息</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">用户ID</span>
                <span className="font-mono">{user?.id}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">注册时间</span>
                <span>{formatJoinDate(user?.created_at)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">最后登录</span>
                <span>{formatJoinDate(user?.last_login_at)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">账户状态</span>
                <span className="text-green-500">正常</span>
              </div>
            </CardContent>
          </Card>

          {/* 快速操作 */}
          <Card>
            <CardHeader>
              <CardTitle>快速操作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start" size="sm">
                <FileText className="mr-2 h-4 w-4" />
                导出数据
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm">
                <Users className="mr-2 h-4 w-4" />
                邀请朋友
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm">
                <TrendingUp className="mr-2 h-4 w-4" />
                使用统计
              </Button>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default Profile

