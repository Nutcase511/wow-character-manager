# 服务器API功能说明

## 🎯 功能概述

为时光服（怀旧服）项目新增了从暴雪API动态获取服务器列表的功能，用户可以通过下拉选择器选择服务器，无需手动输入服务器名称。

## 🚀 新增功能

### 1. 后端API

#### 服务器相关端点
- **GET `/api/realms`** - 获取服务器列表（支持怀旧服/正式服切换）
- **GET `/api/realms/{realm_slug}`** - 获取指定服务器详细信息
- **GET `/api/realms/classic/list`** - 专门获取怀旧服服务器列表
- **GET `/api/realms/retail/list`** - 专门获取正式服服务器列表

#### 查询参数
- `classic` (boolean): 是否获取怀旧服服务器
- `region` (string): 服务器区域过滤（us, eu, kr, tw, cn）

### 2. 前端组件

#### RealmStore (状态管理)
新增了专门的服务器状态管理store：
- `realms` - 所有服务器列表
- `classicRealms` - 怀旧服服务器列表
- `retailRealms` - 正式服服务器列表
- 支持服务器搜索、过滤等功能

#### 角色创建表单更新
- 服务器输入框改为下拉选择器
- 支持服务器搜索功能
- 默认加载怀旧服（时光服）服务器列表
- 提供刷新按钮更新服务器列表

## 📋 使用示例

### 后端调用示例

```python
# 获取怀旧服服务器列表
GET /api/realms/classic/list

# 获取指定区域的服务器
GET /api/realms/classic/list?region=cn

# 获取指定服务器信息
GET /api/realms/stormrage

# 动态切换服务器类型
GET /api/realms?classic=true
```

### 前端调用示例

```typescript
import { realmApi } from '@/api'

// 获取怀旧服服务器列表
const classicRealms = await realmApi.getClassicRealms({ region: 'cn' })

// 获取正式服服务器列表
const retailRealms = await realmApi.getRetailRealms()

// 搜索服务器
import { useRealmStore } from '@/stores/realm'
const realmStore = useRealmStore()
const results = realmStore.searchRealms('艾泽拉斯')
```

## 🎨 界面更新

### 角色创建对话框
```vue
<el-form-item label="服务器" prop="realm">
  <el-select
    v-model="form.realm"
    placeholder="请选择服务器"
    filterable
    remote
    reserve-keyword
    :remote-method="searchRealms"
    :loading="realmStore.loading"
    style="width: 100%"
  >
    <el-option
      v-for="realm in filteredRealms"
      :key="realm.slug"
      :label="realm.name"
      :value="realm.name"
    >
      <span style="float: left">{{ realm.name }}</span>
      <span style="float: right; color: #8492a6; font-size: 13px">
        {{ realm.category }}
      </span>
    </el-option>
  </el-select>
  <div class="form-tip">
    <el-button size="small" link @click="loadClassicRealms">
      <el-icon><Refresh /></el-icon>
      刷新怀旧服服务器
    </el-button>
  </div>
</el-form-item>
```

## 🔧 技术实现

### 暴雪API集成
- 使用动态namespace（`dynamic-classic`）获取怀旧服数据
- 支持OAuth令牌自动刷新
- 错误处理和降级方案

### 数据处理
- 服务器信息包含：ID、名称、slug、分类、时区等
- 支持中文名称显示
- 按区域和分类过滤

### 缓存策略
- 前端Pinia store缓存服务器列表
- 避免频繁API调用
- 支持手动刷新

## 🎯 时光服特性

### 专门优化
- 默认加载怀旧服服务器列表
- 显示服务器分类信息
- 支持中文服务器名称
- 针对国服玩家优化

### 区域支持
- 国服 (cn)
- 美服 (us)
- 欧服 (eu)
- 韩服 (kr)
- 台服 (tw)

## 📊 数据结构

### 服务器对象
```typescript
interface Realm {
  id: number              // 服务器ID
  name: string            // 服务器名称（中文）
  slug: string            // 服务器标识符（英文）
  category: string        // 服务器分类
  locale: string          // 语言环境
  timezone: string        // 时区
  is_tournament: boolean  // 是否为比赛服
  region: string          // 区域
}
```

## 🛠️ 配置说明

### 环境变量
需要在 `.env` 文件中配置暴雪API凭证：
```env
BLIZZARD_CLIENT_ID=你的客户端ID
BLIZZARD_CLIENT_SECRET=你的客户端密钥
BLIZZARD_REGION=cn  # 设置为cn获取国服数据
```

## 🐛 错误处理

### 降级方案
- 如果暴雪API不可用，用户仍可手动输入服务器名称
- 显示友好的错误提示
- 支持重试机制

### 常见问题
1. **API调用失败**: 检查暴雪API凭证是否正确
2. **服务器列表为空**: 检查网络连接和区域设置
3. **中文显示问题**: 确认locale设置正确

## 🚀 未来计划

- [ ] 添加服务器状态监控（在线/离线）
- [ ] 服务器队列信息显示
- [ ] 推荐热门服务器
- [ ] 服务器人口数据显示
- [ ] 支持收藏常用服务器

## 📝 更新日志

### v1.1.0 (2026-05-06)
- ✅ 新增从暴雪API获取服务器列表功能
- ✅ 支持怀旧服和正式服服务器切换
- ✅ 前端服务器选择器优化
- ✅ 添加服务器搜索和过滤功能
- ✅ 新增RealmStore状态管理
- ✅ 针对时光服优化用户体验

---

**适用版本**: v1.1.0+
**更新时间**: 2026-05-06
**主要贡献**: 服务器API集成，提升用户体验