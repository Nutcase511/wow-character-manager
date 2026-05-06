# 🚀 快速启动指南

## ✅ 依赖已安装完成！

所有必需的依赖包已经成功安装，可以开始使用系统了。

## 📋 启动前检查清单

- [x] Python 3.12.10 已安装
- [x] Node.js v24.13.0 已安装
- [x] Python 后端依赖已安装
- [x] Node.js 前端依赖已安装
- [ ] MongoDB 服务正在运行
- [ ] 暴雪API凭证已配置

## 🎯 快速启动（3步）

### 第一步：配置环境变量
```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填入你的暴雪API凭证
```

### 第二步：启动MongoDB
```bash
# Windows
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongodb
```

### 第三步：启动项目
```bash
# Windows - 双击运行
start.bat

# macOS/Linux - 给予执行权限后运行
chmod +x start.sh
./start.sh
```

## 🌐 访问地址

启动成功后，访问以下地址：

- **前端界面**: http://localhost:5173
- **后端API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🎮 开始使用

### 1. 添加你的第一个角色
1. 打开前端界面 http://localhost:5173
2. 点击"角色管理"
3. 点击"添加角色"按钮
4. 填写角色信息（名称、服务器、职业等）

### 2. 配置暴雪API（可选但推荐）
1. 访问 https://develop.battle.net/
2. 创建API客户端获取凭证
3. 在 `backend/.env` 文件中配置：
   ```env
   BLIZZARD_CLIENT_ID=你的客户端ID
   BLIZZARD_CLIENT_SECRET=你的客户端密钥
   ```

### 3. 添加装备需求
1. 进入角色详情页面
2. 点击"添加装备需求"
3. 输入装备ID（可在 wowhead.com 等网站查找）
4. 系统会自动获取装备图标和属性信息

## 🛠️ 手动启动（如果脚本失败）

### 启动后端
```bash
cd backend
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

python -m uvicorn main:app --reload
```

### 启动前端（新终端窗口）
```bash
cd frontend
npm run dev
```

## 📱 功能预览

- 🎭 **多角色管理** - 管理你的所有魔兽世界角色
- 🏰 **副本追踪** - 记录副本进度和Boss击杀情况
- ⚔️ **Boss管理** - 管理Boss信息和掉落
- 🎯 **装备需求** - 追踪需要的装备和获取进度
- 🖼️ **暴雪图标** - 自动获取官方装备和Boss图标
- 📊 **进度统计** - 可视化展示装备获取进度

## ❓ 常见问题

### Q: 启动脚本失败怎么办？
A: 使用手动启动方式，分别启动后端和前端。

### Q: MongoDB连接失败？
A: 确保MongoDB服务正在运行，检查连接字符串配置。

### Q: 暴雪API请求失败？
A: 检查 `.env` 文件中的API凭证是否正确，网络连接是否正常。

### Q: 前端无法连接后端？
A: 确保后端运行在 8000 端口，检查CORS配置。

## 📚 更多信息

- **详细配置说明**: 查看 `SETUP.md`
- **安装完成报告**: 查看 `INSTALLATION_COMPLETE.md`
- **项目说明**: 查看 `README.md`

---

**准备好了吗？开始管理你的魔兽世界角色吧！** 🎮✨