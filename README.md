# 魔兽世界角色管理系统 (WoW Character Manager)

## 🎮 项目简介
专门为魔兽世界时光服（怀旧服）设计的角色和装备管理系统。

## ✨ 核心功能
- 🎭 **多角色管理** - 管理多个魔兽世界角色信息
- 🏰 **副本追踪** - 记录副本进度和Boss击杀情况
- ⚔️ **Boss管理** - 管理Boss信息和掉落
- 🎯 **装备需求** - 追踪需要的装备和获取进度
- 📊 **进度统计** - 可视化展示装备获取进度

## 🚀 技术栈

### 后端
- **Python 3.8+**
- **FastAPI** - 现代Web框架
- **MongoDB** - NoSQL数据库
- **Motor** - 异步MongoDB驱动

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **TypeScript** - 类型安全
- **Element Plus** - Vue 3 组件库
- **Pinia** - 状态管理
- **Vite** - 构建工具

## 📋 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MongoDB 4.4+

### 安装步骤

#### 1. 克隆项目
```bash
git clone https://github.com/Nutcase511/wow-character-manager.git
cd wow-character-manager
```

#### 2. 后端设置
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### 3. 配置环境变量
```bash
cd backend
cp .env.example .env
# 编辑.env文件，配置MongoDB连接
```

#### 4. 前端设置
```bash
cd frontend
npm install
```

#### 5. 启动服务
```bash
# 后端 (终端1)
cd backend
python -m uvicorn main:app --reload

# 前端 (终端2)
cd frontend
npm run dev
```

#### 6. 访问应用
- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 🎯 时光服特性

### 服务器选择
- 时光1、时光2、时光3、时光4
- 简化的服务器选择器

### 角色设置
- 默认等级80（时光服最高等级）
- 完整的专精选择（37个专精选项）
- 支持联盟和部落

## 📁 项目结构
```
wow-character-manager/
├── backend/              # 后端服务
│   ├── app/             # 应用核心
│   ├── main.py          # 应用入口
│   └── requirements.txt # Python依赖
├── frontend/            # 前端应用
│   ├── src/             # 源代码
│   └── package.json     # Node依赖
└── README.md            # 项目说明
```

## 🔧 开发指南

### 添加新功能
1. 后端: 在 `backend/app/api/` 添加API端点
2. 前端: 在 `frontend/src/views/` 添加页面组件
3. 类型: 在 `frontend/src/types/` 定义TypeScript类型

### 数据管理
项目支持从本地魔兽世界客户端提取数据：
- 运行 `python extract_wow_data.py` 提取游戏数据
- 运行 `python import_wow_data.py` 导入到数据库

## 📝 更新日志

### v1.2.0 (2026-05-06)
- ✅ 简化服务器选择（时光1-4）
- ✅ 优化专精选择（下拉选择器）
- ✅ 调整默认等级（80级）
- ✅ 移除暴雪API依赖

### v1.1.0 (2026-05-06)
- ✅ 暴雪API服务器集成
- ✅ RealmStore状态管理
- ✅ 服务器搜索和过滤功能

### v1.0.0 (2026-05-06)
- ✅ 基础角色管理功能
- ✅ 装备需求追踪系统
- ✅ 副本和Boss管理

## 🤝 贡献
欢迎提交Issue和Pull Request！

## 📄 许可证
MIT License

## 📞 联系方式
- GitHub: https://github.com/Nutcase511/wow-character-manager
- Issues: https://github.com/Nutcase511/wow-character-manager/issues

---

**专为时光服玩家打造** 🎮✨