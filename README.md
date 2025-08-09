# Prompt Manager - 极简提示词管理平台

> 让创意更有序，让工作更高效

一个现代化的提示词管理系统，采用极简设计理念，为AI时代的创作者提供强大而优雅的工具。

## ✨ 特色功能

### 🎯 核心功能
- **智能管理** - 创建、编辑、分类和搜索您的提示词模板
- **版本控制** - 完整的版本历史记录，随时回滚到任意版本
- **协作编辑** - 团队协作，共享和改进提示词模板
- **AI测试** - 集成多种AI模型，实时测试提示词效果
- **标签分类** - 灵活的标签系统，快速定位所需模板

### 🎨 设计理念
- **极简美学** - 遵循"少即是多"的设计原则
- **用户体验** - 师从乔布斯和张小龙的产品哲学
- **响应式设计** - 完美适配桌面和移动设备
- **深色模式** - 护眼的深色主题支持

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.11** - 现代Python开发
- **Flask** - 轻量级Web框架
- **SQLAlchemy** - 优雅的ORM映射
- **SQLite** - 轻量级数据库（可扩展至PostgreSQL）

### 前端技术栈
- **React 18** - 现代化前端框架
- **Vite** - 极速构建工具
- **Tailwind CSS** - 原子化CSS框架
- **shadcn/ui** - 高质量组件库
- **Framer Motion** - 流畅动画效果

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Git

### 后端启动

```bash
# 克隆项目
git clone <repository-url>
cd prompt_manager_project

# 进入后端目录
cd backend/prompt_manager_api

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件，设置必要的配置

# 启动服务
python src/main.py
```

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 `http://localhost:5173` 即可使用应用。

## 📁 项目结构

```
prompt_manager_project/
├── backend/                    # 后端代码
│   └── prompt_manager_api/
│       ├── src/
│       │   ├── config/        # 配置管理
│       │   ├── models/        # 数据模型
│       │   ├── services/      # 业务逻辑
│       │   ├── routes/        # API路由
│       │   └── main.py        # 应用入口
│       ├── logs/              # 日志文件
│       ├── .env.template      # 环境变量模板
│       └── requirements.txt   # Python依赖
├── frontend/                   # 前端代码
│   ├── src/
│   │   ├── components/        # React组件
│   │   ├── pages/            # 页面组件
│   │   ├── contexts/         # React Context
│   │   ├── lib/              # 工具库
│   │   └── App.jsx           # 应用入口
│   ├── public/               # 静态资源
│   └── package.json          # Node.js依赖
├── docs/                      # 项目文档
├── .gitignore                # Git忽略文件
└── README.md                 # 项目说明
```

## 🎯 核心特性

### 数据模型设计
- **用户系统** - 完整的用户注册、登录、权限管理
- **提示词管理** - 支持分类、标签、版本控制
- **协作功能** - 多用户协作编辑和权限控制
- **测试记录** - AI模型测试历史和结果分析

### API设计
- **RESTful架构** - 标准的REST API设计
- **统一响应格式** - 一致的API响应结构
- **错误处理** - 完善的错误码和异常处理
- **日志记录** - 详细的操作日志和性能监控

### 前端架构
- **组件化设计** - 可复用的React组件
- **状态管理** - Context API + Hooks
- **路由管理** - React Router v6
- **主题系统** - 深色/浅色模式切换

## 🔧 配置说明

### 环境变量配置

后端 `.env` 文件：
```env
# 应用配置
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key

# 数据库配置
DATABASE_URL=sqlite:///prompt_manager.db

# 日志配置
LOG_LEVEL=DEBUG
LOG_FILE_PATH=logs/

# AI API配置（可选）
OPENAI_API_KEY=your-openai-api-key
```

前端环境变量：
```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## 📖 API文档

### 用户相关
- `POST /api/users/` - 用户注册
- `POST /api/users/login` - 用户登录
- `GET /api/users/{id}` - 获取用户信息
- `PUT /api/users/{id}` - 更新用户信息

### 提示词相关
- `GET /api/prompts` - 获取提示词列表
- `POST /api/prompts` - 创建提示词
- `GET /api/prompts/{id}` - 获取提示词详情
- `PUT /api/prompts/{id}` - 更新提示词
- `DELETE /api/prompts/{id}` - 删除提示词

详细API文档请参考 [API Documentation](docs/api.md)

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- 设计灵感来源于乔布斯的极简美学和张小龙的产品哲学
- 感谢所有开源项目的贡献者
- 特别感谢AI时代的创作者们

## 📞 联系我们

- 项目主页：[GitHub Repository](https://github.com/your-username/prompt-manager)
- 问题反馈：[Issues](https://github.com/your-username/prompt-manager/issues)
- 功能建议：[Discussions](https://github.com/your-username/prompt-manager/discussions)

---

**Prompt Manager** - 为AI时代而生的极简提示词管理平台 ✨

