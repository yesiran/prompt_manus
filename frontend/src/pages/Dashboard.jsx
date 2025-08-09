import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  FileText, 
  Plus, 
  TrendingUp, 
  Users, 
  Clock,
  Star,
  Activity,
  BarChart3
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

import { useAuth } from '../contexts/AuthContext'
import { useNavigate } from 'react-router-dom'

const Dashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalPrompts: 0,
    recentPrompts: 0,
    collaborations: 0,
    totalTests: 0
  })

  // 模拟数据加载
  useEffect(() => {
    // 这里应该调用真实的API获取统计数据
    setStats({
      totalPrompts: 12,
      recentPrompts: 3,
      collaborations: 5,
      totalTests: 28
    })
  }, [])

  // 统计卡片数据
  const statCards = [
    {
      title: '我的 Prompts',
      value: stats.totalPrompts,
      description: '总共创建的提示词',
      icon: FileText,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50 dark:bg-blue-950'
    },
    {
      title: '本周新增',
      value: stats.recentPrompts,
      description: '这周创建的提示词',
      icon: TrendingUp,
      color: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-950'
    },
    {
      title: '协作项目',
      value: stats.collaborations,
      description: '参与的协作项目',
      icon: Users,
      color: 'text-purple-500',
      bgColor: 'bg-purple-50 dark:bg-purple-950'
    },
    {
      title: '测试次数',
      value: stats.totalTests,
      description: '累计测试次数',
      icon: Activity,
      color: 'text-orange-500',
      bgColor: 'bg-orange-50 dark:bg-orange-950'
    }
  ]

  // 最近活动数据（模拟）
  const recentActivities = [
    {
      id: 1,
      type: 'create',
      title: '创建了新的 Prompt "产品描述生成器"',
      time: '2小时前',
      icon: Plus
    },
    {
      id: 2,
      type: 'test',
      title: '测试了 "文章标题优化" Prompt',
      time: '5小时前',
      icon: Activity
    },
    {
      id: 3,
      type: 'collaborate',
      title: '加入了 "营销文案" 协作项目',
      time: '1天前',
      icon: Users
    },
    {
      id: 4,
      type: 'update',
      title: '更新了 "代码注释生成器" 的版本',
      time: '2天前',
      icon: FileText
    }
  ]

  // 快速操作
  const quickActions = [
    {
      title: '新建 Prompt',
      description: '创建一个新的提示词',
      icon: Plus,
      action: () => navigate('/prompts/new'),
      color: 'bg-primary text-primary-foreground'
    },
    {
      title: '浏览 Prompts',
      description: '查看所有提示词',
      icon: FileText,
      action: () => navigate('/prompts'),
      color: 'bg-secondary text-secondary-foreground'
    },
    {
      title: '查看统计',
      description: '分析使用数据',
      icon: BarChart3,
      action: () => navigate('/analytics'),
      color: 'bg-muted text-muted-foreground'
    }
  ]

  return (
    <div className="space-y-6">
      {/* 欢迎区域 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              欢迎回来，{user?.display_name || user?.username}！
            </h1>
            <p className="text-muted-foreground mt-2">
              今天是管理您创意的好日子
            </p>
          </div>
          <div className="mt-4 sm:mt-0">
            <Button onClick={() => navigate('/prompts/new')} className="w-full sm:w-auto">
              <Plus className="mr-2 h-4 w-4" />
              新建 Prompt
            </Button>
          </div>
        </div>
      </motion.div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon
          return (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
            >
              <Card className="hover:shadow-md transition-shadow duration-200">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {card.title}
                  </CardTitle>
                  <div className={`p-2 rounded-md ${card.bgColor}`}>
                    <Icon className={`h-4 w-4 ${card.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{card.value}</div>
                  <p className="text-xs text-muted-foreground">
                    {card.description}
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      {/* 主要内容区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 快速操作 */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="lg:col-span-1"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Star className="mr-2 h-5 w-5" />
                快速操作
              </CardTitle>
              <CardDescription>
                常用功能快速入口
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {quickActions.map((action, index) => {
                const Icon = action.icon
                return (
                  <motion.div
                    key={action.title}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Button
                      variant="outline"
                      className="w-full justify-start h-auto p-4"
                      onClick={action.action}
                    >
                      <div className={`p-2 rounded-md mr-3 ${action.color}`}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="text-left">
                        <div className="font-medium">{action.title}</div>
                        <div className="text-sm text-muted-foreground">
                          {action.description}
                        </div>
                      </div>
                    </Button>
                  </motion.div>
                )
              })}
            </CardContent>
          </Card>
        </motion.div>

        {/* 最近活动 */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="lg:col-span-2"
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="mr-2 h-5 w-5" />
                最近活动
              </CardTitle>
              <CardDescription>
                您最近的操作记录
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.map((activity, index) => {
                  const Icon = activity.icon
                  return (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="flex items-start space-x-3 p-3 rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="p-2 bg-primary/10 rounded-md">
                        <Icon className="h-4 w-4 text-primary" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground">
                          {activity.title}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {activity.time}
                        </p>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* 使用提示 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
      >
        <Card className="bg-gradient-to-r from-primary/5 to-secondary/5 border-primary/20">
          <CardContent className="p-6">
            <div className="flex items-start space-x-4">
              <div className="p-2 bg-primary/10 rounded-md">
                <Star className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-2">
                  💡 使用小贴士
                </h3>
                <p className="text-sm text-muted-foreground mb-3">
                  充分利用 Prompt Manager 的强大功能，让您的创意工作更高效：
                </p>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">版本管理</Badge>
                  <Badge variant="secondary">协作编辑</Badge>
                  <Badge variant="secondary">AI 测试</Badge>
                  <Badge variant="secondary">标签分类</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default Dashboard

