<template>
  <div class="token-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Coin /></el-icon>
        时光徽章 & 兑换计算器
      </h2>
      <div class="header-actions">
        <el-button @click="loadAll" :loading="loading">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
        <el-button type="primary" @click="showRecordDialog = true">
          <el-icon><Plus /></el-icon>
          记录价格
        </el-button>
      </div>
    </div>

    <div class="stats-grid">
      <el-card class="stat-card token-card">
        <div class="stat-body">
          <div class="stat-icon-wrap">
            <el-icon class="stat-icon"><Coin /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">时光徽章价格</div>
            <div class="stat-value">
              {{ currentToken ? formatGold(currentToken.price_gold) : '--' }}
            </div>
            <div class="stat-time">
              {{ currentToken ? formatTime(currentToken.recorded_at) : '暂无数据' }}
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card rate-card">
        <div class="stat-body">
          <div class="stat-icon-wrap">
            <el-icon class="stat-icon"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">金币汇率 (1元 = ?金)</div>
            <div class="stat-value">
              {{ currentRate ? currentRate.gold_per_cny.toFixed(1) + ' 金' : '--' }}
            </div>
            <div class="stat-time">
              {{ currentRate ? formatTime(currentRate.recorded_at) : '暂无数据' }}
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="stat-card calc-card">
        <div class="stat-body">
          <div class="stat-icon-wrap">
            <el-icon class="stat-icon"><WalletFilled /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-label">官方参考比例</div>
            <div class="stat-value">
              90 元 / 徽章
            </div>
            <div class="stat-time">
              时光徽章官方定价
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="charts-container">
      <el-card class="chart-card">
        <div class="chart-header">
          <h3>时光徽章价格走势</h3>
          <el-select v-model="historyLimit" class="limit-select" @change="loadTokenHistory">
            <el-option label="最近 7 天" :value="7" />
            <el-option label="最近 15 天" :value="15" />
            <el-option label="最近 30 天" :value="30" />
          </el-select>
        </div>
        <div ref="tokenChartRef" class="chart"></div>
      </el-card>
    </div>

    <div class="calc-section">
      <el-card class="calc-card-wide">
        <div class="card-header">
          <h3>
            <el-icon><Wallet /></el-icon>
            金币兑换计算器
          </h3>
        </div>
        <div class="calc-body">
          <div class="calc-row">
            <div class="calc-field">
              <label>金币数量</label>
              <el-input-number v-model="calcGold" :min="0" :step="1000" placeholder="输入金币" @change="calcFromGold" />
            </div>
            <div class="calc-arrow">
              <el-icon><Sort /></el-icon>
            </div>
            <div class="calc-field">
              <label>人民币 (元)</label>
              <el-input-number v-model="calcCny" :min="0" :step="10" :precision="2" placeholder="输入人民币" @change="calcFromCny" />
            </div>
          </div>
          <div v-if="calcResult" class="calc-result">
            <div class="result-item">
              <span class="result-label">兑换比例:</span>
              <span class="result-value">{{ calcResult.rate }} 金/元</span>
            </div>
            <div class="result-item">
              <span class="result-label">当前时光徽章价格:</span>
              <span class="result-value">{{ formatGold(calcResult.token_price) }}</span>
            </div>
            <div class="result-item">
              <span class="result-label">可购买时光徽章:</span>
              <span class="result-value highlight">{{ calcResult.token_count?.toFixed(2) ?? '数据不足' }}</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <div class="history-section">
      <el-card>
        <div class="card-header">
          <h3>价格记录历史</h3>
        </div>
        <el-tabs v-model="historyTab">
          <el-tab-pane label="时光徽章" name="token">
            <el-table :data="tokenHistory" stripe v-loading="loading" style="width: 100%">
              <el-table-column label="价格 (金币)" prop="price_gold" align="right">
                <template #default="{ row }">
                  <span class="gold-amount">{{ formatGold(row.price_gold) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="来源" prop="source" align="center" width="100" />
              <el-table-column label="备注" prop="notes" min-width="150" />
              <el-table-column label="记录时间" prop="recorded_at" align="center" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.recorded_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="汇率" name="rate">
            <el-table :data="rateHistory" stripe v-loading="loading" style="width: 100%">
              <el-table-column label="汇率 (金/元)" prop="gold_per_cny" align="right">
                <template #default="{ row }">
                  <span class="gold-amount">{{ row.gold_per_cny }} 金/元</span>
                </template>
              </el-table-column>
              <el-table-column label="来源" prop="source" align="center" width="100" />
              <el-table-column label="备注" prop="notes" min-width="150" />
              <el-table-column label="记录时间" prop="recorded_at" align="center" width="180">
                <template #default="{ row }">
                  {{ formatTime(row.recorded_at) }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>

    <el-dialog v-model="showRecordDialog" title="记录价格" width="420px">
      <el-form label-position="top">
        <el-form-item label="时光徽章价格 (金币)">
          <el-input-number v-model="recordTokenPrice" :min="1" style="width: 100%" placeholder="输入当前拍卖行价格" />
        </el-form-item>
        <el-form-item label="金币汇率 (1元可兑换金币数)">
          <el-input-number v-model="recordRateValue" :min="0.1" :step="0.5" :precision="1" style="width: 100%" placeholder="输入当前市场汇率" />
        </el-form-item>
        <el-form-item label="备注 (可选)">
          <el-input v-model="recordNotes" placeholder="如：重置后价格 / P4阶段" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRecordDialog = false">取消</el-button>
        <el-button type="primary" @click="submitRecord" :loading="recording">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, Plus, Coin, Wallet, WalletFilled, Sort } from '@element-plus/icons-vue'
import { exchangeApi } from '@/api'
import * as echarts from 'echarts'

const loading = ref(false)
const showRecordDialog = ref(false)
const recording = ref(false)

const currentToken = ref<any>(null)
const currentRate = ref<any>(null)
const tokenHistory = ref<any[]>([])
const rateHistory = ref<any[]>([])
const historyLimit = ref(30)
const historyTab = ref('token')

const recordTokenPrice = ref(0)
const recordRateValue = ref(0)
const recordNotes = ref('')

const calcGold = ref<number | null>(null)
const calcCny = ref<number | null>(null)
const calcResult = ref<any>(null)

const tokenChartRef = ref<HTMLElement | null>(null)
let tokenChart: echarts.ECharts | null = null

function formatGold(price: number): string {
  if (!price && price !== 0) return '--'
  return `${price.toLocaleString()} 金`
}

function formatTime(timeStr: string): string {
  if (!timeStr) return '--'
  const d = new Date(timeStr)
  return d.toLocaleString('zh-CN')
}

async function loadCurrentToken() {
  try {
    const data = await exchangeApi.getCurrentToken()
    currentToken.value = data
  } catch {
    currentToken.value = null
  }
}

async function loadCurrentRate() {
  try {
    const data = await exchangeApi.getCurrentRate()
    currentRate.value = data
  } catch {
    currentRate.value = null
  }
}

async function loadTokenHistory() {
  try {
    const data = await exchangeApi.getTokenHistory(historyLimit.value)
    tokenHistory.value = data
    updateChart()
  } catch {
    tokenHistory.value = []
  }
}

async function loadRateHistory() {
  try {
    const data = await exchangeApi.getRateHistory(historyLimit.value)
    rateHistory.value = data
  } catch {
    rateHistory.value = []
  }
}

async function loadAll() {
  loading.value = true
  await Promise.all([
    loadCurrentToken(),
    loadCurrentRate(),
    loadTokenHistory(),
    loadRateHistory()
  ])
  loading.value = false
}

function calcFromGold() {
  if (calcGold.value === null || calcGold.value <= 0) {
    calcResult.value = null
    return
  }
  exchangeApi.calculate({ gold: calcGold.value }).then(data => {
    calcResult.value = data
    calcCny.value = data.cny
  }).catch(() => {
    calcResult.value = null
  })
}

function calcFromCny() {
  if (calcCny.value === null || calcCny.value <= 0) {
    calcResult.value = null
    return
  }
  exchangeApi.calculate({ cny: calcCny.value }).then(data => {
    calcResult.value = data
    calcGold.value = data.gold
  }).catch(() => {
    calcResult.value = null
  })
}

async function submitRecord() {
  if (recordTokenPrice.value <= 0 && recordRateValue.value <= 0) {
    ElMessage.warning('请至少输入一个价格')
    return
  }
  recording.value = true
  try {
    const notes = recordNotes.value || undefined
    if (recordTokenPrice.value > 0) {
      await exchangeApi.recordToken(recordTokenPrice.value, notes)
    }
    if (recordRateValue.value > 0) {
      await exchangeApi.recordRate(recordRateValue.value, notes)
    }
    ElMessage.success('记录成功')
    showRecordDialog.value = false
    recordTokenPrice.value = 0
    recordRateValue.value = 0
    recordNotes.value = ''
    await loadAll()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '记录失败')
  } finally {
    recording.value = false
  }
}

function updateChart() {
  if (!tokenChartRef.value) return
  nextTick(() => {
    if (!tokenChart) {
      tokenChart = echarts.init(tokenChartRef.value)
    }
    const sorted = [...tokenHistory.value].reverse()
    const dates = sorted.map((r: any) => {
      const d = new Date(r.recorded_at)
      return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
    })
    const prices = sorted.map((r: any) => r.price_gold)

    tokenChart.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(31, 41, 55, 0.9)',
        borderColor: '#374151',
        textStyle: { color: '#e5e7eb' }
      },
      grid: { left: 60, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#374151' } },
        axisLabel: { color: '#9ca3af', fontSize: 11 }
      },
      yAxis: {
        type: 'value',
        name: '金币 (金)',
        nameTextStyle: { color: '#9ca3af' },
        axisLine: { show: false },
        splitLine: { lineStyle: { color: 'rgba(55, 65, 81, 0.5)' } },
        axisLabel: { color: '#9ca3af' }
      },
      series: [{
        data: prices,
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#f39c12' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(243, 156, 18, 0.3)' },
            { offset: 1, color: 'rgba(243, 156, 18, 0.02)' }
          ])
        },
        itemStyle: { color: '#f39c12' }
      }]
    })
  })
}

onMounted(() => {
  loadAll()
})

onUnmounted(() => {
  if (tokenChart) {
    tokenChart.dispose()
    tokenChart = null
  }
})
</script>

<style scoped>
.token-view {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 22px;
  font-weight: 700;
  color: #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  overflow: hidden;
}

.stat-body {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 4px 0;
}

.stat-icon-wrap {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.token-card .stat-icon-wrap {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.2), rgba(231, 76, 60, 0.1));
}

.rate-card .stat-icon-wrap {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.2), rgba(39, 174, 96, 0.1));
}

.calc-card .stat-icon-wrap {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(41, 128, 185, 0.1));
}

.stat-icon {
  font-size: 24px;
}

.token-card .stat-icon { color: #f39c12; }
.rate-card .stat-icon { color: #2ecc71; }
.calc-card .stat-icon { color: #3498db; }

.stat-info {
  flex: 1;
  min-width: 0;
}

.stat-label {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #e5e7eb;
  line-height: 1.2;
}

.stat-time {
  font-size: 11px;
  color: #6b7280;
  margin-top: 4px;
}

.charts-container {
  margin-bottom: 20px;
}

.chart-card {
  border-radius: 12px;
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #e5e7eb;
}

.chart {
  width: 100%;
  height: 320px;
}

.calc-section {
  margin-bottom: 20px;
}

.calc-card-wide {
  border-radius: 12px;
}

.card-header {
  margin-bottom: 16px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #e5e7eb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.calc-body {
  padding: 4px 0;
}

.calc-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.calc-field {
  flex: 1;
}

.calc-field label {
  display: block;
  font-size: 13px;
  color: #9ca3af;
  margin-bottom: 8px;
}

.calc-arrow {
  padding-top: 24px;
  color: #6b7280;
  font-size: 20px;
}

.calc-result {
  margin-top: 20px;
  padding: 16px;
  background: rgba(31, 41, 55, 0.5);
  border-radius: 10px;
  border: 1px solid rgba(55, 65, 81, 0.4);
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 14px;
}

.result-label {
  color: #9ca3af;
}

.result-value {
  color: #e5e7eb;
  font-weight: 600;
}

.result-value.highlight {
  color: #f39c12;
  font-size: 16px;
}

.history-section {
  margin-bottom: 20px;
}

.gold-amount {
  color: #f39c12;
  font-weight: 600;
}
</style>