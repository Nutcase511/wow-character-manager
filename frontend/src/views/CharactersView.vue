<template>
  <div class="characters-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><User /></el-icon>
        角色管理
      </h2>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加角色
      </el-button>
      <el-button @click="handleRefreshLevels" :loading="refreshing">
        <el-icon><Refresh /></el-icon>
        刷新等级
      </el-button>
      <el-button type="success" @click="handleRefreshAllData" :loading="refreshingAll">
        <el-icon><RefreshRight /></el-icon>
        刷新全部数据
      </el-button>
    </div>

    <el-card class="characters-card">
      <div v-if="characterStore.loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>

      <div v-else-if="!characterStore.hasCharacters" class="empty-container">
        <el-empty description="暂无角色，请添加您的第一个角色">
          <el-button type="primary" @click="showCreateDialog = true">添加角色</el-button>
        </el-empty>
      </div>

      <div v-else class="characters-grid">
        <div
          v-for="character in sortedCharacters"
          :key="character.id"
          class="character-card"
          :style="getClassCardStyle(character.wow_class)"
          @click="goToCharacterDetail(character.id)"
        >
          <div class="character-header">
            <div class="character-icon">
              <img :src="getClassIcon(character.wow_class)" :alt="getClassDisplayName(character.wow_class)" class="class-icon" />
            </div>
            <div class="character-info">
              <h3 class="character-name">{{ character.name }}</h3>
              <p class="character-realm">{{ character.realm }}</p>
            </div>
            <div class="character-level" :style="{ color: getClassAccentColor(character.wow_class) }">{{ character.level }}级</div>
          </div>

          <div class="character-details">
            <el-tag
              :color="getClassAccentColor(character.wow_class)"
              :style="{ color: getClassTagTextColor(character.wow_class), borderColor: 'transparent' }"
              size="small"
            >
              {{ getClassDisplayName(character.wow_class) }}
            </el-tag>
            <el-tag v-if="character.spec" type="info" size="small">
              {{ SpecNameMap[character.spec] || character.spec }}
            </el-tag>
            <el-tag :type="character.faction === 'alliance' ? 'primary' : 'danger'" size="small">
              <img :src="getFactionIcon(character.faction)" :alt="character.faction" class="faction-icon" />
              {{ character.faction === 'alliance' ? '联盟' : '部落' }}
            </el-tag>
          </div>

          <div class="character-actions">
            <el-button size="small" type="danger" @click.stop="deleteCharacter(character.id)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 添加角色对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="添加角色"
      width="400px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="角色名" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="服务器" prop="realm">
          <el-select v-model="form.realm" placeholder="请选择服务器" style="width: 100%">
            <el-option label="时光1" value="时光1" />
            <el-option label="时光2" value="时光2" />
            <el-option label="时光3" value="时光3" />
            <el-option label="时光4" value="时光4" />
          </el-select>
        </el-form-item>
        <div class="form-tip-block">
          <el-icon><InfoFilled /></el-icon>
          <span>职业、等级、阵营等信息将在刷新数据时从插件自动同步</span>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="characterStore.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCharacterStore } from '@/stores/character'
import { ElMessage, ElMessageBox } from 'element-plus'
import { User, Plus, Delete, Refresh, RefreshRight, InfoFilled } from '@element-plus/icons-vue'
import { characterApi, goldApi } from '@/api'
import { WoWClass, ClassSpecsMap, SpecNameMap } from '@/types'
import { getClassIcon, getFactionIcon } from '@/utils/classIcons'

const router = useRouter()
const characterStore = useCharacterStore()

// 对话框状态
const showCreateDialog = ref(false)

// 表单数据（仅需名称和服务器，其他从插件同步）
const form = reactive({
  name: '',
  realm: '',
  wow_class: 'warrior',  // 默认值，刷新时会覆盖
  spec: '',
  level: 80,
  faction: 'horde'
})

const formRef = ref()

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  realm: [{ required: true, message: '请选择服务器', trigger: 'blur' }]
}

// 职业名称映射
const classNames: Record<string, string> = {
  [WoWClass.WARRIOR]: '战士',
  [WoWClass.PALADIN]: '圣骑士',
  [WoWClass.HUNTER]: '猎人',
  [WoWClass.ROGUE]: '潜行者',
  [WoWClass.PRIEST]: '牧师',
  [WoWClass.DEATH_KNIGHT]: '死亡骑士',
  [WoWClass.SHAMAN]: '萨满祭司',
  [WoWClass.MAGE]: '法师',
  [WoWClass.WARLOCK]: '术士',
  [WoWClass.MONK]: '武僧',
  [WoWClass.DRUID]: '德鲁伊',
  [WoWClass.DEMON_HUNTER]: '恶魔猎手',
  [WoWClass.EVOKER]: '唤魔师'
}

// 获取职业显示名称
function getClassDisplayName(classKey: string): string {
  return classNames[classKey] || classKey
}

// 职业配色映射（WoW 经典职业代表色）
const classColorMap: Record<string, { gradient: string; accent: string; border: string }> = {
  [WoWClass.WARRIOR]:       { gradient: 'linear-gradient(135deg, #7d5a2a 0%, #4a3420 40%, #2a1f14 100%)', accent: '#c79c6e', border: '#7d5a2a' },
  [WoWClass.PALADIN]:       { gradient: 'linear-gradient(135deg, #a0804a 0%, #6b5230 40%, #3d2e1a 100%)', accent: '#f58cba', border: '#a0804a' },
  [WoWClass.HUNTER]:        { gradient: 'linear-gradient(135deg, #3a5a2a 0%, #264020 40%, #1a2d14 100%)', accent: '#abd473', border: '#3a5a2a' },
  [WoWClass.ROGUE]:         { gradient: 'linear-gradient(135deg, #5a3a5a 0%, #3d2540 40%, #2a1a2d 100%)', accent: '#fff569', border: '#5a3a5a' },
  [WoWClass.PRIEST]:        { gradient: 'linear-gradient(135deg, #4a4a6e 0%, #32324e 40%, #22223a 100%)', accent: '#ffffff', border: '#4a4a6e' },
  [WoWClass.DEATH_KNIGHT]:  { gradient: 'linear-gradient(135deg, #4a2030 0%, #321524 40%, #240d1a 100%)', accent: '#c41e3a', border: '#4a2030' },
  [WoWClass.SHAMAN]:        { gradient: 'linear-gradient(135deg, #1a4a5a 0%, #143a45 40%, #0d2830 100%)', accent: '#0070de', border: '#1a4a5a' },
  [WoWClass.MAGE]:          { gradient: 'linear-gradient(135deg, #2a3a6e 0%, #1e2a50 40%, #141c38 100%)', accent: '#69ccf0', border: '#2a3a6e' },
  [WoWClass.WARLOCK]:       { gradient: 'linear-gradient(135deg, #3a2a5a 0%, #2d1e48 40%, #201434 100%)', accent: '#9482c9', border: '#3a2a5a' },
  [WoWClass.MONK]:          { gradient: 'linear-gradient(135deg, #2a5a4a 0%, #1e4438 40%, #142e28 100%)', accent: '#00ff96', border: '#2a5a4a' },
  [WoWClass.DRUID]:         { gradient: 'linear-gradient(135deg, #3a5a30 0%, #2a4422 40%, #1c2e18 100%)', accent: '#ff7d0a', border: '#3a5a30' },
  [WoWClass.DEMON_HUNTER]:  { gradient: 'linear-gradient(135deg, #5a2a1a 0%, #44200f 40%, #30140a 100%)', accent: '#a330c9', border: '#5a2a1a' },
  [WoWClass.EVOKER]:        { gradient: 'linear-gradient(135deg, #2a4a4a 0%, #1e3838 40%, #142828 100%)', accent: '#33937f', border: '#2a4a4a' }
}

// 获取职业卡片样式
function getClassCardStyle(classKey: string) {
  const colors = classColorMap[classKey]
  if (!colors) return {}
  return {
    background: colors.gradient,
    borderColor: colors.border
  }
}

// 获取职业强调色（用于等级数字、职业标签等）
function getClassAccentColor(classKey: string): string {
  return classColorMap[classKey]?.accent || '#f39c12'
}

// 获取职业标签文字颜色（浅色背景用深色字）
function getClassTagTextColor(classKey: string): string {
  const lightAccentClasses = [WoWClass.PRIEST]
  if (lightAccentClasses.includes(classKey as WoWClass)) {
    return '#2a3f6e'
  }
  return '#fff'
}

// 获取职业标签类型
function getClassTagType(classKey: string): string {
  const typeMap: Record<string, string> = {
    [WoWClass.WARRIOR]: 'warning',
    [WoWClass.PALADIN]: 'success',
    [WoWClass.HUNTER]: 'success',
    [WoWClass.ROGUE]: 'warning',
    [WoWClass.PRIEST]: '',
    [WoWClass.DEATH_KNIGHT]: 'danger',
    [WoWClass.SHAMAN]: 'primary',
    [WoWClass.MAGE]: 'primary',
    [WoWClass.WARLOCK]: 'danger',
    [WoWClass.MONK]: 'warning',
    [WoWClass.DRUID]: 'success',
    [WoWClass.DEMON_HUNTER]: 'danger',
    [WoWClass.EVOKER]: 'primary'
  }
  return typeMap[classKey] || ''
}

// 按等级排序的角色列表（等级从高到低）
const sortedCharacters = computed(() => {
  return [...characterStore.characters].sort((a, b) => b.level - a.level)
})

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, {
    name: '',
    realm: '',
    wow_class: 'warrior',
    spec: '',
    level: 80,
    faction: 'horde'
  })
}

// 提交表单（仅创建）
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      await characterStore.createCharacter(form)
      ElMessage.success('角色创建成功，请刷新数据以同步详细信息')
      showCreateDialog.value = false
      resetForm()
    } catch (error) {
      ElMessage.error('角色创建失败')
    }
  })
}

// 删除角色
async function deleteCharacter(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个角色吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await characterStore.deleteCharacter(id)
    ElMessage.success('角色删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('角色删除失败')
    }
  }
}

const refreshing = ref(false)
const refreshingAll = ref(false)

async function handleRefreshLevels() {
  refreshing.value = true
  try {
    const res = await characterApi.refreshLevels()
    ElMessage.success(res.data.message || '刷新成功')
    await characterStore.fetchCharacters()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '刷新失败')
  } finally {
    refreshing.value = false
  }
}

async function handleRefreshAllData() {
  refreshingAll.value = true
  try {
    const res = await characterApi.refreshAllData()
    const data = res.data
    
    if (data.success) {
      ElMessage.success(data.message || '刷新成功')
      await characterStore.fetchCharacters()
      
      // 显示详细结果
      if (data.results && data.results.length > 0) {
        const successCount = data.results.filter((r: any) => r.success).length
        const failedCount = data.results.length - successCount
        
        if (failedCount > 0) {
          ElMessage.warning(`${successCount} 个角色刷新成功，${failedCount} 个失败`)
        }
      }
    } else {
      ElMessage.error(data.message || '刷新失败')
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '刷新全部数据失败')
  } finally {
    refreshingAll.value = false
  }
}

// 跳转到角色详情
function goToCharacterDetail(id: string) {
  router.push(`/characters/${id}`)
}

// 生命周期
onMounted(() => {
  characterStore.fetchCharacters()
})
</script>

<style scoped>
.characters-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #e5e7eb;
}

.characters-card {
  min-height: 400px;
  border: 1px solid #374151;
}

.loading-container {
  padding: 20px;
}

.empty-container {
  padding: 40px 20px;
}

.characters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 10px;
}

.character-card {
  border-radius: 12px;
  padding: 20px;
  color: #e5e7eb;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.3s;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.15);
}

.character-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
  border-color: rgba(255, 255, 255, 0.3);
}

.character-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 12px;
}

.character-icon {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.2);
}

.class-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.character-info {
  flex: 1;
}

.character-name {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
  color: #e5e7eb;
}

.character-realm {
  font-size: 14px;
  opacity: 0.7;
  margin: 0;
  color: #9ca3af;
}

.character-level {
  font-size: 24px;
  font-weight: 700;
}

.character-details {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.character-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 12px;
}

.character-actions .el-button {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #e5e7eb;
}

.character-actions .el-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.character-actions .el-button--danger {
  background: rgba(231, 76, 60, 0.6);
}

.character-actions .el-button--danger:hover {
  background: rgba(231, 76, 60, 0.9);
}

.form-tip {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.form-tip-block {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 12px;
  color: #6b7280;
  padding: 10px;
  background: #1f2937;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
  margin-top: 8px;
}

.faction-icon {
  width: 14px;
  height: 14px;
  margin-right: 4px;
  vertical-align: middle;
}
</style>