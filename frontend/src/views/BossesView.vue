<template>
  <div class="bosses-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><UserFilled /></el-icon>
        Boss管理
      </h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          添加Boss
        </el-button>
      </div>
    </div>

    <el-card class="bosses-card">
      <el-table :data="bosses" stripe v-loading="loading">
        <el-table-column label="图标" width="80">
          <template #default="{ row }">
            <div class="boss-icon">
              <img v-if="row.icon_url" :src="row.icon_url" :alt="row.name" class="boss-icon-img" />
              <span v-else class="boss-icon-placeholder">👹</span>
            </div>
          </template>
        </el-table-column>
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
        <el-form-item label="图标URL">
          <el-input v-model="form.icon_url" placeholder="请输入图标URL（可选）" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">
          {{ isEditing ? '更新' : '添加' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { UserFilled, Plus } from '@element-plus/icons-vue'
import type { Boss } from '@/types'
import { bossApi } from '@/api'

const route = useRoute()

// 状态
const bosses = ref<Boss[]>([])
const loading = ref(false)
const submitting = ref(false)

// 对话框状态
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
  description: '',
  icon_url: ''
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
    description: '',
    icon_url: ''
  })
  isEditing.value = false
  editingBossId.value = null
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    submitting.value = true
    try {
      if (isEditing.value && editingBossId.value) {
        await bossApi.create(form)
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
    } finally {
      submitting.value = false
    }
  })
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
    description: boss.description || '',
    icon_url: boss.icon_url || ''
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
    const dungeonId = Number(route.params.id) || 0
    const params: Record<string, number> = {}
    if (dungeonId > 0) {
      params.dungeon_id = dungeonId
    }
    const data = await bossApi.getAll(params)
    bosses.value = data
  } catch (error) {
    console.error('Error loading bosses:', error)
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
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.bosses-card {
  margin-top: 20px;
}

.boss-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.boss-icon-img {
  width: 48px;
  height: 48px;
  border-radius: 50%;
}

.boss-icon-placeholder {
  font-size: 32px;
}
</style>
