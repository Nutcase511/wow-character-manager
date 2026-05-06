# 时光服服务器API快速使用指南

## 🎯 功能说明

为魔兽世界时光服（怀旧服）项目新增了从暴雪API动态获取服务器列表的功能。用户在创建角色时，可以通过下拉选择器选择服务器，无需手动输入服务器名称。

## 🚀 快速开始

### 1. 配置暴雪API凭证

编辑 `backend/.env` 文件：
```env
BLIZZARD_CLIENT_ID=你的客户端ID
BLIZZARD_CLIENT_SECRET=你的客户端密钥
BLIZZARD_REGION=cn  # 国服设置为cn
```

### 2. 测试API功能

运行测试脚本验证功能：
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python test_realms_api.py
```

### 3. 启动项目

```bash
# 后端
cd backend
python -m uvicorn main:app --reload

# 前端
cd frontend
npm run dev
```

### 4. 使用服务器选择器

1. 访问 http://localhost:5173
2. 点击"角色管理"
3. 点击"添加角色"
4. 在服务器字段中，输入服务器名称进行搜索
5. 从下拉列表中选择服务器

## 📋 API端点

### 获取服务器列表

```bash
# 获取怀旧服服务器（时光服）
GET /api/realms/classic/list

# 获取正式服服务器
GET /api/realms/retail/list

# 动态切换
GET /api/realms?classic=true

# 按区域过滤
GET /api/realms/classic/list?region=cn
```

### 获取指定服务器信息

```bash
GET /api/realms/{realm_slug}

# 示例
GET /api/realms/stormrage
GET /api/realms/艾泽拉斯
```

## 💡 前端使用示例

### 在组件中使用RealmStore

```vue
<script setup lang="ts">
import { useRealmStore } from '@/stores/realm'
import { onMounted } from 'vue'

const realmStore = useRealmStore()

onMounted(async () => {
  // 加载怀旧服服务器列表
  await realmStore.fetchClassicRealms()
})

// 搜索服务器
function searchServers(query: string) {
  const results = realmStore.searchRealms(query)
  console.log('搜索结果:', results)
}
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

### 直接调用API

```typescript
import { realmApi } from '@/api'

// 获取怀旧服服务器
const classicRealms = await realmApi.getClassicRealms({ region: 'cn' })

// 获取正式服服务器
const retailRealms = await realmApi.getRetailRealms()

// 获取指定服务器
const realm = await realmApi.getById('stormrage', { classic: false })
```

## 🎨 数据结构

### 服务器对象
```typescript
{
  id: number,              // 服务器ID
  name: string,            // 服务器名称（中文）
  slug: string,            // 服务器标识符（英文）
  category: string,        // 服务器分类
  locale: string,          // 语言环境
  timezone: string,        // 时区
  is_tournament: boolean,  // 是否为比赛服
  region: string           // 区域
}
```

## 🔍 搜索功能

### 前端搜索
```vue
<el-select
  v-model="selectedRealm"
  filterable
  remote
  :remote-method="searchRealms"
  placeholder="搜索服务器"
>
  <el-option
    v-for="realm in searchResults"
    :key="realm.slug"
    :label="realm.name"
    :value="realm.name"
  />
</el-select>

<script setup lang="ts">
const searchResults = ref([])

function searchRealms(query: string) {
  searchResults.value = realmStore.searchRealms(query)
}
</script>
```

### 后端搜索
```python
# 在store中实现搜索逻辑
def search_realms(self, query: str):
    return [r for r in self.realms if query in r['name'] or query in r['slug']]
```

## 🛠️ 故障排除

### 问题1: 无法获取服务器列表

**可能原因:**
- 暴雪API凭证配置错误
- 网络连接问题
- API服务暂时不可用

**解决方案:**
1. 检查 `.env` 文件配置
2. 运行测试脚本验证API连接
3. 用户仍可手动输入服务器名称

### 问题2: 服务器名称显示为英文

**可能原因:**
- locale设置不正确
- 区域设置错误

**解决方案:**
1. 确认 `BLIZZARD_REGION=cn`
2. 检查服务器对象的 `locale` 字段
3. 使用中文服务器名称进行搜索

### 问题3: 搜索功能不工作

**可能原因:**
- 前端搜索逻辑错误
- 数据加载不完整

**解决方案:**
1. 检查 `searchRealms` 方法实现
2. 确认服务器列表已正确加载
3. 查看浏览器控制台错误信息

## 📊 性能优化

### 前端缓存
```typescript
// RealmStore已实现缓存
const realmStore = useRealmStore()

// 首次加载后会缓存，后续直接使用缓存数据
await realmStore.fetchClassicRealms()
```

### 懒加载
```vue
<!-- 只在需要时加载服务器列表 -->
<el-select @focus="loadRealms">
  <!-- 选项 -->
</el-select>

<script setup lang="ts">
async function loadRealms() {
  if (!realmStore.hasRealms) {
    await realmStore.fetchClassicRealms()
  }
}
</script>
```

## 🎯 时光服特色功能

### 国服优化
- 默认加载国服服务器列表
- 显示中文服务器名称
- 针对国服时区优化

### 怀旧服专用
- 使用 `dynamic-classic` namespace
- 获取怀旧服特定数据
- 支持怀旧服版本的服务器

### 常用服务器快捷访问
```typescript
// 获取常用服务器
const popularRealms = realmStore.classicRealms.filter(r =>
  ['艾泽拉斯', '奥罗', '哈霍兰', '庇护之剑'].includes(r.name)
)
```

## 🔮 未来功能

- [ ] 服务器状态显示（在线/排队）
- [ ] 服务器人口数据
- [ ] 收藏常用服务器
- [ ] 服务器推荐系统
- [ ] 历史选择记录

## 📞 技术支持

如遇到问题，请：
1. 查看控制台错误信息
2. 运行测试脚本验证API
3. 检查网络连接和配置
4. 参考详细文档: `REALM_API_FEATURE.md`

---

**版本**: v1.1.0
**更新**: 2026-05-06
**适用**: 魔兽世界时光服（怀旧服）