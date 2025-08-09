# 部署指南

## GitHub代码推送指南

由于GitHub已停止支持密码认证，您需要使用以下方式之一来推送代码：

### 方式一：使用Personal Access Token (推荐)

1. **生成Personal Access Token**
   - 登录GitHub，点击右上角头像
   - 选择 `Settings` → `Developer settings` → `Personal access tokens` → `Tokens (classic)`
   - 点击 `Generate new token (classic)`
   - 设置名称和过期时间
   - 权限勾选：`repo`（完整仓库访问权限）
   - 点击 `Generate token` 并复制token

2. **推送代码**
   ```bash
   cd /path/to/prompt_manager_project
   git push -u origin main
   # 用户名：yesiran
   # 密码：粘贴您的Personal Access Token
   ```

### 方式二：使用SSH密钥 (推荐)

1. **生成SSH密钥**
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **添加SSH密钥到GitHub**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   复制输出内容，在GitHub Settings → SSH and GPG keys 中添加

3. **更改远程仓库URL为SSH**
   ```bash
   git remote set-url origin git@github.com:yesiran/prompt_manus.git
   git push -u origin main
   ```

### 方式三：直接上传到GitHub网页

1. 在GitHub仓库页面点击 `uploading an existing file`
2. 将项目文件夹压缩为zip
3. 拖拽上传到GitHub

## 本地开发环境搭建

### 后端环境

```bash
# 克隆仓库
git clone https://github.com/yesiran/prompt_manus.git
cd prompt_manus

# 进入后端目录
cd backend/prompt_manager_api

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install flask flask-sqlalchemy flask-cors python-dotenv

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件设置必要配置

# 启动后端服务
python src/main.py
```

### 前端环境

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

## 生产环境部署

### 使用Docker部署 (推荐)

1. **创建Dockerfile**
   ```dockerfile
   # 后端Dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY backend/prompt_manager_api/ .
   RUN pip install -r requirements.txt
   EXPOSE 5000
   CMD ["python", "src/main.py"]
   ```

2. **创建docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     backend:
       build: .
       ports:
         - "5000:5000"
       environment:
         - FLASK_ENV=production
     
     frontend:
       image: nginx:alpine
       ports:
         - "80:80"
       volumes:
         - ./frontend/dist:/usr/share/nginx/html
   ```

### 云平台部署

#### Vercel (前端)
```bash
cd frontend
npm run build
# 连接Vercel账户并部署
```

#### Railway/Render (后端)
- 连接GitHub仓库
- 设置构建命令：`pip install -r requirements.txt`
- 设置启动命令：`python src/main.py`

## 环境变量配置

### 后端 (.env)
```env
# 应用配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-key-here

# 数据库配置
DATABASE_URL=sqlite:///prompt_manager.db

# 日志配置
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/

# CORS配置
CORS_ORIGINS=https://your-frontend-domain.com

# AI API配置 (可选)
OPENAI_API_KEY=your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
```

### 前端 (.env)
```env
VITE_API_BASE_URL=https://your-backend-domain.com/api
```

## 数据库迁移

```bash
# 进入后端目录
cd backend/prompt_manager_api

# 激活虚拟环境
source venv/bin/activate

# 运行应用（自动创建数据库表）
python src/main.py
```

## 常见问题解决

### 1. 端口冲突
```bash
# 查看端口占用
lsof -i :5000
# 杀死进程
kill -9 <PID>
```

### 2. 依赖安装失败
```bash
# 升级pip
pip install --upgrade pip
# 清除缓存
pip cache purge
```

### 3. 前端构建失败
```bash
# 清除node_modules
rm -rf node_modules package-lock.json
npm install
```

## 监控和日志

### 日志查看
```bash
# 后端日志
tail -f backend/prompt_manager_api/logs/prompt_manager.log

# 系统日志
journalctl -u your-service-name -f
```

### 性能监控
- 使用 `htop` 监控系统资源
- 使用 `nginx` 访问日志分析流量
- 配置 `prometheus` + `grafana` 进行详细监控

## 备份策略

### 数据库备份
```bash
# SQLite备份
cp prompt_manager.db backup_$(date +%Y%m%d_%H%M%S).db

# 定时备份脚本
echo "0 2 * * * cp /path/to/prompt_manager.db /backup/prompt_manager_$(date +\%Y\%m\%d).db" | crontab -
```

### 代码备份
```bash
# 定期推送到GitHub
git add .
git commit -m "Auto backup $(date)"
git push origin main
```

