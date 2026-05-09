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

    <!-- 统计卡片 -->
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
        <div class="total-item">
          <span class="total-label">本月收入</span>
          <span class="total-value income">{{ formatGold(monthlyIncome) }}</span>
        </div>
        <div class="total-item">
          <span class="total-label">本月支出</span>
          <span class="total-value expense">{{ formatGold(monthlyExpense) }}</span>
        </div>
      </div>
    </el-card>

    <!-- 图表区域 -->
    <div class="charts-container">
      <!-- 金币趋势图 -->
      <el-card class="chart-card">
        <div class="chart-header">
          <h3>金币获取趋势</h3>
          <el-select v-model="period" class="period-select" @change="loadMonthlyStats">
            <el-option label="按月查看" value="month" />
            <el-option label="按年查看" value="year" />
          </el-select>
        </div>
        <div ref="trendChartRef" class="chart"></div>
      </el-card>

      <!-- 角色金币对比图 -->
      <el-card class="chart-card">
        <div class="chart-header">
          <h3>角色金币对比</h3>
        </div>
        <div ref="barChartRef" class="chart"></div>
      </el-card>
    </div>

    <!-- 角色金币列表 -->
    <el-card class="characters-card">
      <div class="card-header">
        <h3>角色金币</h3>
      </div>
      <el-table :data="goldWithClass" stripe v-loading="loading" style="width: 100%">
        <el-table-column label="角色" min-width="180">
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
        <el-table-column label="当前金币" align="right">
          <template #default="{ row }">
            <span class="gold-amount">{{ formatGold(row.current_gold) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="更新时间" align="center">
          <template #default="{ row }">
            <span class="update-time">{{ formatDate(row.last_updated) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" align="center">
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
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { goldApi, characterApi } from '@/api'
import type { CharacterGold } from '@/types'
import { getClassIcon } from '@/utils/classIcons'

// ECharts
import * as echarts from 'echarts'

const router = useRouter()

const loading = ref(false)
const syncing = ref(false)
const allGold = ref<CharacterGold[]>([])
const characters = ref<any[]>([])
const period = ref('month')

// 图表引用
const trendChartRef = ref<HTMLElement | null>(null)
const barChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

// 图表数据
const monthlyStats = ref<any[]>([])
const characterStats = ref<any[]>([])

const totalGold = computed(() => {
  return allGold.value.reduce((sum, g) => sum + g.current_gold, 0)
})

const monthlyIncome = computed(() => {
  const currentMonth = new Date().toISOString().slice(0, 7)
  return monthlyStats.value
    .filter(s => s.period === currentMonth)
    .reduce((sum, s) => sum + s.total_in, 0)
})

const monthlyExpense = computed(() => {
  const currentMonth = new Date().toISOString().slice(0, 7)
  return monthlyStats.value
    .filter(s => s.period === currentMonth)
    .reduce((sum, s) => sum + s.total_out, 0)
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
    await loadMonthlyStats()
    await loadCharacterStats()
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

async function loadMonthlyStats() {
  try {
    const response = await goldApi.getMonthlyStats(period.value)
    monthlyStats.value = response.data
    updateTrendChart()
  } catch (error) {
    console.error('加载月度统计失败:', error)
  }
}

async function loadCharacterStats() {
  try {
    const response = await goldApi.getCharacterStats()
    characterStats.value = response.data
    updateBarChart()
  } catch (error) {
    console.error('加载角色统计失败:', error)
  }
}

function initCharts() {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    updateTrendChart()
  }
  
  if (barChartRef.value) {
    barChart = echarts.init(barChartRef.value)
    updateBarChart()
  }
}

function updateTrendChart() {
  if (!trendChart || monthlyStats.value.length === 0) return

  const periods = monthlyStats.value.map(s => {
    const parts = s.period.split('-')
    if (period.value === 'year') {
      // 按年查看时，显示月份（如 "1月", "2月"）
      return parts[1] + '月'
    } else {
      // 按月查看时，显示日期（如 "1日", "2日"）
      return parts[2] + '日'
    }
  })

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let result = `<strong>${periods[params[0].dataIndex]}</strong><br/>`
        params.forEach((item: any) => {
          const value = Math.floor(item.value / 10000)
          result += `${item.marker} ${item.seriesName}: ${value}金<br/>`
        })
        return result
      }
    },
    legend: {
      data: ['收入', '支出', '净收入'],
      top: 0,
      textStyle: { color: '#9ca3af' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: periods,
      axisLabel: { color: '#9ca3af' }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#9ca3af',
        formatter: (value: number) => Math.floor(value / 10000) + '金'
      }
    },
    series: [
      {
        name: '收入',
        type: 'line',
        smooth: true,
        data: monthlyStats.value.map(s => s.total_in),
        lineStyle: { color: '#4ade80' },
        itemStyle: { color: '#4ade80' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(74, 222, 128, 0.3)' },
            { offset: 1, color: 'rgba(74, 222, 128, 0)' }
          ])
        }
      },
      {
        name: '支出',
        type: 'line',
        smooth: true,
        data: monthlyStats.value.map(s => s.total_out),
        lineStyle: { color: '#f87171' },
        itemStyle: { color: '#f87171' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(248, 113, 113, 0.3)' },
            { offset: 1, color: 'rgba(248, 113, 113, 0)' }
          ])
        }
      },
      {
        name: '净收入',
        type: 'line',
        smooth: true,
        data: monthlyStats.value.map(s => s.net),
        lineStyle: { color: '#fbbf24', width: 3 },
        itemStyle: { color: '#fbbf24' }
      }
    ]
  }

  trendChart.setOption(option)
}

function updateBarChart() {
  if (!barChart || characterStats.value.length === 0) return

  const names = characterStats.value.map(s => s.character_name)
  const values = characterStats.value.map(s => s.current_gold)

  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const item = params[0]
        const value = Math.floor(item.value / 10000)
        return `<strong>${item.name}</strong><br/>金币: ${value}金`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { 
        color: '#9ca3af',
        rotate: names.length > 6 ? 30 : 0
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#9ca3af',
        formatter: (value: number) => Math.floor(value / 10000) + '金'
      }
    },
    series: [
      {
        type: 'bar',
        data: values.map((v, i) => ({
          value: v,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: getBarColor(i, 'top') },
              { offset: 1, color: getBarColor(i, 'bottom') }
            ]),
            borderRadius: [4, 4, 0, 0]
          }
        })),
        barWidth: '50%'
      }
    ]
  }

  barChart.setOption(option)
}

function getBarColor(index: number, position: string): string {
  const colors = [
    ['#fbbf24', '#f59e0b'],
    ['#4ade80', '#22c55e'],
    ['#60a5fa', '#3b82f6'],
    ['#f472b6', '#ec4899'],
    ['#a78bfa', '#8b5cf6'],
    ['#fb923c', '#f97316'],
    ['#34d399', '#10b981'],
    ['#a5b4fc', '#818cf8']
  ]
  const colorSet = colors[index % colors.length]
  return position === 'top' ? colorSet[0] : colorSet[1]
}

function viewCharacter(characterId: string) {
  router.push(`/gold/character/${characterId}`)
}

function handleResize() {
  trendChart?.resize()
  barChart?.resize()
}

onMounted(async () => {
  await loadCharacters()
  await loadAllGold()
  await loadMonthlyStats()
  await loadCharacterStats()
  
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.gold-overview {
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

.total-card {
  margin-bottom: 20px;
  border: 1px solid #374151;
}

.total-info {
  display: flex;
  gap: 40px;
  flex-wrap: wrap;
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

.total-value.income {
  color: #4ade80;
}

.total-value.expense {
  color: #f87171;
}

/* 图表容器 */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.chart-card {
  border: 1px solid #374151;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  color: #e5e7eb;
}

.period-select {
  width: 120px;
}

.chart {
  height: 300px;
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
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  object-fit: cover;
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

@media (max-width: 768px) {
  .charts-container {
    grid-template-columns: 1fr;
  }
  
  .total-info {
    gap: 20px;
  }
  
  .total-value {
    font-size: 22px;
  }
}
</style>
