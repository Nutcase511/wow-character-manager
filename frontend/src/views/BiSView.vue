<template>
  <div class="bis-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><TrophyBase /></el-icon>
        毕业装备
      </h2>
      <div class="header-actions">
        <el-select v-model="selectedClass" placeholder="选择职业" style="width: 160px" @change="onClassChange">
          <el-option v-for="(label, key) in BisClassNameMap" :key="key" :label="label" :value="key">
            <div class="option-with-icon">
              <img :src="getClassIcon(key)" class="option-icon" />
              <span>{{ label }}</span>
            </div>
          </el-option>
        </el-select>
        <el-select v-model="selectedSpec" placeholder="选择天赋" style="width: 160px" @change="onSpecChange" :disabled="!selectedClass">
          <el-option v-for="spec in specs" :key="spec" :label="SpecNameMap[spec] || spec" :value="spec" />
        </el-select>
        <el-select v-model="selectedPhase" placeholder="选择阶段" style="width: 140px" @change="loadBisList" :disabled="!selectedSpec">
          <el-option v-for="phase in phases" :key="phase" :label="PhaseNameMap[phase] || phase" :value="phase" />
        </el-select>
        <el-button type="primary" @click="showImportDialog = true" :disabled="!bisItems.length">
          <el-icon><Download /></el-icon>
          导入到角色
        </el-button>
      </div>
    </div>

    <el-card class="bis-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span v-if="selectedClass && selectedSpec && selectedPhase">
            {{ BisClassNameMap[selectedClass] }} - {{ SpecNameMap[selectedSpec] || selectedSpec }} - {{ PhaseNameMap[selectedPhase] || selectedPhase }}
          </span>
          <span v-else>请选择职业、天赋和阶段</span>
          <el-tag v-if="bisItems.length" type="info" size="small">
            {{ bisItems.length }} 件装备
          </el-tag>
        </div>
      </template>

      <div v-if="!selectedClass || !selectedSpec || !selectedPhase" class="empty-container">
        <el-empty description="请先选择职业、天赋和阶段" />
      </div>

      <div v-else class="bis-grid">
        <div v-for="item in bisItems" :key="item.id" class="bis-item-card" :class="getQualityClass(item.quality)">
          <div class="item-slot">{{ SlotNameMap[item.slot] || item.slot }}</div>
          <div class="item-icon-wrapper">
            <img v-if="item.icon_url" :src="item.icon_url" class="item-icon" />
            <div v-else class="item-icon-placeholder">
              <el-icon><QuestionFilled /></el-icon>
            </div>
          </div>
          <div class="item-info">
            <div class="item-name" :class="getQualityClass(item.quality)">{{ item.item_name || `物品 #${item.item_id}` }}</div>
            <div class="item-meta">
              <span v-if="item.item_level" class="item-level">装等 {{ item.item_level }}</span>
              <span v-if="item.source" class="item-source">{{ item.source }}</span>
            </div>
          </div>
        </div>
      </div>
    </el-card>

    <el-dialog v-model="showImportDialog" title="导入毕业装备到角色" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择角色">
          <el-select v-model="importCharacterId" placeholder="请选择角色" style="width: 100%" filterable>
            <el-option v-for="char in characters" :key="char.id" :label="`${char.name} - ${char.realm}`" :value="char.id">
              <div class="option-with-icon">
                <img :src="getClassIcon(char.wow_class)" class="option-icon" />
                <span>{{ char.name }} - {{ char.realm }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="导入说明">
          <div class="import-info">
            <p>将当前选择的毕业装备列表导入到角色的装备需求中。</p>
            <p>每个部位只导入排名第1的装备，已存在的装备会自动跳过。</p>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button type="primary" @click="importToCharacter" :loading="importing">
          确认导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { TrophyBase, Download, QuestionFilled } from '@element-plus/icons-vue'
import { bisApi, characterApi } from '@/api'
import { BisClassNameMap, SlotNameMap, PhaseNameMap, SpecNameMap } from '@/types'
import type { BiSItem, BiSClasses, Character } from '@/types'
import { getClassIcon } from '@/utils/classIcons'

const loading = ref(false)
const importing = ref(false)
const bisClasses = ref<BiSClasses>({})
const bisItems = ref<BiSItem[]>([])
const characters = ref<Character[]>([])

const selectedClass = ref('')
const selectedSpec = ref('')
const selectedPhase = ref('')

const showImportDialog = ref(false)
const importCharacterId = ref('')

const specs = computed(() => {
  if (!selectedClass.value || !bisClasses.value[selectedClass.value]) return []
  return Object.keys(bisClasses.value[selectedClass.value])
})

const phases = computed(() => {
  if (!selectedClass.value || !selectedSpec.value) return []
  const raw = bisClasses.value[selectedClass.value]?.[selectedSpec.value] || []
  return [...raw].sort((a, b) => {
    const numA = parseInt(a.replace('P', ''))
    const numB = parseInt(b.replace('P', ''))
    if (isNaN(numA) && isNaN(numB)) return 0
    if (isNaN(numA)) return -1
    if (isNaN(numB)) return 1
    return numA - numB
  })
})

function getQualityClass(quality: string | null): string {
  const map: Record<string, string> = {
    'legendary': 'quality-legendary',
    'epic': 'quality-epic',
    'rare': 'quality-rare',
    'uncommon': 'quality-uncommon',
    'common': 'quality-common'
  }
  return map[quality || ''] || ''
}

function onClassChange() {
  selectedSpec.value = ''
  selectedPhase.value = ''
  bisItems.value = []
  if (specs.value.length === 1) {
    selectedSpec.value = specs.value[0]
    onSpecChange()
  }
}

function onSpecChange() {
  selectedPhase.value = ''
  bisItems.value = []
  if (phases.value.length === 1) {
    selectedPhase.value = phases.value[0]
    loadBisList()
  }
}

async function loadBisList() {
  if (!selectedClass.value || !selectedSpec.value || !selectedPhase.value) return
  loading.value = true
  try {
    const data = await bisApi.getBisList({
      class_name: selectedClass.value,
      spec_name: selectedSpec.value,
      phase: selectedPhase.value,
      max_rank: 1
    })
    bisItems.value = data
  } catch {
    bisItems.value = []
    ElMessage.error('加载毕业装备列表失败')
  } finally {
    loading.value = false
  }
}

async function importToCharacter() {
  if (!importCharacterId.value) {
    ElMessage.warning('请选择角色')
    return
  }
  importing.value = true
  try {
    const result = await bisApi.importToNeeds(Number(importCharacterId.value), {
      class_name: selectedClass.value,
      spec_name: selectedSpec.value,
      phase: selectedPhase.value,
      max_rank: 1
    })
    ElMessage.success(result.message || '导入成功')
    showImportDialog.value = false
    importCharacterId.value = ''
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(async () => {
  try {
    const [classesData, charsData] = await Promise.all([
      bisApi.getClasses(),
      characterApi.getAll()
    ])
    bisClasses.value = classesData
    characters.value = charsData
  } catch {
    ElMessage.error('加载数据失败')
  }
})
</script>

<style scoped>
.bis-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
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
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.bis-card {
  min-height: 400px;
  border: 1px solid rgba(55, 65, 81, 0.4);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.empty-container {
  padding: 60px 20px;
  text-align: center;
}

.bis-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 12px;
}

.bis-item-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: rgba(31, 41, 55, 0.55);
  border: 1px solid rgba(55, 65, 81, 0.4);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.04);
  transition: all 0.2s;
}

.bis-item-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.bis-item-card.quality-legendary { border-color: #ff8000; }
.bis-item-card.quality-epic { border-color: #a335ee; }
.bis-item-card.quality-rare { border-color: #0070dd; }
.bis-item-card.quality-uncommon { border-color: #1eff00; }
.bis-item-card.quality-common { border-color: #9d9d9d; }

.item-slot {
  writing-mode: vertical-lr;
  font-size: 11px;
  color: #6b7280;
  padding: 4px 2px;
  background: #172033;
  border-radius: 4px;
  text-align: center;
  letter-spacing: 2px;
}

.item-icon-wrapper {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  border-radius: 6px;
  overflow: hidden;
  background: #111827;
  display: flex;
  align-items: center;
  justify-content: center;
}

.item-icon {
  width: 48px;
  height: 48px;
  object-fit: cover;
}

.item-icon-placeholder {
  font-size: 20px;
  color: #4b5563;
}

.item-info {
  flex: 1;
  min-width: 0;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-name.quality-legendary { color: #ff8000; }
.item-name.quality-epic { color: #a335ee; }
.item-name.quality-rare { color: #0070dd; }
.item-name.quality-uncommon { color: #1eff00; }
.item-name.quality-common { color: #9d9d9d; }

.item-meta {
  display: flex;
  gap: 8px;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.item-source {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.option-with-icon {
  display: flex;
  align-items: center;
  gap: 8px;
}

.option-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
  object-fit: cover;
}

.import-info {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
}

.import-info p {
  margin: 4px 0;
}
</style>