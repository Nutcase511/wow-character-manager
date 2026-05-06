# 从魔兽世界客户端获取数据指南

## 🎯 概述

本指南教你如何从本地魔兽世界客户端文件中提取副本、Boss、装备数据，完全无需暴雪API，合法可靠。

## 📁 魔兽世界客户端数据文件

### 数据文件位置
魔兽世界客户端的DBFilesClient目录包含所有游戏数据：

```
World of Warcraft/_classic_/DBFilesClient/
├── JournalInstance.dbc      # 副本信息
├── JournalEncounter.dbc     # Boss信息
├── Item.dbc                 # 装备基础信息
├── ItemSparse.dbc           # 装备详细信息
├── Creature.dbc             # 生物信息
└── ... (更多数据文件)
```

### 常见安装路径
```
C:/Program Files (x86)/World of Warcraft/_classic_/
C:/Games/World of Warcraft/_classic_/
D:/World of Warcraft/_classic_/
```

## 🚀 使用步骤

### 第一步：提取数据

#### 1. 定位魔兽世界目录
找到你的魔兽世界怀旧服客户端安装目录，确认`DBFilesClient`文件夹存在。

#### 2. 运行数据提取脚本
```bash
cd backend
python extract_wow_data.py
```

#### 3. 选择数据来源
脚本会自动查找魔兽世界目录，或让你手动输入路径。

#### 4. 确认提取
输入 `y` 确认开始提取数据。

### 第二步：导入数据

#### 1. 确保MongoDB运行
```bash
# Windows
net start MongoDB

# 或者检查是否已运行
mongo --eval "db.version()"
```

#### 2. 运行数据导入脚本
```bash
cd backend
python import_wow_data.py
```

#### 3. 确认导入
输入 `y` 确认导入数据（会清空现有数据）。

## 📊 数据结构

### 副本数据 (JournalInstance.dbc)
```json
{
  "dungeon_id": 1,
  "name": "纳克萨玛斯",
  "description": "天灾军团的堡垒",
  "map_name": "",
  "minimum_level": 70,
  "modes": ["normal", "heroic"],
  "icon_url": null
}
```

### Boss数据 (JournalEncounter.dbc)
```json
{
  "boss_id": 1107,
  "name": "阿努布雷坎",
  "description": "纳克萨玛斯的第一个Boss",
  "dungeon_id": 1,
  "dungeon_name": "纳克萨玛斯",
  "category": "副本Boss",
  "icon_url": null
}
```

### 装备数据 (ItemSparse.dbc)
```json
{
  "item_id": 12345,
  "name": "黑暗神殿护肩",
  "quality": "epic",
  "item_level": 141,
  "slot": "肩部",
  "stats": {},
  "icon_url": null
}
```

## 🛠️ 工具说明

### extract_wow_data.py
**功能**: 从DBC文件中提取游戏数据

**支持的数据文件**:
- `JournalInstance.dbc` - 副本信息
- `JournalEncounter.dbc` - Boss信息
- `ItemSparse.dbc` - 装备信息

**输出格式**: JSON文件，保存在`wow_data`目录

### import_wow_data.py
**功能**: 将提取的数据导入到MongoDB

**配置选项**:
- `ITEM_LIMIT`: 装备导入数量限制（默认500，避免数据过大）
- `DATA_DIR`: 数据文件目录
- `DATABASE_NAME`: 数据库名称

## ⚙️ 高级配置

### 调整装备导入数量
编辑`import_wow_data.py`:
```python
ITEM_LIMIT = 1000  # 增加到1000个装备
```

### 修改数据文件路径
```python
DATA_DIR = "C:/my_wow_data"  # 自定义数据目录
```

### 只导入特定数据
注释掉不需要的导入部分：
```python
# await importer.import_items(items_file, ITEM_LIMIT)  # 不导入装备
```

## 🔍 数据验证

### 检查提取的数据
```bash
cd wow_data
# 查看副本数据
head -20 instances.json

# 查看Boss数据
head -20 bosses.json

# 查看装备数据
head -20 items.json
```

### 检查导入的数据
```python
# 连接MongoDB检查
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client["wow_character_manager"]

# 检查副本数量
print(f"副本数量: {db.dungeons.count_documents({})}")

# 检查Boss数量
print(f"Boss数量: {db.bosses.count_documents({})}")

# 检查装备数量
print(f"装备数量: {db.items.count_documents({})}")
```

## 🎨 数据质量

### 优势
- ✅ **完整准确**: 来自官方游戏数据
- ✅ **及时更新**: 游戏更新后数据同步更新
- ✅ **零成本**: 无需API费用
- ✅ **完全合法**: 使用自己的游戏客户端数据
- ✅ **无网络依赖**: 无需互联网连接

### 局限性
- ⚠️ 需要游戏客户端安装
- ⚠️ 需要一定的技术操作
- ⚠️ 部分数据需要多个文件配合解析
- ⚠️ 图标需要额外处理

## 🐛 常见问题

### Q1: 找不到魔兽世界目录
**A**: 脚本支持常见安装路径，如果找不到，可以手动输入完整路径。

### Q2: DBC文件解析失败
**A**: 可能是游戏版本不同导致的字段结构变化，需要调整解析逻辑。

### Q3: 数据导入后没有显示
**A**: 检查MongoDB是否正常运行，确认数据导入成功。

### Q4: 装备属性为空
**A**: 简化版本只导入基本信息，完整属性需要解析Item.dbc和其他相关文件。

### Q5: 如何获取装备图标
**A**: 装备图标需要从游戏客户端的纹理文件中提取，或使用第三方图标库。

## 📈 数据量参考

### 典型怀旧服数据量
- 副本: 约20-30个
- Boss: 约200-300个
- 装备: 数千个（建议限制导入数量）

### 推荐配置
```python
ITEM_LIMIT = 500  # 时光服常用装备足够
```

## 🔧 故障排除

### 提取失败
```bash
# 检查文件权限
ls -la DBFilesClient/

# 检查文件是否存在
file JournalInstance.dbc
```

### 导入失败
```bash
# 检查MongoDB连接
mongo --eval "db.version()"

# 检查数据库权限
show dbs
```

### 数据乱码
- 确认使用UTF-8编码
- 检查游戏客户端语言版本

## 🎯 时光服特别优化

### 推荐配置
```python
# 只导入时光服相关的副本
TIME_SERVER_INSTANCES = [1, 2, 3, ...]  # 时光服副本ID

# 只导入时光服等级范围的装备
MIN_ITEM_LEVEL = 1
MAX_ITEM_LEVEL = 80
```

## 📞 技术支持

如果遇到问题：
1. 检查魔兽世界客户端版本
2. 确认DBC文件完整性
3. 查看脚本输出的错误信息
4. 检查MongoDB连接状态

---

**版本**: v1.0.0
**更新**: 2026-05-06
**适用**: 魔兽世界怀旧服客户端
**状态**: ✅ 可用