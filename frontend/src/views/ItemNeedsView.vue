<template>
  <div class="item-needs-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Goods /></el-icon>
        装备需求管理
      </h2>
      <div class="header-actions">
        <el-select
          v-model="selectedCharacterId"
          placeholder="选择角色"
          style="width: 200px; margin-right: 12px"
          @change="handleCharacterChange"
          clearable
        >
          <el-option
            v-for="char in characters"
            :key="char.id"
            :label="`${char.name} - ${char.realm}`"
            :value="char.id"
          />
        </el-select>
        <el-button type="primary" @click="showAddDialog = true" :disabled="!selectedCharacterId">
          <el-icon><Plus /></el-icon>
          添加装备需求
        </el-button>
      </div>
    </div>

    <el-card class="item-needs-card">
      <template #header>
        <div class="card-header">
          <span>装备需求列表</span>
          <div class="header-filters">
            <el-radio-group v-model="filterStatus" size="small" @change="applyFilters">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="pending">未获取</el-radio-button>
              <el-radio-button label="obtained">已获取</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <div v-if="!selectedCharacterId" class="empty-container">
        <el-empty description="请先选择一个角色">
          <el-select
            v-model="selectedCharacterId"
            placeholder="选择角色"
            style="width: 200px"
            @change="handleCharacterChange"
          >
            <el-option
              v-for="char in characters"
              :key="char.id"
              :label="`${char.name} - ${char.realm}`"
              :value="char.id"
            />
          </el-select>
        </el-empty>
      </div>

      <el-table
        v-else
        :data="filteredNeeds"
        stripe
        v-loading="loading"
        style="width: 100%"
      >
        <el-table-column prop="item_name" label="装备名称" width="200" />
        <el-table-column prop="item_id" label="装备ID" width="100" />
        <el-table-column prop="character_id" label="角色" width="150">
          <template #default="{ row }">
            {{ getCharacterName(row.character_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="dungeon_name" label="副本" width="150" />
        <el-table-column prop="boss_name" label="Boss" width="150" />
        <el-table-column prop="priority" label="优先级" width="150">
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
        <el-table-column label="操作" width="250" fixed="right">
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

    <!-- 添加/编辑装备需求对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEditing ? '编辑装备需求' : '添加装备需求'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="角色" prop="character_id">
          <el-select
            v-model="form.character_id"
            placeholder="请选择角色"
            style="width: 100%"
            :disabled="isEditing"
          >
            <el-option
              v-for="char in characters"
              :key="char.id"
              :label="`${char.name} - ${char.realm}`"
              :value="char.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="装备ID" prop="item_id">
          <el-input-number
            v-model="form.item_id"
            :min="1"
            placeholder="请输入装备ID"
            style="width: 100%"
          />
          <div class="form-tip">提示：可以在魔兽世界数据库网站查找装备ID</div>
        </el-form-item>
        <el-form-item label="装备名称" prop="item_name">
          <el-input v-model="form.item_name" placeholder="请输入装备名称" />
        </el-form-item>
        <el-form-item label="副本名称" prop="dungeon_name">
          <el-input v-model="form.dungeon_name" placeholder="请输入副本名称（可选）" />
        </el-form-item>
        <el-form-item label="Boss名称" prop="boss_name">
          <el-input v-model="form.boss_name" placeholder="请输入Boss名称（可选）" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-rate v-model="form.priority" :max="5" show-text />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useCharacterStore } from '@/stores/character'
import { useItemNeedStore } from '@/stores/itemNeed'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Goods, Plus } from '@element-plus/icons-vue'
import type { ItemNeed, ItemNeedCreate, Character } from '@/types'

const characterStore = useCharacterStore()
const itemNeedStore = useItemNeedStore()

// 状态
const loading = ref(false)
const characters = ref<Character[]>([])
const itemNeeds = ref<ItemNeed[]>([])

// 过滤器
const selectedCharacterId = ref<string>('')
const filterStatus = ref<'all' | 'pending' | 'obtained'>('all')

// 对话框状态
const showAddDialog = ref(false)
const isEditing = ref(false)
const editingNeedId = ref<string | null>(null)

// 表单数据
const form = reactive<ItemNeedCreate>({
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

const formRef = ref()

// 表单验证规则
const rules = {
  character_id: [{ required: true, message: '请选择角色', trigger: 'change' }],
  item_id: [{ required: true, message: '请输入装备ID', trigger: 'blur' }],
  item_name: [{ required: true, message: '请输入装备名称', trigger: 'blur' }]
}

// 过滤后的装备需求
const filteredNeeds = computed(() => {
  let result = itemNeeds.value

  // 按角色过滤
  if (selectedCharacterId.value) {
    result = result.filter(item => item.character_id === selectedCharacterId.value)
  }

  // 按状态过滤
  if (filterStatus.value === 'pending') {
    result = result.filter(item => !item.obtained)
  } else if (filterStatus.value === 'obtained') {
    result = result.filter(item => item.obtained)
  }

  return result
})

// 获取角色名称
function getCharacterName(characterId: string): string {
  const character = characters.value.find(c => c.id === characterId)
  return character ? `${character.name} - ${character.realm}` : characterId
}

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, {
    character_id: selectedCharacterId.value,
    item_id: 0,
    item_name: '',
    boss_id: undefined,
    boss_name: '',
    dungeon_name: '',
    priority: 1,
    obtained: false,
    notes: ''
  })
  isEditing.value = false
  editingNeedId.value = null
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      if (isEditing.value && editingNeedId.value) {
        await itemNeedStore.updateItemNeed(editingNeedId.value, form)
        ElMessage.success('装备需求更新成功')
      } else {
        await itemNeedStore.createItemNeed(form)
        ElMessage.success('装备需求添加成功')
      }
      showAddDialog.value = false
      resetForm()
      await loadData()
    } catch (error) {
      ElMessage.error(isEditing.value ? '装备需求更新失败' : '装备需求添加失败')
    }
  })
}

// 编辑装备需求
function editNeed(need: ItemNeed) {
  isEditing.value = true
  editingNeedId.value = need.id
  Object.assign(form, {
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
  showAddDialog.value = true
}

// 标记装备为已获取
async function markAsObtained(id: string) {
  try {
    await itemNeedStore.markAsObtained(id)
    ElMessage.success('已标记为获取')
    await loadData()
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
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 角色变化处理
function handleCharacterChange() {
  applyFilters()
}

// 应用过滤器
function applyFilters() {
  // filteredNeeds 会自动更新
}

// 加载数据
async function loadData() {
  loading.value = true
  try {
    // 加载角色列表
    await characterStore.fetchCharacters()
    characters.value = characterStore.characters

    // 加载装备需求
    await itemNeedStore.fetchItemNeeds()
    itemNeeds.value = itemNeedStore.itemNeeds
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.item-needs-view {
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
  color: #1a1a2e;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
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

.item-needs-card {
  min-height: 400px;
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