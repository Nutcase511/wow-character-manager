<template>
  <div class="dungeons-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Grid /></el-icon>
        副本管理
      </h2>
      <div class="header-actions">
        <el-button type="success" @click="handleImportAtlasLoot" :loading="importing">
          <el-icon><Upload /></el-icon>
          从 AtlasLoot 导入
        </el-button>
      </div>
    </div>

    <!-- 阶段选择 -->
    <div class="phase-bar">
      <span class="phase-label">阶段:</span>
      <el-select v-model="activePhase" placeholder="选择阶段" @change="handlePhaseChange">
        <el-option label="五人本" value="dungeon" />
        <el-option label="P1" value="P1" />
        <el-option label="P2" value="P2" />
        <el-option label="P3" value="P3" />
        <el-option label="P4" value="P4" />
        <el-option label="P5" value="P5" />
        <el-option label="P6" value="P6" />
        <el-option label="P7" value="P7" />
        <el-option label="P8" value="P8" />
        <el-option label="P9" value="P9" />
        <el-option label="P10" value="P10" />
        <el-option label="P11" value="P11" />
      </el-select>
    </div>

    <!-- 五人本区域 -->
    <div v-if="!activePhase || activePhase === 'dungeon'" class="dungeon-section">
      <div class="section-header">
        <h3>
          <el-icon><Building /></el-icon>
          五人本
        </h3>
        <span class="section-count">{{ dungeonList.length }} 个</span>
      </div>
      <div v-if="dungeonList.length > 0" class="dungeon-grid dungeon-grid-sm">
        <el-card
          v-for="dungeon in dungeonList"
          :key="dungeon.id"
          class="dungeon-card dungeon-card-sm"
          shadow="hover"
          @click="goToBosses(dungeon)"
        >
          <div class="card-content">
            <div class="card-icon" :class="getCategoryClass(dungeon.category)">
              {{ getCategoryIcon(dungeon.category) }}
            </div>
            <div class="card-info">
              <h3 class="card-name">{{ dungeon.name }}</h3>
              <div class="card-meta">
                <el-tag :type="getCategoryTagType(dungeon.category)" size="small">
                  {{ getCategoryName(dungeon.category) }}
                </el-tag>
                <span class="card-level">Lv.{{ dungeon.minimum_level }}</span>
              </div>
            </div>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="暂无五人本数据" />
    </div>

    <!-- 团本区域 -->
    <div v-if="!activePhase || activePhase !== 'dungeon'" class="dungeon-section">
      <div class="section-header">
        <h3>
          <el-icon><Trophy /></el-icon>
          团队副本
        </h3>
        <span class="section-count">{{ raidList.length }} 个</span>
      </div>

      <div v-if="raidList.length > 0" class="dungeon-grid">
        <el-card
          v-for="dungeon in raidList"
          :key="dungeon.id"
          class="dungeon-card"
          shadow="hover"
          @click="goToBosses(dungeon)"
        >
          <div class="card-content">
            <div class="card-icon" :class="getCategoryClass(dungeon.category)">
              {{ getCategoryIcon(dungeon.category) }}
            </div>
            <div class="card-info">
              <h3 class="card-name">{{ dungeon.name }}</h3>
              <div class="card-meta">
                <el-tag :type="getPhaseTagType(dungeon.phase)" class="phase-tag-sm">
                  {{ dungeon.phase }}
                </el-tag>
                <el-tag :type="getCategoryTagType(dungeon.category)" size="small">
                  {{ getCategoryName(dungeon.category) }}
                </el-tag>
                <span class="card-level">Lv.{{ dungeon.minimum_level }}</span>
              </div>
              <div class="card-modes">
                <span
                  v-for="mode in dungeon.modes"
                  :key="mode"
                  class="mode-tag"
                >{{ getModeDisplayName(mode) }}</span>
              </div>
            </div>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="暂无团本数据" />
    </div>

    <!-- 世界Boss区域 -->
    <div v-if="!activePhase || activePhase !== 'dungeon'" class="dungeon-section">
      <div class="section-header">
        <h3>
          <el-icon><Skull /></el-icon>
          世界Boss
        </h3>
        <span class="section-count">{{ worldBossList.length }} 个</span>
      </div>
      <div v-if="worldBossList.length > 0" class="dungeon-grid dungeon-grid-sm">
        <el-card
          v-for="dungeon in worldBossList"
          :key="dungeon.id"
          class="dungeon-card dungeon-card-sm"
          shadow="hover"
          @click="goToBosses(dungeon)"
        >
          <div class="card-content">
            <div class="card-icon" :class="getCategoryClass(dungeon.category)">
              {{ getCategoryIcon(dungeon.category) }}
            </div>
            <div class="card-info">
              <h3 class="card-name">{{ dungeon.name }}</h3>
              <div class="card-meta">
                <el-tag :type="getCategoryTagType(dungeon.category)" size="small">
                  {{ getCategoryName(dungeon.category) }}
                </el-tag>
                <span class="card-level">Lv.{{ dungeon.minimum_level }}</span>
              </div>
            </div>
            <el-icon class="card-arrow"><ArrowRight /></el-icon>
          </div>
        </el-card>
      </div>
      <el-empty v-else description="暂无世界Boss数据" />
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dungeonApi } from '@/api'
import { ElMessage } from 'element-plus'

import type { Dungeon } from '@/types'

const router = useRouter()

// 筛选状态
const activePhase = ref('P3')

// 数据状态
const dungeons = ref<Dungeon[]>([])
const loading = ref(false)
const importing = ref(false)

// 阶段标题映射
function getPhaseTitle(phase: string): string {
  const titles: Record<string, string> = {
    'P1': '第一阶段',
    'P2': '第二阶段',
    'P3': '第三阶段',
    'P4': '第四阶段',
    'P5': '第五阶段',
    'P6': '第六阶段',
    'P7': '第七阶段',
    'P8': '第八阶段',
    'P9': '第九阶段',
    'P10': '第十阶段',
    'P11': '第十一阶段',
  }
  return titles[phase] || phase
}

// 阶段标签类型
function getPhaseTagType(phase: string): string {
  const types: Record<string, string> = {
    'P1': 'success',
    'P2': 'success',
    'P3': 'primary',
    'P4': 'primary',
    'P5': 'warning',
    'P6': 'warning',
    'P7': 'warning',
    'P8': 'danger',
    'P9': 'info',
    'P10': 'info',
    'P11': 'danger',
  }
  return types[phase] || 'default'
}

// 显示名称映射
function getModeDisplayName(mode: string): string {
  const names: Record<string, string> = {
    normal: '普通', heroic: '英雄', '10': '10人', '25': '25人', '10h': '10H', '25h': '25H'
  }
  return names[mode] || mode
}

function getCategoryName(cat: string): string {
  const names: Record<string, string> = { dungeon: '五人本', raid: '团本', worldboss: '世界Boss' }
  return names[cat] || cat
}

function getCategoryIcon(cat: string): string {
  const icons: Record<string, string> = { dungeon: '🏰', raid: '👑', worldboss: '💀' }
  return icons[cat] || '📦'
}

function getCategoryClass(cat: string): string {
  const classes: Record<string, string> = { dungeon: 'icon-dungeon', raid: 'icon-raid', worldboss: 'icon-worldboss' }
  return classes[cat] || ''
}

function getCategoryTagType(cat: string): string {
  const types: Record<string, string> = { dungeon: 'primary', raid: 'success', worldboss: 'danger' }
  return types[cat] || 'default'
}

// 筛选后的列表
const dungeonList = computed(() => {
  return dungeons.value.filter(d => d.category === 'dungeon')
})

const raidList = computed(() => {
  return dungeons.value.filter(d => d.category === 'raid')
})

const worldBossList = computed(() => {
  return dungeons.value.filter(d => d.category === 'worldboss')
})



async function loadDungeons() {
  loading.value = true
  try {
    const params: Record<string, string> = {}
    if (activePhase.value === 'dungeon') {
      params.category = 'dungeon'
    } else if (activePhase.value) {
      params.phase = activePhase.value
    }
    const data = await dungeonApi.getAll(params)
    dungeons.value = data
  } catch (error) {
    ElMessage.error('加载副本失败')
  } finally {
    loading.value = false
  }
}

function goToBosses(dungeon: Dungeon) {
  router.push(`/dungeons/${dungeon.dungeon_id}/bosses`)
}

function handlePhaseChange() {
  loadDungeons()
}

async function handleImportAtlasLoot() {
  importing.value = true
  try {
    const data = await dungeonApi.importAtlasLoot()
    ElMessage.success(`成功导入 ${data.stats?.instances || 0} 个副本`)
    loadDungeons()
  } catch (error) {
    ElMessage.error('导入失败')
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadDungeons()
})
</script>

<style lang="scss" scoped>
.dungeons-view {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .page-title {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .header-actions {
    display: flex;
    gap: 10px;
  }
}

.phase-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
  
  .phase-label {
    font-weight: 500;
    color: #666;
  }
  
  :deep(.el-select) {
    width: 160px;
  }
}

.dungeon-section {
  margin-bottom: 30px;
  
  .section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 2px solid #eee;
    
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      font-size: 18px;
      font-weight: 600;
    }
    
    .section-count {
      color: #999;
      font-size: 14px;
    }
  }
}

.phase-group {
  margin-bottom: 25px;
  
  .phase-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
    
    .phase-tag {
      font-weight: bold;
    }
    
    .phase-title {
      font-weight: 600;
      font-size: 15px;
    }
    
    .phase-count {
      color: #999;
      font-size: 13px;
      margin-left: auto;
    }
  }
}

.dungeon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 15px;
  
  &.dungeon-grid-sm {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
}

.dungeon-card {
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  }
  
  &.dungeon-card-sm {
    .card-content {
      padding: 12px 15px;
    }
    
    .card-icon {
      width: 40px;
      height: 40px;
      font-size: 20px;
    }
    
    .card-name {
      font-size: 15px;
    }
    
    .card-meta {
      flex-wrap: wrap;
    }
  }
  
  .card-content {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 15px;
  }
  
  .card-icon {
    width: 50px;
    height: 50px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
    
    &.icon-dungeon {
      background: linear-gradient(135deg, #409eff, #667eea);
    }
    
    &.icon-raid {
      background: linear-gradient(135deg, #67c23a, #85ce61);
    }
    
    &.icon-worldboss {
      background: linear-gradient(135deg, #f56c6c, #f87171);
    }
  }
  
  .card-info {
    flex: 1;
    min-width: 0;
    
    .card-name {
      margin: 0 0 8px 0;
      font-size: 16px;
      font-weight: 600;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .card-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 6px;
      
      .card-level {
        font-size: 13px;
        color: #999;
      }
    }
    
    .card-modes {
      display: flex;
      gap: 6px;
      
      .mode-tag {
        font-size: 12px;
        padding: 2px 6px;
        background: #f5f7fa;
        border-radius: 4px;
        color: #666;
      }
    }
  }
  
  .card-arrow {
    color: #ccc;
    font-size: 18px;
    transition: color 0.3s;
  }
  
  &:hover .card-arrow {
    color: #409eff;
  }
}
</style>