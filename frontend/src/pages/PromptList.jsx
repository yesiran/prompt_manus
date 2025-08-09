import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Plus, 
  Search, 
  Filter, 
  MoreVertical,
  Edit,
  Copy,
  Trash2,
  Star,
  Clock,
  User,
  Tag,
  Eye,
  Play
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

import { useAuth } from '../contexts/AuthContext'

const PromptList = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  
  const [prompts, setPrompts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterBy, setFilterBy] = useState('all')
  const [sortBy, setSortBy] = useState('updated_at')

  // 模拟数据
  useEffect(() => {
    // 这里应该调用真实的API获取Prompt列表
    setTimeout(() => {
      setPrompts([
        {
          id: 1,
          title: '产品描述生成器',
          description: '为电商产品生成吸引人的描述文案',
          content: '请为以下产品生成一个吸引人的描述...',
          tags: ['电商', '文案', '营销'],
          category: 'marketing',
          is_public: true,
          created_at: '2024-01-15T10:30:00Z',
          updated_at: '2024-01-20T14:20:00Z',
          version_count: 3,
          test_count: 15,
          author: {
            id: user?.id,
            username: user?.username,
            display_name: user?.display_name
          }
        },
        {
          id: 2,
          title: '代码注释生成器',
          description: '为代码自动生成清晰的注释',
          content: '请为以下代码生成详细的注释...',
          tags: ['编程', '代码', '注释'],
          category: 'development',
          is_public: false,
          created_at: '2024-01-10T09:15:00Z',
          updated_at: '2024-01-18T16:45:00Z',
          version_count: 2,
          test_count: 8,
          author: {
            id: user?.id,
            username: user?.username,
            display_name: user?.display_name
          }
        },
        {
          id: 3,
          title: '文章标题优化',
          description: '优化文章标题，提高点击率',
          content: '请帮我优化以下文章标题...',
          tags: ['写作', '标题', 'SEO'],
          category: 'writing',
          is_public: true,
          created_at: '2024-01-05T14:20:00Z',
          updated_at: '2024-01-15T11:30:00Z',
          version_count: 1,
          test_count: 22,
          author: {
            id: 999,
            username: 'collaborator',
            display_name: '协作者'
          }
        }
      ])
      setLoading(false)
    }, 1000)
  }, [user])

  // 过滤和搜索逻辑
  const filteredPrompts = prompts.filter(prompt => {
    const matchesSearch = prompt.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         prompt.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesFilter = filterBy === 'all' || 
                         (filterBy === 'mine' && prompt.author.id === user?.id) ||
                         (filterBy === 'public' && prompt.is_public) ||
                         (filterBy === 'private' && !prompt.is_public)
    
    return matchesSearch && matchesFilter
  })

  // 排序逻辑
  const sortedPrompts = [...filteredPrompts].sort((a, b) => {
    switch (sortBy) {
      case 'title':
        return a.title.localeCompare(b.title)
      case 'created_at':
        return new Date(b.created_at) - new Date(a.created_at)
      case 'updated_at':
        return new Date(b.updated_at) - new Date(a.updated_at)
      case 'test_count':
        return b.test_count - a.test_count
      default:
        return 0
    }
  })

  // 格式化时间
  const formatTime = (timeString) => {
    const time = new Date(timeString)
    const now = new Date()
    const diffInHours = (now - time) / (1000 * 60 * 60)
    
    if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}小时前`
    } else if (diffInHours < 24 * 7) {
      return `${Math.floor(diffInHours / 24)}天前`
    } else {
      return time.toLocaleDateString('zh-CN')
    }
  }

  // 处理Prompt操作
  const handleEdit = (prompt) => {
    navigate(`/prompts/${prompt.id}/edit`)
  }

  const handleView = (prompt) => {
    navigate(`/prompts/${prompt.id}`)
  }

  const handleTest = (prompt) => {
    // 这里应该打开测试对话框或跳转到测试页面
    console.log('测试 Prompt:', prompt.title)
  }

  const handleCopy = (prompt) => {
    // 复制Prompt内容到剪贴板
    navigator.clipboard.writeText(prompt.content)
    // 这里应该显示成功提示
  }

  const handleDelete = (prompt) => {
    // 这里应该显示确认对话框
    console.log('删除 Prompt:', prompt.title)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面头部 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-foreground">Prompt 管理</h1>
          <p className="text-muted-foreground mt-2">
            管理您的所有提示词模板
          </p>
        </div>
        <Button onClick={() => navigate('/prompts/new')} className="mt-4 sm:mt-0">
          <Plus className="mr-2 h-4 w-4" />
          新建 Prompt
        </Button>
      </motion.div>

      {/* 搜索和过滤栏 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4"
      >
        {/* 搜索框 */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="搜索 Prompt..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* 过滤器 */}
        <Select value={filterBy} onValueChange={setFilterBy}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="过滤条件" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">全部</SelectItem>
            <SelectItem value="mine">我的</SelectItem>
            <SelectItem value="public">公开</SelectItem>
            <SelectItem value="private">私有</SelectItem>
          </SelectContent>
        </Select>

        {/* 排序 */}
        <Select value={sortBy} onValueChange={setSortBy}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="排序方式" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="updated_at">最近更新</SelectItem>
            <SelectItem value="created_at">创建时间</SelectItem>
            <SelectItem value="title">标题</SelectItem>
            <SelectItem value="test_count">测试次数</SelectItem>
          </SelectContent>
        </Select>
      </motion.div>

      {/* Prompt 列表 */}
      <AnimatePresence>
        {sortedPrompts.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center py-12"
          >
            <div className="text-muted-foreground">
              {searchTerm || filterBy !== 'all' ? '没有找到匹配的 Prompt' : '还没有创建任何 Prompt'}
            </div>
            <Button 
              variant="outline" 
              className="mt-4"
              onClick={() => navigate('/prompts/new')}
            >
              <Plus className="mr-2 h-4 w-4" />
              创建第一个 Prompt
            </Button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedPrompts.map((prompt, index) => (
              <motion.div
                key={prompt.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ y: -5 }}
                className="group"
              >
                <Card className="h-full hover:shadow-lg transition-all duration-200 cursor-pointer">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <CardTitle 
                          className="text-lg truncate group-hover:text-primary transition-colors"
                          onClick={() => handleView(prompt)}
                        >
                          {prompt.title}
                        </CardTitle>
                        <CardDescription className="mt-1 line-clamp-2">
                          {prompt.description}
                        </CardDescription>
                      </div>
                      
                      {/* 操作菜单 */}
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => handleView(prompt)}>
                            <Eye className="mr-2 h-4 w-4" />
                            查看
                          </DropdownMenuItem>
                          {prompt.author.id === user?.id && (
                            <DropdownMenuItem onClick={() => handleEdit(prompt)}>
                              <Edit className="mr-2 h-4 w-4" />
                              编辑
                            </DropdownMenuItem>
                          )}
                          <DropdownMenuItem onClick={() => handleTest(prompt)}>
                            <Play className="mr-2 h-4 w-4" />
                            测试
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleCopy(prompt)}>
                            <Copy className="mr-2 h-4 w-4" />
                            复制
                          </DropdownMenuItem>
                          {prompt.author.id === user?.id && (
                            <>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem 
                                onClick={() => handleDelete(prompt)}
                                className="text-destructive"
                              >
                                <Trash2 className="mr-2 h-4 w-4" />
                                删除
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>

                  <CardContent className="space-y-4">
                    {/* 标签 */}
                    <div className="flex flex-wrap gap-1">
                      {prompt.tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="secondary" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                      {prompt.tags.length > 3 && (
                        <Badge variant="outline" className="text-xs">
                          +{prompt.tags.length - 3}
                        </Badge>
                      )}
                    </div>

                    {/* 元信息 */}
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <User className="mr-1 h-3 w-3" />
                          {prompt.author.display_name}
                        </div>
                        <div className="flex items-center">
                          {prompt.is_public ? (
                            <Badge variant="outline" className="text-xs">公开</Badge>
                          ) : (
                            <Badge variant="secondary" className="text-xs">私有</Badge>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <Clock className="mr-1 h-3 w-3" />
                          {formatTime(prompt.updated_at)}
                        </div>
                        <div className="flex items-center space-x-3">
                          <span>v{prompt.version_count}</span>
                          <span>{prompt.test_count} 次测试</span>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default PromptList

