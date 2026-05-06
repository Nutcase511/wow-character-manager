# 时光服简化配置说明

## 🎯 更新内容

根据时光服项目需求，对角色创建功能进行了以下简化：

### 1. 服务器选择简化
- ❌ 移除暴雪API集成
- ✅ 固定提供4个服务器选项：时光1、时光2、时光3、时光4
- ✅ 使用简单的下拉选择器

### 2. 角色等级默认调整
- ✅ 默认等级从70调整为80（时光服最高等级）
- ✅ 添加提示信息："时光服最高等级为80"

### 3. 专精选择优化
- ❌ 移除手动输入
- ✅ 改为下拉选择器
- ✅ 预置所有职业专精选项

## 📋 具体修改

### 服务器选择
```vue
<el-form-item label="服务器" prop="realm">
  <el-select v-model="form.realm" placeholder="请选择服务器" style="width: 100%">
    <el-option label="时光1" value="时光1" />
    <el-option label="时光2" value="时光2" />
    <el-option label="时光3" value="时光3" />
    <el-option label="时光4" value="时光4" />
  </el-select>
</el-form-item>
```

### 专精选择
```vue
<el-form-item label="专精" prop="spec">
  <el-select v-model="form.spec" placeholder="请选择专精" style="width: 100%">
    <!-- 战士 -->
    <el-option label="防护" value="防护" />
    <el-option label="武器" value="武器" />
    <el-option label="狂暴" value="狂暴" />

    <!-- 圣骑士 -->
    <el-option label="神圣" value="神圣" />
    <el-option label="惩戒" value="惩戒" />

    <!-- 猎人 -->
    <el-option label="野兽" value="野兽" />
    <el-option label="射击" value="射击" />
    <el-option label="生存" value="生存" />

    <!-- 潜行者 -->
    <el-option label="刺杀" value="刺杀" />
    <el-option label="战斗" value="战斗" />
    <el-option label="敏锐" value="敏锐" />

    <!-- 牧师 -->
    <el-option label="戒律" value="戒律" />
    <el-option label="暗影" value="暗影" />
    <el-option label="神圣" value="神圣" />

    <!-- 死亡骑士 -->
    <el-option label="鲜血" value="鲜血" />
    <el-option label="冰霜" value="冰霜" />
    <el-option label="邪恶" value="邪恶" />

    <!-- 萨满 -->
    <el-option label="元素" value="元素" />
    <el-option label="增强" value="增强" />
    <el-option label="恢复" value="恢复" />

    <!-- 法师 -->
    <el-option label="奥术" value="奥术" />
    <el-option label="火焰" value="火焰" />
    <el-option label="冰霜" value="冰霜" />

    <!-- 术士 -->
    <el-option label="痛苦" value="痛苦" />
    <el-option label="恶魔" value="恶魔" />
    <el-option label="毁灭" value="毁灭" />

    <!-- 武僧 -->
    <el-option label="酒仙" value="酒仙" />
    <el-option label="织雾" value="织雾" />
    <el-option label="踏风" value="踏风" />

    <!-- 德鲁伊 -->
    <el-option label="平衡" value="平衡" />
    <el-option label="野性" value="野性" />
    <el-option label="守护" value="守护" />
    <el-option label="恢复" value="恢复" />

    <!-- 恶魔猎手 -->
    <el-option label="浩劫" value="浩劫" />
    <el-option label="复仇" value="复仇" />

    <!-- 唤魔师 -->
    <el-option label="增辉" value="增辉" />
    <el-option label="湮灭" value="湮灭" />
    <el-option label="恩护" value="恩护" />
  </el-select>
</el-form-item>
```

### 等级设置
```vue
<el-form-item label="等级" prop="level">
  <el-input-number v-model="form.level" :min="1" :max="80" />
  <div class="form-tip">时光服最高等级为80</div>
</el-form-item>
```

## 🧹 代码清理

### 移除的导入
```typescript
// 移除这些不再需要的导入
import { useRealmStore } from '@/stores/realm'
import { Refresh } from '@element-plus/icons-vue'
import { computed, watch } from 'vue'
```

### 移除的变量
```typescript
// 移除这些状态变量
const realmStore = useRealmStore()
const realmSearchQuery = ref('')
const useClassicRealms = ref(true)
const filteredRealms = computed(() => { ... })
```

### 移除的方法
```typescript
// 移除这些方法
async function loadClassicRealms() { ... }
async function loadRetailRealms() { ... }
function searchRealms(query: string) { ... }
// 移除watch监听
watch(useClassicRealms, (newValue) => { ... })
```

## 🎨 样式调整

### 简化样式
```css
/* 移除复杂的form-tip样式 */
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
```

## 📁 文件变更

### 修改的文件
- `frontend/src/views/CharactersView.vue`
  - 简化服务器选择器
  - 优化专精选择
  - 调整默认等级
  - 移除暴雪API相关代码

### 保留的文件（暂不使用）
- `backend/app/api/realms.py` - 服务器API（保留备用）
- `backend/app/services/blizzard_api.py` - 暴雪API服务（保留备用）
- `frontend/src/stores/realm.ts` - 服务器状态管理（保留备用）

## 🚀 优势

### 简化后优势
1. **无需API配置** - 不需要暴雪API凭证
2. **更快的响应** - 无需网络请求
3. **更稳定的体验** - 不依赖外部服务
4. **更符合需求** - 专门针对时光服定制

### 保留的灵活性
- 如果将来需要更多服务器，只需在选项中添加
- 如果暴雪API可用，可以随时恢复集成
- 代码结构保持清晰，便于维护

## 🎯 用户体验

### 创建角色流程
1. 输入角色名称
2. 选择服务器（时光1-4）
3. 选择职业
4. 选择专精（下拉选择）
5. 确认等级（默认80）
6. 选择阵营
7. 提交创建

### 界面优化
- 服务器选择更直观
- 专精选择更准确
- 等级设置更合理
- 整体体验更流畅

## 📝 注意事项

### 扩展服务器列表
如需添加更多服务器，只需在服务器选择器中添加选项：
```vue
<el-option label="时光5" value="时光5" />
<el-option label="时光6" value="时光6" />
```

### 专精选项管理
如需调整专精选项，可以：
1. 按职业分组显示专精
2. 根据选择职业动态显示对应专精
3. 添加自定义专精选项

## 🔧 未来扩展

### 可能的改进
- [ ] 根据职业动态显示对应专精
- [ ] 添加服务器描述信息
- [ ] 支持自定义服务器名称
- [ ] 添加角色模板功能

---

**版本**: v1.2.0 - 时光服简化版
**更新时间**: 2026-05-06
**主要变更**: 简化服务器选择，优化专精和等级设置