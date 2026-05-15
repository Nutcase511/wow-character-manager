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
            <template #label>
              <div class="form-label-with-tag">
                <span>TitanBistooltip 插件路径</span>
                <el-tag v-if="!isCustomTitanbis" size="small" type="info">默认</el-tag>
                <el-tag v-else size="small" type="success">自定义</el-tag>
              </div>
            </template>
            <el-input
              v-model="dataSourceForm.titanbisPath"
              placeholder="选择 TitanBistooltip 插件目录"
              readonly
            >
              <template #append>
                <el-button @click="selectFolder('titanbis')">
                  <el-icon><FolderOpened /></el-icon>
                </el-button>
              </template>
            </el-input>
            <div class="form-tip">TitanBistooltip 重铸泰坦毕业装备(BiS)插件目录</div>
            <div class="form-example">
              <el-icon><InfoFilled /></el-icon>
              <span>示例: C:\WOW\World of Warcraft\_classic_\Interface\AddOns\TitanBistooltip</span>
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
            <el-button type="success" plain @click="autoDetectPaths" :loading="autoDetecting">
              <el-icon><Search /></el-icon>
              自动检测
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

          <div class="action-item">
            <div class="action-info">
              <h4>重新导入毕业装备(BiS)</h4>
              <p>从 TitanBistooltip 插件重新导入重铸泰坦各阶段毕业装备列表</p>
            </div>
            <el-button type="warning" plain @click="reimportBis" :loading="reimporting.bis">
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

    <!-- 目录浏览对话框 -->
    <el-dialog
      v-model="browseDialogVisible"
      :title="browseTitle"
      width="600px"
      destroy-on-close
    >
      <div class="browse-dialog">
        <div class="browse-path-bar">
          <el-input v-model="browseCurrentPath" placeholder="输入路径或从下方选择" size="small">
            <template #prepend>路径</template>
            <template #append>
              <el-button @click="browseGoTo(browseCurrentPath)" size="small">前往</el-button>
            </template>
          </el-input>
        </div>
        <div class="browse-list" v-loading="browseLoading">
          <div class="browse-item" v-if="browseParent" @click="browseGoTo(browseParent)">
            <el-icon><FolderOpened /></el-icon>
            <span class="browse-name">..</span>
            <span class="browse-meta">返回上级</span>
          </div>
          <div
            v-for="item in browseItems"
            :key="item.path"
            class="browse-item"
            :class="{ 'browse-dir': item.is_dir, 'browse-file': !item.is_dir }"
            @click="onBrowseItemClick(item)"
            @dblclick="onBrowseItemDblClick(item)"
          >
            <el-icon v-if="item.is_dir"><Folder /></el-icon>
            <el-icon v-else><Document /></el-icon>
            <span class="browse-name">{{ item.name }}</span>
            <span class="browse-meta" v-if="item.is_dir">文件夹</span>
            <span class="browse-meta" v-else>{{ formatSize(item.size) }}</span>
          </div>
          <el-empty v-if="!browseLoading && browseItems.length === 0" description="空目录" :image-size="40" />
        </div>
      </div>
      <template #footer>
        <el-button @click="browseDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmBrowseSelection" :disabled="!browseSelectedPath">
          选择: {{ browseSelectedPath || '未选择' }}
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
  WarningFilled,
  Search,
  Document
} from '@element-plus/icons-vue'

// 默认配置（从后端配置读取）
const defaultConfig = reactive({
  accountantPath: '',
  tdinspectPath: '',
  atlaslootPath: '',
  titanbisPath: ''
})

// 数据源表单（用户填写的）
const dataSourceForm = reactive({
  accountantPath: '',
  tdinspectPath: '',
  atlaslootPath: '',
  titanbisPath: ''
})

// 数据库中的原始配置（用于判断是否为自定义）
const dbConfig = reactive({
  accountantPath: '',
  tdinspectPath: '',
  atlaslootPath: '',
  titanbisPath: ''
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

const isCustomTitanbis = computed(() => {
  return !!dbConfig.titanbisPath
})

// 加载状态
const saving = ref(false)
const reimporting = reactive({
  dungeons: false,
  characters: false,
  gold: false,
  bis: false
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

// 目录浏览
const browseDialogVisible = ref(false)
const browseLoading = ref(false)
const browseItems = ref<any[]>([])
const browseCurrentPath = ref('')
const browseParent = ref('')
const browseSelectedPath = ref('')
const browseType = ref<'file' | 'dir' | 'lua'>('file')
const browseTarget = ref<'accountant' | 'tdinspect' | 'atlasloot'>('accountant')
const browseTitle = computed(() => {
  const names: Record<string, string> = {
    accountant: '选择 Accountant 文件',
    tdinspect: '选择 tdInspect 文件',
    atlasloot: '选择 AtlasLoot 目录'
  }
  return names[browseTarget.value] || '浏览'
})

// 自动检测
const autoDetecting = ref(false)

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
        atlaslootPath: data.dbAtlaslootPath || '',
        titanbisPath: data.dbTitanbisPath || ''
      })
      // 保存默认配置
      Object.assign(defaultConfig, {
        accountantPath: data.defaultAccountantPath || '',
        tdinspectPath: data.defaultTdinspectPath || '',
        atlaslootPath: data.defaultAtlaslootPath || '',
        titanbisPath: data.defaultTitanbisPath || ''
      })
      // 显示当前生效的配置（数据库配置优先）
      Object.assign(dataSourceForm, {
        accountantPath: data.accountantPath || '',
        tdinspectPath: data.tdinspectPath || '',
        atlaslootPath: data.atlaslootPath || '',
        titanbisPath: data.titanbisPath || ''
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
const selectFile = (type: 'accountant' | 'tdinspect') => {
  browseTarget.value = type
  browseType.value = 'lua'
  browseSelectedPath.value = ''
  // 从当前配置路径开始浏览
  const currentPath = type === 'accountant' ? dataSourceForm.accountantPath : dataSourceForm.tdinspectPath
  browseCurrentPath.value = currentPath ? currentPath.split('\\').slice(0, -1).join('\\') || '' : ''
  browseDialogVisible.value = true
  browseGoTo(browseCurrentPath.value || '')
}

// 选择文件夹
const selectFolder = (type: 'atlasloot' | 'titanbis') => {
  browseTarget.value = type
  browseType.value = 'dir'
  browseSelectedPath.value = ''
  const currentPath = type === 'atlasloot' ? dataSourceForm.atlaslootPath : dataSourceForm.titanbisPath
  browseCurrentPath.value = currentPath || ''
  browseDialogVisible.value = true
  browseGoTo(browseCurrentPath.value || '')
}

// 浏览目录
const browseGoTo = async (path: string) => {
  browseLoading.value = true
  try {
    const params = new URLSearchParams()
    if (path) params.set('path', path)
    if (browseType.value === 'lua') params.set('file_type', 'lua')
    if (browseType.value === 'dir') params.set('file_type', 'dir')

    const response = await fetch(`/api/settings/browse?${params}`)
    if (response.ok) {
      const data = await response.json()
      browseItems.value = data.items || []
      browseCurrentPath.value = data.current_path || ''
      browseParent.value = data.parent || ''
    } else {
      ElMessage.error('无法浏览该路径')
    }
  } catch (error) {
    ElMessage.error('浏览失败')
  } finally {
    browseLoading.value = false
  }
}

// 点击浏览项
const onBrowseItemClick = (item: any) => {
  browseSelectedPath.value = item.path
}

// 双击进入目录
const onBrowseItemDblClick = (item: any) => {
  if (item.is_dir) {
    browseGoTo(item.path)
  } else {
    browseSelectedPath.value = item.path
  }
}

// 确认浏览选择
const confirmBrowseSelection = () => {
  if (!browseSelectedPath.value) return
  if (browseTarget.value === 'accountant') {
    dataSourceForm.accountantPath = browseSelectedPath.value
  } else if (browseTarget.value === 'tdinspect') {
    dataSourceForm.tdinspectPath = browseSelectedPath.value
  } else if (browseTarget.value === 'atlasloot') {
    dataSourceForm.atlaslootPath = browseSelectedPath.value
  } else if (browseTarget.value === 'titanbis') {
    dataSourceForm.titanbisPath = browseSelectedPath.value
  }
  browseDialogVisible.value = false
}

// 格式化文件大小
const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 自动检测路径
const autoDetectPaths = async () => {
  autoDetecting.value = true
  try {
    const response = await fetch('/api/settings/auto-detect')
    if (response.ok) {
      const data = await response.json()
      if (data.detected) {
        if (data.accountantPath) dataSourceForm.accountantPath = data.accountantPath
        if (data.tdinspectPath) dataSourceForm.tdinspectPath = data.tdinspectPath
        if (data.atlaslootPath) dataSourceForm.atlaslootPath = data.atlaslootPath
        if (data.titanbisPath) dataSourceForm.titanbisPath = data.titanbisPath
        ElMessage.success(`已检测到 WoW 目录: ${data.wow_dir}`)
      } else {
        ElMessage.warning('未检测到 WoW 安装目录，请手动配置路径')
      }
    } else {
      ElMessage.error('自动检测失败')
    }
  } catch (error) {
    ElMessage.error('自动检测失败')
  } finally {
    autoDetecting.value = false
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
      atlaslootPath: dataSourceForm.atlaslootPath || defaultConfig.atlaslootPath,
      titanbisPath: dataSourceForm.titanbisPath || defaultConfig.titanbisPath
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
    const response = await fetch('/api/dungeons/import-atlasloot', { method: 'POST' })
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
    const response = await fetch('/api/character-refresh/refresh-all', { method: 'POST' })
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
    const response = await fetch('/api/gold/refresh', { method: 'POST' })
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

// 重新导入BiS
const reimportBis = async () => {
  reimporting.bis = true
  try {
    const response = await fetch('/api/settings/import-bis', { method: 'POST' })
    if (response.ok) {
      const data = await response.json()
      ElMessage.success(data.message || 'BiS 数据导入成功')
    } else {
      const data = await response.json()
      ElMessage.error(data.detail || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error)
  } finally {
    reimporting.bis = false
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
  background: rgba(31, 41, 55, 0.55);
  border: 1px solid rgba(55, 65, 81, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.settings-card :deep(.el-card__header) {
  background: rgba(23, 32, 51, 0.6);
  border-bottom: 1px solid rgba(55, 65, 81, 0.4);
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

/* 目录浏览对话框 */
.browse-dialog {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.browse-path-bar {
  flex-shrink: 0;
}

.browse-list {
  height: 350px;
  overflow-y: auto;
  border: 1px solid #374151;
  border-radius: 6px;
  padding: 8px;
  background: #111827;
}

.browse-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s;
  color: #e5e7eb;
}

.browse-item:hover {
  background: #1f2937;
}

.browse-item .el-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.browse-dir .el-icon {
  color: #f39c12;
}

.browse-file .el-icon {
  color: #6b7280;
}

.browse-name {
  flex: 1;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.browse-meta {
  font-size: 11px;
  color: #6b7280;
  flex-shrink: 0;
}
</style>
