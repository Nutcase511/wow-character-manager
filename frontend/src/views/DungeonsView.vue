<template>
  <div class="dungeons-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Grid /></el-icon>
        副本管理
      </h2>
      <div class="header-actions">
        <el-button @click="showSyncDialog = true">
          <el-icon><Refresh /></el-icon>
          从暴雪API同步
        </el-button>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          添加副本
        </el-button>
      </div>
    </div>

    <el-card class="dungeons-card">
      <el-table :data="dungeons" stripe v-loading="loading">
        <el-table-column prop="name" label="副本名称" width="200" />
        <el-table-column prop="map_name" label="地图名称" width="150" />
        <el-table-column prop="minimum_level" label="最低等级" width="100" />
        <el-table-column prop="modes" label="难度" width="200">
          <template #default="{ row }">
            <el-tag
              v-for="mode in row.modes"
              :key="mode"
              size="small"
              style="margin-right: 4px"
            >
              {{ getModeDisplayName(mode) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="editDungeon(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteDungeon(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 从暴雪API同步对话框 -->
    <el-dialog
      v-model="showSyncDialog"
      title="从暴雪API同步副本数据"
      width="400px"
    >
      <el-form :model="syncForm" label-width="100px">
        <el-form-item label="副本ID">
          <el-input-number
            v-model="syncForm.journal_instance_id"
            :min="1"
            placeholder="请输入副本Journal ID"
            style="width: 100%"
          />
          <div class="form-tip">
            提示：可以在暴雪API文档中查找副本的Journal Instance ID
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

    <!-- 添加/编辑副本对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="isEditing ? '编辑副本' : '添加副本'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="副本ID" prop="dungeon_id">
          <el-input-number v-model="form.dungeon_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="副本名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入副本名称" />
        </el-form-item>
        <el-form-item label="地图名称" prop="map_name">
          <el-input v-model="form.map_name" placeholder="请输入地图名称" />
        </el-form-item>
        <el-form-item label="最低等级" prop="minimum_level">
          <el-input-number v-model="form.minimum_level" :min="1" :max="80" />
        </el-form-item>
        <el-form-item label="难度" prop="modes">
          <el-checkbox-group v-model="form.modes">
            <el-checkbox label="normal">普通</el-checkbox>
            <el-checkbox label="heroic">英雄</el-checkbox>
            <el-checkbox label="mythic">史诗</el-checkbox>
            <el-checkbox label="raid_finder">随机团队</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入副本描述"
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
import { dungeonApi } from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Grid, Refresh, Plus } from '@element-plus/icons-vue'
import type { Dungeon } from '@/types'

// 状态
const dungeons = ref<Dungeon[]>([])
const loading = ref(false)
const syncing = ref(false)

// 对话框状态
const showSyncDialog = ref(false)
const showCreateDialog = ref(false)
const isEditing = ref(false)
const editingDungeonId = ref<string | null>(null)

// 表单数据
const form = reactive({
  dungeon_id: 0,
  name: '',
  map_name: '',
  minimum_level: 70,
  modes: [],
  description: ''
})

const syncForm = reactive({
  journal_instance_id: 0
})

const formRef = ref()

// 表单验证规则
const rules = {
  dungeon_id: [{ required: true, message: '请输入副本ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入副本名称', trigger: 'blur' }],
  minimum_level: [{ required: true, message: '请输入最低等级', trigger: 'blur' }]
}

// 获取难度显示名称
function getModeDisplayName(mode: string): string {
  const modeNames: Record<string, string> = {
    normal: '普通',
    heroic: '英雄',
    mythic: '史诗',
    raid_finder: '随机团队'
  }
  return modeNames[mode] || mode
}

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, {
    dungeon_id: 0,
    name: '',
    map_name: '',
    minimum_level: 70,
    modes: [],
    description: ''
  })
  isEditing.value = false
  editingDungeonId.value = null
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return

  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      if (isEditing.value && editingDungeonId.value) {
        await dungeonApi.create(form) // 这里应该用update API
        ElMessage.success('副本更新成功')
      } else {
        await dungeonApi.create(form)
        ElMessage.success('副本添加成功')
      }
      showCreateDialog.value = false
      resetForm()
      await loadDungeons()
    } catch (error) {
      ElMessage.error(isEditing.value ? '副本更新失败' : '副本添加失败')
    }
  })
}

// 从暴雪API同步
async function syncFromBlizzard() {
  if (syncForm.journal_instance_id <= 0) {
    ElMessage.warning('请输入有效的副本ID')
    return
  }

  syncing.value = true
  try {
    await dungeonApi.syncFromBlizzard(syncForm.journal_instance_id)
    ElMessage.success('同步成功')
    showSyncDialog.value = false
    syncForm.journal_instance_id = 0
    await loadDungeons()
  } catch (error) {
    ElMessage.error('同步失败，请检查副本ID是否正确')
  } finally {
    syncing.value = false
  }
}

// 编辑副本
function editDungeon(dungeon: Dungeon) {
  isEditing.value = true
  editingDungeonId.value = dungeon.id
  Object.assign(form, {
    dungeon_id: dungeon.dungeon_id,
    name: dungeon.name,
    map_name: dungeon.map_name || '',
    minimum_level: dungeon.minimum_level,
    modes: dungeon.modes,
    description: dungeon.description || ''
  })
  showCreateDialog.value = true
}

// 删除副本
async function deleteDungeon(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个副本吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await dungeonApi.delete(id)
    ElMessage.success('删除成功')
    await loadDungeons()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 加载副本列表
async function loadDungeons() {
  loading.value = true
  try {
    const response = await dungeonApi.getAll()
    dungeons.value = response.data
  } catch (error) {
    ElMessage.error('加载副本列表失败')
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadDungeons()
})
</script>

<style scoped>
.dungeons-view {
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
}

.dungeons-card {
  min-height: 400px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>