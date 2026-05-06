<template>
  <div class="character-detail-view">
    <div class="page-header">
      <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
      <h2 class="page-title">{{ character?.name }} - 角色详情</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showAddNeedDialog = true">
          <el-icon><Plus /></el-icon>
          添加装备需求
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="character" class="character-content">
      <!-- 角色基本信息 -->
      <el-card class="character-info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="character.faction === 'alliance' ? 'primary' : 'danger'">
              {{ character.faction === 'alliance' ? '联盟' : '部落' }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="角色名">{{ character.name }}</el-descriptions-item>
          <el-descriptions-item label="服务器">{{ character.realm }}</el-descriptions-item>
          <el-descriptions-item label="等级">{{ character.level }}</el-descriptions-item>
          <el-descriptions-item label="职业">
            <el-tag :type="getClassTagType(character.wow_class)">
              {{ getClassDisplayName(character.wow_class) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="专精">{{ character.spec || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(character.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 装备进度 -->
      <el-card class="progress-card">
        <template #header>
          <div class="card-header">
            <span>装备获取进度</span>
            <el-tag v-if="progress" type="success">
              {{ progress.progress_percentage }}%
            </el-tag>
          </div>
        </template>
        <div v-if="progress" class="progress-content">
          <el-progress
            :percentage="progress.progress_percentage"
            :stroke-width="20"
            :text-inside="true"
            status="success"
          />
          <div class="progress-stats">
            <el-statistic title="总需求" :value="progress.total_needs" />
            <el-statistic title="已获取" :value="progress.obtained" />
            <el-statistic title="剩余" :value="progress.remaining" />
          </div>
        </div>
        <el-empty v-else description="暂无装备需求数据" />
      </el-card>

      <!-- 装备需求列表 -->
      <el-card class="item-needs-card">
        <template #header>
          <div class="card-header">
            <span>装备需求列表</span>
            <div class="header-filters">
              <el-radio-group v-model="filterStatus" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="pending">未获取</el-radio-button>
                <el-radio-button label="obtained">已获取</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>

        <div v-if="filteredNeeds.length === 0" class="empty-container">
          <el-empty description="暂无装备需求">
            <el-button type="primary" @click="showAddNeedDialog = true">添加装备需求</el-button>
          </el-empty>
        </div>

        <el-table v-else :data="filteredNeeds" stripe style="width: 100%">
          <el-table-column prop="item_name" label="装备名称" width="200" />
          <el-table-column prop="item_id" label="装备ID" width="100" />
          <el-table-column prop="dungeon_name" label="副本" width="150" />
          <el-table-column prop="boss_name" label="Boss" width="150" />
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-rate v-model="row.priority" disabled show-score />
            </template>
          </el-table-column>
          <el-table-column prop="obtained" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.obtained ? 'success' : 'warning'">
                {{ row.obtained ? '已获取' : '未获取' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="!row.obtained"
                size="small"
                type="success"
                @click="markAsObtained(row.id)"
              >
                标记获取
              </el-button>
              <el-button size="small" @click="editNeed(row)">编辑</el-button>
              <el-button size="small" type="danger" @click="deleteNeed(row.id)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 添加/编辑装备需求对话框 -->
    <el-dialog
      v-model="showAddNeedDialog"
      :title="isEditingNeed ? '编辑装备需求' : '添加装备需求'"
      width="600px"
      @close="resetNeedForm"
    >
      <el-form :model="needForm" :rules="needRules" ref="needFormRef" label-width="100px">
        <el-form-item label="装备ID" prop="item_id">
          <el-input-number v-model="needForm.item_id" :min="1" placeholder="请输入装备ID" />
          <div class="form-tip">提示：可以在魔兽世界数据库网站查找装备ID</div>
        </el-form-item>
        <el-form-item label="装备名称" prop="item_name">
          <el-input v-model="needForm.item_name" placeholder="请输入装备名称" />
        </el-form-item>
        <el-form-item label="副本名称" prop="dungeon_name">
          <el-input v-model="needForm.dungeon_name" placeholder="请输入副本名称（可选）" />
        </el-form-item>
        <el-form-item label="Boss名称" prop="boss_name">
          <el-input v-model="needForm.boss_name" placeholder="请输入Boss名称（可选）" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-rate v-model="needForm.priority" :max="5" show-text />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="needForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddNeedDialog = false">取消</el-button>
        <el-button type="primary" @click="submitNeedForm" :loading="itemNeedStore.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCharacterStore } from '@/stores/character'
import { useItemNeedStore } from '@/stores/itemNeed'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import type { ItemNeed, ItemNeedCreate, ItemProgress } from '@/types'
import { WoWClass } from '@/types'

const route = useRoute()
const router = useRouter()
const characterStore = useCharacterStore()
const itemNeedStore = useItemNeedStore()

// 状态
const loading = ref(true)
const character = ref<any>(null)
const progress = ref<ItemProgress | null>(null)
const itemNeeds = ref<ItemNeed[]>([])

// 过滤器
const filterStatus = ref<'all' | 'pending' | 'obtained'>('all')

// 对话框状态
const showAddNeedDialog = ref(false)
const isEditingNeed = ref(false)
const editingNeedId = ref<string | null>(null)

// 装备需求表单
const needForm = reactive<ItemNeedCreate>({
  character_id: '',
  item_id: 0,
  item_name: '',
  boss_id: undefined,
  boss_name: '',
  dungeon_name: '',
  priority: 1,
  obtained: false,
  notes: ''
})

const needFormRef = ref()

// 表单验证规则
const needRules = {
  item_id: [{ required: true, message: '请输入装备ID', trigger: 'blur' }],
  item_name: [{ required: true, message: '请输入装备名称', trigger: 'blur' }]
}

// 过滤后的装备需求
const filteredNeeds = computed(() => {
  if (filterStatus.value === 'all') {
    return itemNeeds.value
  } else if (filterStatus.value === 'pending') {
    return itemNeeds.value.filter(item => !item.obtained)
  } else {
    return itemNeeds.value.filter(item => item.obtained)
  }
})

// 获取职业显示名称
function getClassDisplayName(classKey: string): string {
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
  return classNames[classKey] || classKey
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

// 格式化日期
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 返回上一页
function goBack() {
  router.back()
}

// 重置装备需求表单
function resetNeedForm() {
  needFormRef.value?.resetFields()
  Object.assign(needForm, {
    character_id: '',
    item_id: 0,
    item_name: '',
    boss_id: undefined,
    boss_name: '',
    dungeon_name: '',
    priority: 1,
    obtained: false,
    notes: ''
  })
  isEditingNeed.value = false
  editingNeedId.value = null
}

// 提交装备需求表单
async function submitNeedForm() {
  if (!needFormRef.value) return

  await needFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      if (isEditingNeed.value && editingNeedId.value) {
        await itemNeedStore.updateItemNeed(editingNeedId.value, needForm)
        ElMessage.success('装备需求更新成功')
      } else {
        await itemNeedStore.createItemNeed(needForm)
        ElMessage.success('装备需求添加成功')
      }
      showAddNeedDialog.value = false
      resetNeedForm()
      await loadItemNeeds()
      await loadProgress()
    } catch (error) {
      ElMessage.error(isEditingNeed.value ? '装备需求更新失败' : '装备需求添加失败')
    }
  })
}

// 编辑装备需求
function editNeed(need: ItemNeed) {
  isEditingNeed.value = true
  editingNeedId.value = need.id
  Object.assign(needForm, {
    character_id: need.character_id,
    item_id: need.item_id,
    item_name: need.item_name,
    boss_id: need.boss_id,
    boss_name: need.boss_name || '',
    dungeon_name: need.dungeon_name || '',
    priority: need.priority,
    obtained: need.obtained,
    notes: need.notes || ''
  })
  showAddNeedDialog.value = true
}

// 标记装备为已获取
async function markAsObtained(id: string) {
  try {
    await itemNeedStore.markAsObtained(id)
    ElMessage.success('已标记为获取')
    await loadItemNeeds()
    await loadProgress()
  } catch (error) {
    ElMessage.error('标记失败')
  }
}

// 删除装备需求
async function deleteNeed(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个装备需求吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await itemNeedStore.deleteItemNeed(id)
    ElMessage.success('删除成功')
    await loadItemNeeds()
    await loadProgress()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 加载角色信息
async function loadCharacter() {
  const characterId = route.params.id as string
  try {
    character.value = await characterStore.fetchCharacter(characterId)
    needForm.character_id = characterId
  } catch (error) {
    ElMessage.error('加载角色信息失败')
    router.push('/characters')
  }
}

// 加载装备需求
async function loadItemNeeds() {
  const characterId = route.params.id as string
  await itemNeedStore.fetchItemNeeds({ character_id: characterId })
  itemNeeds.value = itemNeedStore.filterByCharacter(characterId)
}

// 加载进度
async function loadProgress() {
  const characterId = route.params.id as string
  try {
    progress.value = await itemNeedStore.fetchProgress(characterId)
  } catch (error) {
    console.error('加载进度失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  loading.value = true
  try {
    await loadCharacter()
    await loadItemNeeds()
    await loadProgress()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.character-detail-view {
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
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  flex: 1;
  text-align: center;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-container {
  padding: 20px;
}

.character-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.header-filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

.progress-content {
  padding: 20px 0;
}

.progress-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.empty-container {
  padding: 40px 20px;
  text-align: center;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>