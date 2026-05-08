<template>
  <div class="gold-character">
    <div class="page-header">
      <div class="header-left">
        <el-button @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2 class="page-title">
          <el-icon>💰</el-icon>
          {{ summary?.character_gold?.character_name }} - 金币详情
        </h2>
      </div>
      <div class="header-actions">
        <el-button @click="loadSummary">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </div>

    <el-card class="current-gold-card">
      <div class="gold-display">
        <div class="gold-icon">💰</div>
        <div class="gold-info">
          <div class="gold-label">当前金币</div>
          <div class="gold-value">{{ formatGold(summary?.character_gold?.current_gold || 0) }}</div>
          <div class="gold-update">更新于: {{ formatDate(summary?.character_gold?.last_updated) }}</div>
        </div>
      </div>
    </el-card>

    <el-card class="summary-card">
      <div class="summary-tabs">
        <el-radio-group v-model="activeTimeMode" @change="loadSummary">
          <el-radio-button v-for="mode in TimeModes" :key="mode" :value="mode">
            {{ TimeModeLabels[mode] }}
          </el-radio-button>
        </el-radio-group>
      </div>

      <div class="summary-stats">
        <div class="stat-item income">
          <div class="stat-label">收入</div>
          <div class="stat-value">{{ formatGold(summary?.total_in || 0) }}</div>
        </div>
        <div class="stat-item expense">
          <div class="stat-label">支出</div>
          <div class="stat-value">{{ formatGold(summary?.total_out || 0) }}</div>
        </div>
        <div class="stat-item net" :class="{ positive: summary?.net >= 0 }">
          <div class="stat-label">净收入</div>
          <div class="stat-value">{{ summary?.net >= 0 ? '+' : '' }}{{ formatGold(summary?.net || 0) }}</div>
        </div>
      </div>
    </el-card>

    <el-card class="transactions-card">
      <div class="card-header">
        <h3>收支明细</h3>
      </div>
      <el-table :data="summary?.transactions || []" stripe v-loading="loading">
        <el-table-column label="来源" prop="source_title" width="120" />
        <el-table-column label="收入" width="150">
          <template #default="{ row }">
            <span v-if="row.amount_in > 0" class="income-amount">{{ formatGold(row.amount_in) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="支出" width="150">
          <template #default="{ row }">
            <span v-if="row.amount_out > 0" class="expense-amount">{{ formatGold(row.amount_out) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="净收入">
          <template #default="{ row }">
            <span :class="{ positive: row.amount_in - row.amount_out >= 0 }">
              {{ row.amount_in - row.amount_out >= 0 ? '+' : '' }}{{ formatGold(row.amount_in - row.amount_out) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="snapshots-card">
      <div class="card-header">
        <h3>金币历史</h3>
      </div>
      <div v-loading="snapshotsLoading" class="snapshots-container">
        <div v-if="snapshots.length === 0" class="empty-snapshots">
          暂无历史记录
        </div>
        <div v-else class="snapshots-list">
          <div v-for="snapshot in snapshots" :key="snapshot.id" class="snapshot-item">
            <div class="snapshot-date">{{ formatDate(snapshot.snapshot_date) }}</div>
            <div class="snapshot-value">{{ formatGold(snapshot.gold_amount) }}</div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Refresh } from '@element-plus/icons-vue'
import { goldApi } from '@/api'
import type { GoldSummary, GoldSnapshot } from '@/types'
import { TimeModes, TimeModeLabels } from '@/types'

const router = useRouter()
const route = useRoute()

const characterId = route.params.characterId as string
const loading = ref(false)
const snapshotsLoading = ref(false)
const summary = ref<GoldSummary | null>(null)
const snapshots = ref<GoldSnapshot[]>([])
const activeTimeMode = ref('Total')

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

async function loadSummary() {
  loading.value = true
  try {
    const response = await goldApi.getCharacterSummary(characterId, activeTimeMode.value)
    summary.value = response.data
  } catch (error) {
    ElMessage.error('加载金币详情失败')
  } finally {
    loading.value = false
  }
}

async function loadSnapshots() {
  snapshotsLoading.value = true
  try {
    const response = await goldApi.getCharacterSnapshots(characterId, 30)
    snapshots.value = response.data
  } catch (error) {
    ElMessage.error('加载历史记录失败')
  } finally {
    snapshotsLoading.value = false
  }
}

onMounted(() => {
  loadSummary()
  loadSnapshots()
})
</script>

<style scoped>
.gold-character {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 24px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.current-gold-card {
  margin-bottom: 20px;
  border: 1px solid #374151;
}

.gold-display {
  display: flex;
  align-items: center;
  gap: 24px;
}

.gold-icon {
  font-size: 48px;
}

.gold-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.gold-label {
  font-size: 14px;
  color: #9ca3af;
}

.gold-value {
  font-size: 32px;
  font-weight: 700;
  color: #fbbf24;
}

.gold-update {
  font-size: 12px;
  color: #6b7280;
}

.summary-card {
  margin-bottom: 20px;
  border: 1px solid #374151;
}

.summary-tabs {
  margin-bottom: 20px;
}

.summary-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #9ca3af;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
}

.stat-item.income .stat-value {
  color: #22c55e;
}

.stat-item.expense .stat-value {
  color: #ef4444;
}

.stat-item.net .stat-value {
  color: #6b7280;
}

.stat-item.net.positive .stat-value {
  color: #22c55e;
}

.transactions-card,
.snapshots-card {
  margin-bottom: 20px;
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

.income-amount {
  color: #22c55e;
  font-weight: 600;
}

.expense-amount {
  color: #ef4444;
  font-weight: 600;
}

.positive {
  color: #22c55e;
  font-weight: 600;
}

.snapshots-container {
  min-height: 100px;
}

.empty-snapshots {
  text-align: center;
  color: #6b7280;
  padding: 20px;
}

.snapshots-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.snapshot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #1f2937;
  border-radius: 8px;
}

.snapshot-date {
  font-size: 14px;
  color: #9ca3af;
}

.snapshot-value {
  font-size: 16px;
  font-weight: 600;
  color: #fbbf24;
}
</style>
