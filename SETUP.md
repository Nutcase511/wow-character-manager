# 魔兽世界角色管理系统 - 配置指南

## 系统要求

### 后端
- Python 3.8+
- MongoDB 4.4+

### 前端
- Node.js 16+
- npm 或 yarn

## 安装步骤

### 1. 克隆项目
```bash
cd wow-character-manager
```

### 2. 配置暴雪API

#### 获取暴雪API凭证
1. 访问 [Battle.net Developer Portal](https://develop.battle.net/)
2. 登录你的Battle.net账号
3. 创建新的API客户端
4. 记录下 `Client ID` 和 `Client Secret`

#### 配置后端环境变量
```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填入你的暴雪API凭证：
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=wow_character_manager

# Blizzard API Configuration
BLIZZARD_CLIENT_ID=你的客户端ID
BLIZZARD_CLIENT_SECRET=你的客户端密钥
BLIZZARD_REGION=cn  # 可选: us, eu, kr, tw, cn

# Application Configuration
APP_NAME=WoW Character Manager
APP_VERSION=1.0.0
DEBUG=True

# CORS Configuration
FRONTEND_URL=http://localhost:5173
```

### 3. 安装MongoDB

#### Windows
1. 下载MongoDB Community Server: https://www.mongodb.com/try/download/community
2. 运行安装程序，使用默认设置
3. 确保MongoDB服务正在运行

#### macOS
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 4. 启动项目

#### Windows
双击运行 `start.bat`

#### macOS/Linux
```bash
chmod +x start.sh
./start.sh
```

#### 手动启动

**启动后端:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**启动前端:**
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

- 前端界面: http://localhost:5173
- 后端API文档: http://localhost:8000/docs
- API根路径: http://localhost:8000

## 功能使用说明

### 1. 角色管理
- 添加你的魔兽世界角色
- 支持多角色管理
- 记录角色职业、专精、等级等信息

### 2. 副本管理
- 手动添加副本信息
- 从暴雪API同步副本数据（需要副本的Journal Instance ID）
- 记录副本难度、最低等级等信息

### 3. Boss管理
- 手动添加Boss信息
- 从暴雪API同步Boss数据（需要Boss的Journal Encounter ID）
- 关联Boss到对应的副本

### 4. 装备需求
- 为角色添加需要的装备
- 记录装备来源（哪个Boss掉落）
- 设置装备优先级
- 标记装备获取状态
- 查看装备获取进度

### 5. 暴雪API集成

#### 查找副本ID
1. 访问暴雪API文档或使用魔兽世界数据库网站
2. 搜索你想要的副本
3. 找到对应的Journal Instance ID
4. 在副本管理页面使用"从暴雪API同步"功能

#### 查找BossID
1. 同上，找到Boss的Journal Encounter ID
2. 在Boss管理页面同步数据

#### 查找装备ID
1. 访问魔兽世界数据库网站（如 wowhead.com）
2. 搜索装备名称
3. 在URL中找到装备ID
4. 添加装备需求时使用该ID

系统会自动获取装备的图标、属性等信息

## 常见问题

### MongoDB连接失败
- 确保MongoDB服务正在运行
- 检查 `MONGODB_URL` 配置是否正确
- 检查防火墙设置

### 暴雪API请求失败
- 检查 `BLIZZARD_CLIENT_ID` 和 `BLIZZARD_CLIENT_SECRET` 是否正确
- 确认API客户端是否有访问权限
- 检查网络连接

### 前端无法连接后端
- 确保后端服务正在运行（http://localhost:8000）
- 检查 `FRONTEND_URL` 配置
- 检查CORS设置

## 开发说明

### 项目结构
```
wow-character-manager/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── schemas/        # Pydantic模式
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API调用
│   │   ├── components/    # Vue组件
│   │   ├── stores/        # Pinia状态管理
│   │   ├── types/         # TypeScript类型
│   │   ├── views/         # 页面视图
│   │   └── router/        # 路由配置
│   └── package.json       # Node依赖
└── README.md              # 项目说明
```

### 技术栈
- **后端**: Python + FastAPI + MongoDB
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia
- **API**: 暴雪游戏数据API

## 许可证
MIT License