<template>
  <div class="bosses-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><UserFilled /></el-icon>
        Boss列表
      </h2>
    </div>

    <el-card class="bosses-card">
      <el-table :data="bosses" stripe v-loading="loading">
        <el-table-column label="图标" width="80">
          <template #default="{ row }">
            <div class="boss-icon">
              <img v-if="row.icon_url && !erroredIcons['boss-' + String(row.boss_id)]" :src="row.icon_url" :alt="row.name" class="boss-icon-img" @error="handleIconError('boss-' + String(row.boss_id))" />
              <span v-else class="boss-icon-placeholder">👹</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="Boss名称" width="200" />
        <el-table-column prop="dungeon_name" label="所属副本" width="200" />
        <el-table-column prop="category" label="分类" width="150" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="viewLoot(row)">查看掉落</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UserFilled } from '@element-plus/icons-vue'
import type { Boss } from '@/types'
import { bossApi } from '@/api'

const route = useRoute()
const router = useRouter()

// 状态
const bosses = ref<Boss[]>([])
const loading = ref(false)
const erroredIcons = reactive<Record<string, boolean>>({})

function handleIconError(key: string) {
  erroredIcons[key] = true
}

// 查看掉落
function viewLoot(boss: Boss) {
  router.push(`/bosses/${boss.boss_id}/loot`)
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
