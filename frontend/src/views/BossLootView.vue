<template>
  <div class="boss-loot-view">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/dungeons' }">副本管理</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: `/dungeons/${dungeonId}/bosses` }">{{ dungeonName }}</el-breadcrumb-item>
      <el-breadcrumb-item>{{ bossName }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="page-header">
      <h2 class="page-title">{{ bossName }} - 掉落装备</h2>
      <span class="loot-count">共 {{ lootItems.length }} 件装备</span>
    </div>

    <!-- 装备列表 -->
    <el-card v-loading="loading" class="loot-card">
      <el-table :data="lootItems" stripe style="width: 100%">
        <el-table-column label="装备名称" min-width="250">
          <template #default="{ row }">
            <span class="item-name" :class="getQualityClass(row.quality)">
              {{ row.item_name || `物品#${row.item_id}` }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="品质" width="100">
          <template #default="{ row }">
            <el-tag :type="getQualityTagType(row.quality)" size="small">
              {{ getQualityName(row.quality) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="物品等级" width="100">
          <template #default="{ row }">
            {{ row.item_level || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="部位" width="120">
          <template #default="{ row }">
            {{ getSlotName(row.slot) }}
          </template>
        </el-table-column>
        <el-table-column label="物品ID" width="100" prop="item_id" />
      </el-table>
    </el-card>

    <el-empty v-if="!loading && lootItems.length === 0" description="暂无掉落数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { bossApi } from '@/api'
import { ElMessage } from 'element-plus'

const route = useRoute()

const bossId = Number(route.params.bossId)
const dungeonId = ref(0)
const dungeonName = ref('')
const bossName = ref('')
const lootItems = ref<any[]>([])
const loading = ref(false)

function getQualityClass(quality: string): string {
  const classes: Record<string, string> = {
    poor: 'q-poor', common: 'q-common', uncommon: 'q-uncommon',
    rare: 'q-rare', epic: 'q-epic', legendary: 'q-legendary'
  }
  return classes[quality] || 'q-common'
}

function getQualityName(quality: string): string {
  const names: Record<string, string> = {
    poor: '垃圾', common: '普通', uncommon: '优秀',
    rare: '精良', epic: '史诗', legendary: '传说'
  }
  return names[quality] || quality || '普通'
}

function getQualityTagType(quality: string): string {
  const types: Record<string, string> = {
    poor: 'info', common: '', uncommon: 'success',
    rare: '', epic: 'danger', legendary: 'warning'
  }
  return types[quality] || ''
}

function getSlotName(slot: string | null): string {
  if (!slot) return '-'
  const names: Record<string, string> = {
    head: '头部', neck: '颈部', shoulder: '肩部', back: '背部',
    chest: '胸部', wrist: '手腕', hands: '手', waist: '腰部',
    legs: '腿部', feet: '脚', finger: '手指', trinket: '饰品',
    mainhand: '主手', offhand: '副手', twohand: '双手',
    ranged: '远程', relic: '圣物'
  }
  return names[slot] || slot
}

async function loadLoot() {
  loading.value = true
  try {
    const [lootRes, bossRes] = await Promise.all([
      bossApi.getBossLoot(bossId),
      bossApi.lookupByBossId(bossId).catch(() => null)
    ])
    lootItems.value = lootRes.data

    if (bossRes?.data) {
      bossName.value = bossRes.data.name
      dungeonName.value = bossRes.data.dungeon_name
      dungeonId.value = bossRes.data.dungeon_id
    } else {
      bossName.value = `Boss #${bossId}`
    }
  } catch (error) {
    ElMessage.error('加载掉落列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadLoot() })
</script>

<style scoped>
.boss-loot-view {
  max-width: 1400px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.loot-count {
  font-size: 14px;
  color: #6b7280;
}

.loot-card {
  min-height: 400px;
  border: 1px solid #374151;
}

/* WoW 品质颜色 */
.item-name {
  font-weight: 600;
}

.q-poor { color: #9d9d9d; }
.q-common { color: #e5e7eb; }
.q-uncommon { color: #1eff00; }
.q-rare { color: #4d9dff; }
.q-epic { color: #c875ff; }
.q-legendary { color: #ff8000; }
</style>
