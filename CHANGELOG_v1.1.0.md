# 功能更新日志 - 服务器API集成

## 🎯 v1.1.0 - 时光服服务器API集成

**发布日期**: 2026-05-06
**主要更新**: 为时光服项目新增从暴雪API动态获取服务器列表的功能

---

## ✨ 新增功能

### 🌐 后端API

#### 1. 服务器管理API (`/api/realms`)
- **GET `/api/realms`** - 获取服务器列表，支持怀旧服/正式服切换
- **GET `/api/realms/{slug}`** - 获取指定服务器详细信息
- **GET `/api/realms/classic/list`** - 专门获取怀旧服服务器列表
- **GET `/api/realms/retail/list`** - 专门获取正式服服务器列表

#### 2. 暴雪API服务增强
- 新增 `get_realms(classic=False)` 方法
- 新增 `get_realm(realm_slug, classic=False)` 方法
- 支持动态namespace切换（`dynamic-classic` / `dynamic`）
- 支持按区域过滤服务器

#### 3. 数据模型
- 新增 `RealmResponse` schema，定义服务器响应格式
- 支持服务器ID、名称、slug、分类、时区等完整信息

### 🎨 前端功能

#### 1. RealmStore (状态管理)
- 新增专门的服务器状态管理store
- 支持怀旧服和正式服服务器分别管理
- 实现服务器搜索、过滤功能
- 提供多种查询方法（按名称、slug、区域、分类）

#### 2. 角色创建表单优化
- 服务器输入框升级为下拉选择器
- 支持服务器实时搜索
- 显示服务器分类信息
- 提供服务器列表刷新按钮
- 默认加载怀旧服服务器列表

#### 3. API调用封装
- 新增 `realmApi` 模块，封装所有服务器相关API调用
- 提供类型安全的TypeScript接口
- 统一的错误处理机制

---

## 🔧 技术改进

### 后端改进
- **暴雪API服务**: 支持动态namespace参数，适配不同游戏版本
- **错误处理**: 完善的错误捕获和用户友好的错误提示
- **降级方案**: API不可用时仍支持手动输入服务器名称

### 前端改进
- **状态管理**: 新增RealmStore，统一管理服务器状态
- **用户体验**: 搜索、过滤、缓存等优化功能
- **类型安全**: 完整的TypeScript类型定义
- **响应式设计**: 支持大量服务器数据的流畅展示

---

## 📋 数据结构

### 服务器对象
```typescript
interface Realm {
  id: number              // 服务器ID
  name: string            // 服务器名称（支持中文）
  slug: string            // 服务器标识符
  category: string        // 服务器分类
  locale: string          // 语言环境
  timezone: string        // 时区
  is_tournament: boolean  // 是否为比赛服
  region: string           // 区域
}
```

---

## 🚀 使用示例

### 后端API调用
```bash
# 获取怀旧服服务器列表
curl http://localhost:8000/api/realms/classic/list

# 获取指定区域的服务器
curl http://localhost:8000/api/realms/classic/list?region=cn

# 获取指定服务器信息
curl http://localhost:8000/api/realms/stormrage
```

### 前端组件使用
```vue
<script setup lang="ts">
import { useRealmStore } from '@/stores/realm'

const realmStore = useRealmStore()

// 加载怀旧服服务器
await realmStore.fetchClassicRealms()

// 搜索服务器
const results = realmStore.searchRealms('艾泽拉斯')
</script>

<template>
  <el-select v-model="selectedRealm" filterable>
    <el-option
      v-for="realm in realmStore.classicRealms"
      :key="realm.slug"
      :label="realm.name"
      :value="realm.name"
    />
  </el-select>
</template>
```

---

## 🎯 时光服特色

### 专门优化
1. **默认怀旧服**: 系统默认加载和优先显示怀旧服服务器列表
2. **中文支持**: 完整支持中文服务器名称显示和搜索
3. **国服优化**: 针对国服玩家的时区和语言环境优化
4. **分类显示**: 显示服务器分类信息，帮助用户快速识别

### 用户体验提升
- **智能搜索**: 支持中英文服务器名称搜索
- **实时过滤**: 输入时实时过滤服务器列表
- **快捷刷新**: 一键刷新最新服务器列表
- **降级方案**: API不可用时仍可手动输入

---

## 📁 文件变更

### 新增文件
```
backend/
├── app/api/realms.py              # 服务器API路由
└── test_realms_api.py             # API测试脚本

frontend/
└── src/stores/realm.ts            # 服务器状态管理

文档/
├── REALM_API_FEATURE.md           # 功能详细说明
└── REALM_QUICK_GUIDE.md           # 快速使用指南
```

### 修改文件
```
backend/
├── app/services/blizzard_api.py   # 新增服务器获取方法
├── app/schemas/schemas.py         # 新增RealmResponse schema
└── main.py                        # 注册realms路由

frontend/
├── src/api/index.ts               # 新增realmApi模块
├── src/types/index.ts             # 新增Realm类型定义
└── src/views/CharactersView.vue   # 优化服务器选择器

文档/
├── backend/app/api/.claude.md     # 更新API文档
├── backend/app/services/.claude.md # 更新服务文档
├── frontend/src/stores/.claude.md # 更新store文档
└── frontend/src/api/.claude.md    # 更新API文档
```

---

## 🧪 测试

### 测试脚本
新增 `test_realms_api.py` 测试脚本，包含：
- 怀旧服服务器列表获取测试
- 正式服服务器列表获取测试
- 指定服务器信息获取测试
- 服务器搜索功能测试
- 服务器过滤功能测试

### 运行测试
```bash
cd backend
python test_realms_api.py
```

---

## 📝 配置要求

### 环境变量
需要在 `backend/.env` 中配置：
```env
BLIZZARD_CLIENT_ID=你的客户端ID
BLIZZARD_CLIENT_SECRET=你的客户端密钥
BLIZZARD_REGION=cn  # 国服设置为cn
```

### 依赖更新
无需新增依赖，使用现有的暴雪API集成

---

## 🐛 已知问题

1. **API限流**: 暴雪API有调用频率限制，大量请求可能被限流
2. **网络依赖**: 需要稳定的网络连接访问暴雪API
3. **数据同步**: 服务器列表可能不是实时更新的

### 解决方案
- 实现前端缓存，减少API调用
- 提供降级方案，支持手动输入
- 添加刷新按钮，用户可手动更新数据

---

## 🚀 后续计划

### 短期计划
- [ ] 添加服务器状态监控（在线/离线）
- [ ] 实现服务器收藏功能
- [ ] 添加服务器人口数据显示
- [ ] 优化大数据量下的性能

### 长期计划
- [ ] 服务器推荐算法
- [ ] 历史选择记录
- [ ] 服务器对比功能
- [ ] 多区域服务器管理

---

## 📞 技术支持

### 文档资源
- **功能说明**: `REALM_API_FEATURE.md`
- **快速指南**: `REALM_QUICK_GUIDE.md`
- **API文档**: http://localhost:8000/docs

### 常见问题
1. **如何获取暴雪API凭证？**
   - 访问 https://develop.battle.net/ 注册开发者账号

2. **API调用失败怎么办？**
   - 检查凭证配置，运行测试脚本验证
   - 用户仍可手动输入服务器名称

3. **如何切换怀旧服/正式服？**
   - 前端自动加载怀旧服，可通过API参数切换

---

## 🎉 总结

本次更新为时光服项目新增了完整的服务器API集成功能，大幅提升了用户体验。用户现在可以通过下拉选择器轻松选择服务器，系统会自动从暴雪API获取最新的服务器列表，支持搜索、过滤等多种便捷功能。

**核心价值**:
- ✅ 自动化服务器列表获取，无需手动维护
- ✅ 智能搜索和过滤，提升选择效率
- ✅ 完整的降级方案，保证系统可用性
- ✅ 专门针对时光服优化，符合用户需求

---

**版本**: v1.1.0
**发布时间**: 2026-05-06
**更新类型**: 功能增强
**影响范围**: 服务器选择功能