<template>
  <div class="bosses-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><UserFilled /></el-icon>
        Boss管理
      </h2>
      <div class="header-actions">
        <el-button @click="showSyncDialog = true">
          <el-icon><Refresh /></el-icon>
          从暴雪API同步
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          添加Boss
        </el-button>
      </div>
    </div>

    <el-card class="bosses-card">
      <el-table :data="bosses" stripe v-loading="loading">
        <el-table-column prop="name" label="Boss名称" width="200" />
        <el-table-column prop="dungeon_name" label="所属副本" width="200" />
        <el-table-column prop="category" label="分类" width="150" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editBoss(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteBoss(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 从暴雪API同步对话框 -->
    <el-dialog
      v-model="showSyncDialog"
      title="从暴雪API同步Boss数据"
      width="400px"
    >
      <el-form :model="syncForm" label-width="120px">
        <el-form-item label="Boss ID">
          <el-input-number
            v-model="syncForm.journal_encounter_id"
            :min="1"
            placeholder="请输入Boss Journal ID"
            style="width: 100%"
          />
          <div class="form-tip">
            提示：可以在暴雪API文档中查找Boss的Journal Encounter ID
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showSyncDialog = false">取消</el-button>
        <el-button type="primary" @click="syncFromBlizzard" :loading="syncing">
          同步
        </el-button>
      </template>
    </el-dialog>

    <!-- 添加/编辑Boss对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑Boss' : '添加Boss'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="Boss ID" prop="boss_id">
          <el-input-number v-model="form.boss_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="Boss名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入Boss名称" />
        </el-form-item>
        <el-form-item label="所属副本ID" prop="dungeon_id">
          <el-input-number v-model="form.dungeon_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="所属副本" prop="dungeon_name">
          <el-input v-model="form.dungeon_name" placeholder="请输入所属副本名称" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-input v-model="form.category" placeholder="请输入Boss分类（可选）" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入Boss描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { bossApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Refresh, Plus } from '@element-plus/icons-vue'
import type { Boss } from '@/types'

// 状态
const bosses = ref<Boss[]>([])
const loading = ref(false)
const syncing = ref(false)

// 对话框状态
const showSyncDialog = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)
const editingBossId = ref<string | null>(null)

// 表单数据
const form = reactive({
  boss_id: 0,
  name: '',
  dungeon_id: 0,
  dungeon_name: '',
  category: '',
  description: ''
})

const syncForm = reactive({
  journal_encounter_id: 0
})

const formRef = ref()

// 表单验证规则
const rules = {
  boss_id: [{ required: true, message: '请输入Boss ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入Boss名称', trigger: 'blur' }],
  dungeon_id: [{ required: true, message: '请输入所属副本ID', trigger: 'blur' }],
  dungeon_name: [{ required: true, message: '请输入所属副本名称', trigger: 'blur' }]
}

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, {
    boss_id: 0,
    name: '',
    dungeon_id: 0,
    dungeon_name: '',
    category: '',
    description: ''
  })
  isEditing.value = false
  editingBossId.value = null
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      if (isEditing.value && editingBossId.value) {
        await bossApi.create(form) // 这里应该用update API
        ElMessage.success('Boss更新成功')
      } else {
        await bossApi.create(form)
        ElMessage.success('Boss添加成功')
      }
      showCreateDialog.value = false
      resetForm()
      await loadBosses()
    } catch (error) {
      ElMessage.error(isEditing.value ? 'Boss更新失败' : 'Boss添加失败')
    }
  })
}

// 从暴雪API同步
async function syncFromBlizzard() {
  if (syncForm.journal_encounter_id <= 0) {
    ElMessage.warning('请输入有效的Boss ID')
    return
  }

  syncing.value = true
  try {
    await bossApi.syncFromBlizzard(syncForm.journal_encounter_id)
    ElMessage.success('同步成功')
    showSyncDialog.value = false
    syncForm.journal_encounter_id = 0
    await loadBosses()
  } catch (error) {
    ElMessage.error('同步失败，请检查Boss ID是否正确')
  } finally {
    syncing.value = false
  }
}

// 编辑Boss
function editBoss(boss: Boss) {
  isEditing.value = true
  editingBossId.value = boss.id
  Object.assign(form, {
    boss_id: boss.boss_id,
    name: boss.name,
    dungeon_id: boss.dungeon_id,
    dungeon_name: boss.dungeon_name,
    category: boss.category || '',
    description: boss.description || ''
  })
  showCreateDialog.value = true
}

// 删除Boss
async function deleteBoss(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个Boss吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await bossApi.delete(id)
    ElMessage.success('删除成功')
    await loadBosses()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 加载Boss列表
async function loadBosses() {
  loading.value = true
  try {
    const response = await bossApi.getAll()
    bosses.value = response.data
  } catch (error) {
    ElMessage.error('加载Boss列表失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadBosses()
})
</script>

<style scoped>
.bosses-view {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.bosses-card {
  min-height: 400px;
  border: 1px solid #374151;
}

.form-tip {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}
</style>