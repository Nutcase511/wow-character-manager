<template>
  <div class="gold-overview">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon>💰</el-icon>
        金币统计
      </h2>
      <div class="header-actions">
        <el-button @click="handleRefresh" :loading="syncing">
          <el-icon><Refresh /></el-icon>
          {{ syncing ? '同步中...' : '刷新' }}
        </el-button>
      </div>
    </div>

    <el-card class="total-card">
      <div class="total-info">
        <div class="total-item">
          <span class="total-label">总金币</span>
          <span class="total-value">{{ formatGold(totalGold) }}</span>
        </div>
        <div class="total-item">
          <span class="total-label">角色数</span>
          <span class="total-value">{{ allGold.length }}</span>
        </div>
      </div>
    </el-card>

    <el-card class="characters-card">
      <div class="card-header">
        <h3>角色金币</h3>
      </div>
      <el-table :data="goldWithClass" stripe v-loading="loading">
        <el-table-column label="角色" width="180">
          <template #default="{ row }">
            <div class="character-info">
              <img :src="getClassIcon(row.wow_class)" :alt="row.wow_class" class="mini-class-icon" />
              <div class="character-text">
                <span class="character-name">{{ row.character_name }}</span>
                <span class="character-realm">{{ row.realm }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="当前金币" width="200">
          <template #default="{ row }">
            <span class="gold-amount">{{ formatGold(row.current_gold) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" width="200">
          <template #default="{ row }">
            <span class="update-time">{{ formatDate(row.last_updated) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="viewCharacter(row.character_id)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-empty v-if="!loading && allGold.length === 0" description="暂无金币数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { goldApi, characterApi } from '@/api'
import type { CharacterGold } from '@/types'
import { getClassIcon } from '@/utils/classIcons'

const router = useRouter()

const loading = ref(false)
const syncing = ref(false)
const allGold = ref<CharacterGold[]>([])
const characters = ref<any[]>([])

const totalGold = computed(() => {
  return allGold.value.reduce((sum, g) => sum + g.current_gold, 0)
})

const goldWithClass = computed(() => {
  return allGold.value.map(gold => {
    const char = characters.value.find(c => c.id === gold.character_id)
    return {
      ...gold,
      wow_class: char?.wow_class || '未知'
    }
  })
})

async function loadCharacters() {
  try {
    const response = await characterApi.getAll()
    characters.value = response.data
  } catch {
    characters.value = []
  }
}

function formatGold(copper: number): string {
  if (!copper) return '0金 0银 0铜'
  const gold = Math.floor(copper / 10000)
  const silver = Math.floor((copper % 10000) / 100)
  const copperRemain = copper % 100
  return `${gold}金 ${silver}银 ${copperRemain}铜`
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

async function handleRefresh() {
  syncing.value = true
  try {
    await goldApi.refreshGold()
    await loadAllGold()
    ElMessage.success('金币数据已同步最新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '同步失败，请确认游戏已保存数据')
  } finally {
    syncing.value = false
  }
}
async function loadAllGold() {
  loading.value = true
  try {
    const response = await goldApi.getAllGold()
    allGold.value = response.data
  } catch (error) {
    ElMessage.error('加载金币数据失败')
  } finally {
    loading.value = false
  }
}

function viewCharacter(characterId: string) {
  router.push(`/gold/character/${characterId}`)
}

onMounted(() => {
  loadCharacters()
  loadAllGold()
})
</script>

<style scoped>
.gold-overview {
  max-width: 1200px;
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

.total-card {
  margin-bottom: 20px;
  border: 1px solid #374151;
}

.total-info {
  display: flex;
  gap: 40px;
}

.total-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.total-label {
  font-size: 14px;
  color: #9ca3af;
}

.total-value {
  font-size: 28px;
  font-weight: 700;
  color: #fbbf24;
}

.characters-card {
  border: 1px solid #374151;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #e5e7eb;
}

.character-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mini-class-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  object-fit: contain;
}

.character-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.character-name {
  font-weight: 600;
  color: #e5e7eb;
}

.character-realm {
  font-size: 12px;
  color: #6b7280;
}

.gold-amount {
  font-weight: 600;
  color: #fbbf24;
}

.update-time {
  font-size: 12px;
  color: #9ca3af;
}
</style>
