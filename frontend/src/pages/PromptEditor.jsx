import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Save, 
  ArrowLeft, 
  Play, 
  Eye, 
  EyeOff,
  Settings,
  Tag,
  Globe,
  Lock,
  Copy,
  Download
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

import { useAuth } from '../contexts/AuthContext'

const PromptEditor = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()
  const isEditing = Boolean(id && id !== 'new')

  const [prompt, setPrompt] = useState({
    title: '',
    description: '',
    content: '',
    tags: [],
    category: '',
    is_public: false,
    variables: []
  })
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [previewMode, setPreviewMode] = useState(false)
  const [newTag, setNewTag] = useState('')

  // 模拟数据加载
  useEffect(() => {
    if (isEditing) {
      setLoading(true)
      // 这里应该调用API获取Prompt详情
      setTimeout(() => {
        setPrompt({
          title: '产品描述生成器',
          description: '为电商产品生成吸引人的描述文案',
          content: `请为以下产品生成一个吸引人的描述：

产品名称：{product_name}
产品类别：{category}
主要特点：{features}
目标用户：{target_audience}

要求：
1. 突出产品的核心优势
2. 使用吸引人的语言
3. 包含情感化的描述
4. 长度控制在100-200字`,
          tags: ['电商', '文案', '营销'],
          category: 'marketing',
          is_public: true,
          variables: [
            { name: 'product_name', description: '产品名称', required: true },
            { name: 'category', description: '产品类别', required: true },
            { name: 'features', description: '主要特点', required: true },
            { name: 'target_audience', description: '目标用户', required: false }
          ]
        })
        setLoading(false)
      }, 1000)
    }
  }, [isEditing])

  // 处理表单输入
  const handleInputChange = (field, value) => {
    setPrompt(prev => ({
      ...prev,
      [field]: value
    }))
  }

  // 添加标签
  const addTag = () => {
    if (newTag.trim() && !prompt.tags.includes(newTag.trim())) {
      setPrompt(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }))
      setNewTag('')
    }
  }

  // 删除标签
  const removeTag = (tagToRemove) => {
    setPrompt(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  // 保存Prompt
  const handleSave = async () => {
    setSaving(true)
    try {
      // 这里应该调用API保存Prompt
      await new Promise(resolve => setTimeout(resolve, 1000))
      navigate('/prompts')
    } catch (error) {
      console.error('保存失败:', error)
    } finally {
      setSaving(false)
    }
  }

  // 测试Prompt
  const handleTest = () => {
    // 这里应该打开测试对话框
    console.log('测试 Prompt')
  }

  // 复制内容
  const handleCopy = () => {
    navigator.clipboard.writeText(prompt.content)
    // 这里应该显示成功提示
  }

  // 导出Prompt
  const handleExport = () => {
    const dataStr = JSON.stringify(prompt, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${prompt.title || 'prompt'}.json`
    link.click()
    URL.revokeObjectURL(url)
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
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 页面头部 */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center space-x-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/prompts')}
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            返回
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-foreground">
              {isEditing ? '编辑 Prompt' : '新建 Prompt'}
            </h1>
            <p className="text-muted-foreground mt-1">
              {isEditing ? '修改您的提示词模板' : '创建一个新的提示词模板'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPreviewMode(!previewMode)}
          >
            {previewMode ? (
              <>
                <EyeOff className="mr-2 h-4 w-4" />
                编辑
              </>
            ) : (
              <>
                <Eye className="mr-2 h-4 w-4" />
                预览
              </>
            )}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleTest}
          >
            <Play className="mr-2 h-4 w-4" />
            测试
          </Button>
          <Button
            onClick={handleSave}
            disabled={saving || !prompt.title || !prompt.content}
          >
            <Save className="mr-2 h-4 w-4" />
            {saving ? '保存中...' : '保存'}
          </Button>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 主编辑区域 */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* 基本信息 */}
          <Card>
            <CardHeader>
              <CardTitle>基本信息</CardTitle>
              <CardDescription>
                设置 Prompt 的基本信息
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">标题 *</Label>
                <Input
                  id="title"
                  placeholder="请输入 Prompt 标题"
                  value={prompt.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">描述</Label>
                <Textarea
                  id="description"
                  placeholder="请输入 Prompt 描述"
                  value={prompt.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="category">分类</Label>
                <Select
                  value={prompt.category}
                  onValueChange={(value) => handleInputChange('category', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="选择分类" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="writing">写作</SelectItem>
                    <SelectItem value="marketing">营销</SelectItem>
                    <SelectItem value="development">开发</SelectItem>
                    <SelectItem value="analysis">分析</SelectItem>
                    <SelectItem value="creative">创意</SelectItem>
                    <SelectItem value="other">其他</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Prompt 内容 */}
          <Card>
            <CardHeader>
              <CardTitle>Prompt 内容</CardTitle>
              <CardDescription>
                编写您的提示词模板，使用 {'{variable_name}'} 定义变量
              </CardDescription>
            </CardHeader>
            <CardContent>
              {previewMode ? (
                <div className="min-h-[300px] p-4 bg-muted rounded-md">
                  <pre className="whitespace-pre-wrap text-sm">
                    {prompt.content}
                  </pre>
                </div>
              ) : (
                <Textarea
                  placeholder="请输入 Prompt 内容..."
                  value={prompt.content}
                  onChange={(e) => handleInputChange('content', e.target.value)}
                  rows={15}
                  className="font-mono text-sm"
                />
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
          {/* 设置 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="mr-2 h-4 w-4" />
                设置
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label className="text-sm font-medium">公开访问</Label>
                  <p className="text-xs text-muted-foreground">
                    允许其他用户查看此 Prompt
                  </p>
                </div>
                <Switch
                  checked={prompt.is_public}
                  onCheckedChange={(checked) => handleInputChange('is_public', checked)}
                />
              </div>

              <Separator />

              <div className="flex items-center space-x-2">
                {prompt.is_public ? (
                  <>
                    <Globe className="h-4 w-4 text-green-500" />
                    <span className="text-sm text-green-500">公开</span>
                  </>
                ) : (
                  <>
                    <Lock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm text-muted-foreground">私有</span>
                  </>
                )}
              </div>
            </CardContent>
          </Card>

          {/* 标签 */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Tag className="mr-2 h-4 w-4" />
                标签
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {prompt.tags.map((tag) => (
                  <Badge
                    key={tag}
                    variant="secondary"
                    className="cursor-pointer"
                    onClick={() => removeTag(tag)}
                  >
                    {tag} ×
                  </Badge>
                ))}
              </div>

              <div className="flex space-x-2">
                <Input
                  placeholder="添加标签"
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addTag()}
                />
                <Button size="sm" onClick={addTag}>
                  添加
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* 操作 */}
          <Card>
            <CardHeader>
              <CardTitle>操作</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleCopy}
              >
                <Copy className="mr-2 h-4 w-4" />
                复制内容
              </Button>
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={handleExport}
              >
                <Download className="mr-2 h-4 w-4" />
                导出 JSON
              </Button>
            </CardContent>
          </Card>

          {/* 统计信息（编辑模式） */}
          {isEditing && (
            <Card>
              <CardHeader>
                <CardTitle>统计信息</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">版本数量</span>
                  <span>3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">测试次数</span>
                  <span>15</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">创建时间</span>
                  <span>2024-01-15</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">最后更新</span>
                  <span>2024-01-20</span>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default PromptEditor

