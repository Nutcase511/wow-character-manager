<template>
  <div class="settings-page">
    <div class="page-header">
      <h1 class="page-title">
        <el-icon><Setting /></el-icon>
        系统配置
      </h1>
      <p class="page-subtitle">管理系统设置和数据源配置</p>
    </div>

    <div class="settings-content">
      <!-- 数据源配置 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><Folder /></el-icon>
            <span>数据源配置</span>
          </div>
        </template>
        
        <el-form :model="dataSourceForm" label-position="top" class="settings-form">
          <el-form-item>
            <template #label>
              <div class="form-label-with-tag">
                <span>Accountant 插件路径</span>
                <el-tag v-if="!isCustomAccountant" size="small" type="info">默认</el-tag>
                <el-tag v-else size="small" type="success">自定义</el-tag>
              </div>
            </template>
            <el-input
              v-model="dataSourceForm.accountantPath"
              placeholder="选择 Accountant_Classic.lua 文件路径"
              readonly
            >
              <template #append>
                <el-button @click="selectFile('accountant')">
                  <el-icon><FolderOpened /></el-icon>
                </el-button>
              </template>
            </el-input>
            <div class="form-tip">Accountant 金币统计插件数据文件</div>
            <div class="form-example">
              <el-icon><InfoFilled /></el-icon>
              <span>示例: C:\WOW\World of Warcraft\_classic_\WTF\Account\你的账号\SavedVariables\Accountant_Classic.lua</span>
            </div>
          </el-form-item>

          <el-form-item>
            <template #label>
              <div class="form-label-with-tag">
                <span>tdInspect 插件路径</span>
                <el-tag v-if="!isCustomTdinspect" size="small" type="info">默认</el-tag>
                <el-tag v-else size="small" type="success">自定义</el-tag>
              </div>
            </template>
            <el-input
              v-model="dataSourceForm.tdinspectPath"
              placeholder="选择 tdInspect.lua 文件路径"
              readonly
            >
              <template #append>
                <el-button @click="selectFile('tdinspect')">
                  <el-icon><FolderOpened /></el-icon>
                </el-button>
              </template>
            </el-input>
            <div class="form-tip">tdInspect 角色装备和天赋数据文件</div>
            <div class="form-example">
              <el-icon><InfoFilled /></el-icon>
              <span>示例: C:\WOW\World of Warcraft\_classic_\WTF\Account\你的账号\SavedVariables\tdInspect.lua</span>
            </div>
          </el-form-item>

          <el-form-item>
            <template #label>
              <div class="form-label-with-tag">
                <span>AtlasLoot 插件路径</span>
                <el-tag v-if="!isCustomAtlasloot" size="small" type="info">默认</el-tag>
                <el-tag v-else size="small" type="success">自定义</el-tag>
              </div>
            </template>
            <el-input
              v-model="dataSourceForm.atlaslootPath"
              placeholder="选择 AtlasLootMY 插件目录"
              readonly
            >
              <template #append>
                <el-button @click="selectFolder('atlasloot')">
                  <el-icon><FolderOpened /></el-icon>
                </el-button>
              </template>
            </el-input>
            <div class="form-tip">AtlasLootMY 副本掉落数据目录</div>
            <div class="form-example">
              <el-icon><InfoFilled /></el-icon>
              <span>示例: C:\WOW\World of Warcraft\_classic_\Interface\AddOns\AtlasLootMY_DungeonsAndRaids</span>
            </div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveDataSource" :loading="saving">
              <el-icon><Check /></el-icon>
              保存配置
            </el-button>
            <el-button @click="testConnections">
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 数据管理 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><DataLine /></el-icon>
            <span>数据管理</span>
          </div>
        </template>

        <div class="data-actions">
          <div class="action-item">
            <div class="action-info">
              <h4>重新导入副本数据</h4>
              <p>从 AtlasLoot 重新导入所有副本和掉落数据</p>
            </div>
            <el-button type="warning" plain @click="reimportDungeons" :loading="reimporting.dungeons">
              <el-icon><Refresh /></el-icon>
              重新导入
            </el-button>
          </div>

          <el-divider />

          <div class="action-item">
            <div class="action-info">
              <h4>重新导入角色数据</h4>
              <p>从 tdInspect 重新导入所有角色数据</p>
            </div>
            <el-button type="warning" plain @click="reimportCharacters" :loading="reimporting.characters">
              <el-icon><Refresh /></el-icon>
              重新导入
            </el-button>
          </div>

          <el-divider />

          <div class="action-item">
            <div class="action-info">
              <h4>重新导入金币数据</h4>
              <p>从 Accountant 重新导入所有金币数据</p>
            </div>
            <el-button type="warning" plain @click="reimportGold" :loading="reimporting.gold">
              <el-icon><Refresh /></el-icon>
              重新导入
            </el-button>
          </div>

          <el-divider />

          <div class="action-item danger">
            <div class="action-info">
              <h4>清空所有数据</h4>
              <p class="danger-text">⚠️ 这将删除所有角色、副本、掉落等数据，不可恢复！</p>
            </div>
            <el-button type="danger" @click="confirmClearAll">
              <el-icon><Delete /></el-icon>
              清空数据
            </el-button>
          </div>
        </div>
      </el-card>

      <!-- 系统信息 -->
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>系统信息</span>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
          <el-descriptions-item label="数据库">SQLite</el-descriptions-item>
          <el-descriptions-item label="后端">FastAPI</el-descriptions-item>
          <el-descriptions-item label="前端">Vue 3 + Element Plus</el-descriptions-item>
          <el-descriptions-item label="数据版本" :span="2">
            <el-tag v-if="dataVersion" type="success">{{ dataVersion }}</el-tag>
            <el-tag v-else type="info">未记录</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div class="stats-section">
          <h4>数据统计</h4>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.characters }}</div>
                <div class="stat-label">角色</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.dungeons }}</div>
                <div class="stat-label">副本</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.bosses }}</div>
                <div class="stat-label">Boss</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-item">
                <div class="stat-value">{{ stats.items }}</div>
                <div class="stat-label">物品</div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>

    <!-- 清空数据确认对话框 -->
    <el-dialog
      v-model="clearDialogVisible"
      title="确认清空所有数据"
      width="400px"
      center
    >
      <div class="clear-warning">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <p>此操作将永久删除以下数据：</p>
        <ul>
          <li>所有角色信息</li>
          <li>所有副本和Boss数据</li>
          <li>所有装备和掉落数据</li>
          <li>所有金币记录</li>
        </ul>
        <p class="confirm-text">请输入 "DELETE" 确认删除：</p>
        <el-input v-model="clearConfirmText" placeholder="输入 DELETE" />
      </div>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="executeClearAll" :disabled="clearConfirmText !== 'DELETE'">
          确认删除
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Setting,
  Folder,
  FolderOpened,
  Check,
  Connection,
  DataLine,
  Refresh,
  Delete,
  InfoFilled,
  WarningFilled
} from '@element-plus/icons-vue'

// 默认配置（从后端配置读取）
const defaultConfig = reactive({
  accountantPath: '',
  tdinspectPath: '',
  atlaslootPath: ''
})

// 数据源表单（用户填写的）
const dataSourceForm = reactive({
  accountantPath: '',
  tdinspectPath: '',
  atlaslootPath: ''
})

// 数据库中的原始配置（用于判断是否为自定义）
const dbConfig = reactive({
  accountantPath: '',
  tdinspectPath: '',
  atlaslootPath: ''
})

// 计算属性：判断是否为自定义配置
const isCustomAccountant = computed(() => {
  return !!dbConfig.accountantPath
})

const isCustomTdinspect = computed(() => {
  return !!dbConfig.tdinspectPath
})

const isCustomAtlasloot = computed(() => {
  return !!dbConfig.atlaslootPath
})

// 加载状态
const saving = ref(false)
const reimporting = reactive({
  dungeons: false,
  characters: false,
  gold: false
})

// 统计数据
const stats = reactive({
  characters: 0,
  dungeons: 0,
  bosses: 0,
  items: 0
})

const dataVersion = ref('')

// 清空数据对话框
const clearDialogVisible = ref(false)
const clearConfirmText = ref('')

// 加载配置
onMounted(async () => {
  await loadSettings()
  await loadStats()
})

// 加载设置
const loadSettings = async () => {
  try {
    const response = await fetch('/api/settings?includeSource=true')
    if (response.ok) {
      const data = await response.json()
      // 保存数据库中的原始配置（用于判断是否为自定义）
      Object.assign(dbConfig, {
        accountantPath: data.dbAccountantPath || '',
        tdinspectPath: data.dbTdinspectPath || '',
        atlaslootPath: data.dbAtlaslootPath || ''
      })
      // 保存默认配置
      Object.assign(defaultConfig, {
        accountantPath: data.defaultAccountantPath || '',
        tdinspectPath: data.defaultTdinspectPath || '',
        atlaslootPath: data.defaultAtlaslootPath || ''
      })
      // 显示当前生效的配置（数据库配置优先）
      Object.assign(dataSourceForm, {
        accountantPath: data.accountantPath || '',
        tdinspectPath: data.tdinspectPath || '',
        atlaslootPath: data.atlaslootPath || ''
      })
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

// 加载统计
const loadStats = async () => {
  try {
    const response = await fetch('/api/stats')
    if (response.ok) {
      const data = await response.json()
      Object.assign(stats, data)
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 选择文件
const selectFile = (type: string) => {
  // 实际项目中这里应该调用文件选择对话框
  // 暂时使用 prompt 模拟
  const path = prompt(`请输入 ${type} 文件路径:`)
  if (path) {
    if (type === 'accountant') {
      dataSourceForm.accountantPath = path
    } else if (type === 'tdinspect') {
      dataSourceForm.tdinspectPath = path
    }
  }
}

// 选择文件夹
const selectFolder = (type: string) => {
  const path = prompt(`请输入 ${type} 目录路径:`)
  if (path) {
    dataSourceForm.atlaslootPath = path
  }
}

// 保存数据源配置
const saveDataSource = async () => {
  saving.value = true
  try {
    // 只保存非空的路径，空的保留之前的默认值
    const dataToSave = {
      accountantPath: dataSourceForm.accountantPath || defaultConfig.accountantPath,
      tdinspectPath: dataSourceForm.tdinspectPath || defaultConfig.tdinspectPath,
      atlaslootPath: dataSourceForm.atlaslootPath || defaultConfig.atlaslootPath
    }
    
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dataToSave)
    })
    if (response.ok) {
      ElMessage.success('配置保存成功')
      // 更新默认配置
      Object.assign(defaultConfig, dataToSave)
    } else {
      ElMessage.error('保存失败')
    }
  } catch (error) {
    ElMessage.error('保存失败: ' + error)
  } finally {
    saving.value = false
  }
}

// 测试连接
const testConnections = async () => {
  try {
    const response = await fetch('/api/settings/test')
    if (response.ok) {
      ElMessage.success('连接测试成功')
    } else {
      ElMessage.error('连接测试失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败: ' + error)
  }
}

// 重新导入副本
const reimportDungeons = async () => {
  reimporting.dungeons = true
  try {
    const response = await fetch('/api/dungeons/reimport', { method: 'POST' })
    if (response.ok) {
      ElMessage.success('副本数据重新导入成功')
      await loadStats()
    } else {
      ElMessage.error('导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error)
  } finally {
    reimporting.dungeons = false
  }
}

// 重新导入角色
const reimportCharacters = async () => {
  reimporting.characters = true
  try {
    const response = await fetch('/api/characters/reimport', { method: 'POST' })
    if (response.ok) {
      ElMessage.success('角色数据重新导入成功')
      await loadStats()
    } else {
      ElMessage.error('导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error)
  } finally {
    reimporting.characters = false
  }
}

// 重新导入金币
const reimportGold = async () => {
  reimporting.gold = true
  try {
    const response = await fetch('/api/gold/reimport', { method: 'POST' })
    if (response.ok) {
      ElMessage.success('金币数据重新导入成功')
      await loadStats()
    } else {
      ElMessage.error('导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error)
  } finally {
    reimporting.gold = false
  }
}

// 确认清空数据
const confirmClearAll = () => {
  clearConfirmText.value = ''
  clearDialogVisible.value = true
}

// 执行清空
const executeClearAll = async () => {
  try {
    const response = await fetch('/api/settings/clear-all', { method: 'DELETE' })
    if (response.ok) {
      ElMessage.success('所有数据已清空')
      clearDialogVisible.value = false
      await loadStats()
    } else {
      ElMessage.error('清空失败')
    }
  } catch (error) {
    ElMessage.error('清空失败: ' + error)
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 28px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0 0 8px 0;
}

.page-title .el-icon {
  font-size: 32px;
  color: #f39c12;
}

.page-subtitle {
  color: #6b7280;
  margin: 0;
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.settings-card {
  background: #1f2937;
  border: 1px solid #374151;
}

.settings-card :deep(.el-card__header) {
  background: #172033;
  border-bottom: 1px solid #374151;
  padding: 16px 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #e5e7eb;
}

.card-header .el-icon {
  color: #f39c12;
}

.settings-form {
  max-width: 600px;
}

.form-tip {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.form-example {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 11px;
  color: #4b5563;
  margin-top: 6px;
  padding: 6px 10px;
  background: #172033;
  border-radius: 4px;
  border-left: 3px solid #3b82f6;
}

.form-example .el-icon {
  font-size: 12px;
  color: #3b82f6;
  margin-top: 1px;
  flex-shrink: 0;
}

.form-example span {
  word-break: break-all;
  line-height: 1.4;
}

.form-label-with-tag {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-label-with-tag .el-tag {
  font-size: 11px;
  height: 18px;
  line-height: 16px;
  padding: 0 6px;
}

.data-actions {
  display: flex;
  flex-direction: column;
}

.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.action-item.danger {
  background: rgba(239, 68, 68, 0.05);
  margin: 0 -20px;
  padding: 16px 20px;
  border-radius: 4px;
}

.action-info h4 {
  margin: 0 0 4px 0;
  color: #e5e7eb;
  font-size: 15px;
}

.action-info p {
  margin: 0;
  color: #6b7280;
  font-size: 13px;
}

.action-info .danger-text {
  color: #ef4444;
}

.stats-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #374151;
}

.stats-section h4 {
  margin: 0 0 16px 0;
  color: #e5e7eb;
  font-size: 15px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #172033;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #f39c12;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.clear-warning {
  text-align: center;
}

.warning-icon {
  font-size: 48px;
  color: #ef4444;
  margin-bottom: 16px;
}

.clear-warning p {
  color: #e5e7eb;
  margin: 8px 0;
}

.clear-warning ul {
  text-align: left;
  display: inline-block;
  color: #9ca3af;
  margin: 8px 0;
}

.clear-warning li {
  margin: 4px 0;
}

.confirm-text {
  margin-top: 16px !important;
  font-weight: 500;
}

:deep(.el-divider) {
  margin: 0;
  border-color: #374151;
}

:deep(.el-descriptions__body) {
  background: #172033;
}

:deep(.el-descriptions__label) {
  background: #1f2937 !important;
}
</style>
