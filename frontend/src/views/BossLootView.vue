<template>
  <div class="boss-loot-view">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/dungeons' }">副本管理</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: `/dungeons/${dungeonId}/bosses` }">{{ dungeonName }}</el-breadcrumb-item>
      <el-breadcrumb-item>{{ bossName }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="page-header">
      <div class="boss-header">
        <div class="boss-icon-container">
          <img v-if="bossIcon" :src="bossIcon" :alt="bossName" class="boss-icon" />
          <span v-else class="boss-icon-placeholder">👹</span>
        </div>
        <h2 class="page-title">{{ bossName }} - 掉落装备</h2>
      </div>
      <span class="loot-count">共 {{ lootItems.length }} 件装备</span>
    </div>

    <!-- 装备卡片列表 -->
    <div v-loading="loading" class="loot-grid">
      <div 
        v-for="item in lootItems" 
        :key="item.item_id" 
        class="item-card"
        :class="getQualityClass(item.quality)"
        @click="showItemDetail(item)"
      >
        <!-- 装备图标 -->
        <div class="item-icon-wrapper">
          <img 
            v-if="item.icon_url" 
            :src="item.icon_url" 
            :alt="item.item_name" 
            class="item-icon"
          />
          <span v-else class="item-icon-placeholder">📦</span>
        </div>
        
        <!-- 装备名称和品质 -->
        <div class="item-info">
          <h3 class="item-name">{{ item.item_name || `物品#${item.item_id}` }}</h3>
          <div class="item-meta">
            <el-tag :type="getQualityTagType(item.quality)" size="small" class="quality-tag">
              {{ getQualityName(item.quality) }}
            </el-tag>
            <span class="item-level">Lv.{{ item.item_level || '-' }}</span>
          </div>
        </div>
        
        <!-- 装备部位 -->
        <div class="item-slot">
          {{ getSlotName(item.slot) }}
        </div>
        
        <!-- 装备属性 -->
        <div v-if="item.stats && Object.keys(item.stats).length > 0" class="item-stats">
          <div 
            v-for="(value, stat) in item.stats" 
            :key="stat" 
            class="stat-item"
          >
            <span class="stat-name">{{ getStatName(stat) }}</span>
            <span class="stat-value">+{{ value }}</span>
          </div>
        </div>
        
        <!-- 物品ID -->
        <div class="item-footer">
          <span class="item-id">#{{ item.item_id }}</span>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && lootItems.length === 0" description="暂无掉落数据" />

    <!-- 装备详情弹窗 -->
    <el-dialog 
      v-model="showDetailDialog" 
      :title="selectedItem?.item_name || '装备详情'"
      width="400px"
    >
      <div v-if="selectedItem" class="item-detail">
        <div class="detail-header">
          <div class="detail-icon-wrapper" :class="getQualityClass(selectedItem.quality)">
            <img 
              v-if="selectedItem.icon_url" 
              :src="selectedItem.icon_url" 
              :alt="selectedItem.item_name" 
              class="detail-icon"
            />
            <span v-else class="detail-icon-placeholder">📦</span>
          </div>
          <div class="detail-info">
            <h3 class="detail-name" :class="getQualityClass(selectedItem.quality)">
              {{ selectedItem.item_name }}
            </h3>
            <div class="detail-meta">
              <el-tag :type="getQualityTagType(selectedItem.quality)" size="small">
                {{ getQualityName(selectedItem.quality) }}
              </el-tag>
              <span class="detail-ilvl">物品等级 {{ selectedItem.item_level || '-' }}</span>
              <span class="detail-slot">{{ getSlotName(selectedItem.slot) }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-stats">
          <h4>属性</h4>
          <div v-if="selectedItem.stats && Object.keys(selectedItem.stats).length > 0" class="stats-grid">
            <div 
              v-for="(value, stat) in selectedItem.stats" 
              :key="stat" 
              class="stat-row"
            >
              <span class="stat-label">{{ getStatName(stat) }}</span>
              <span class="stat-val">+{{ value }}</span>
            </div>
          </div>
          <p v-else class="no-stats">暂无属性数据</p>
        </div>
        
        <div class="detail-footer">
          <span class="detail-id">物品ID: {{ selectedItem.item_id }}</span>
        </div>
      </div>
    </el-dialog>
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
const bossIcon = ref('')
const lootItems = ref<any[]>([])
const loading = ref(false)
const showDetailDialog = ref(false)
const selectedItem = ref<any>(null)

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
    rare: 'primary', epic: 'danger', legendary: 'warning'
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

function getStatName(stat: string): string {
  const names: Record<string, string> = {
    strength: '力量', agility: '敏捷', intellect: '智力',
    stamina: '耐力', spirit: '精神',
    attack_power: '攻击强度', spell_power: '法术强度',
    haste: '急速', crit: '暴击', mastery: '精通',
    versatility: '全能', hit: '命中', expertise: '精准',
    dodge: '躲闪', parry: '招架', block: '格挡',
    armor: '护甲', health: '生命值', mana: '法力值'
  }
  return names[stat] || stat
}

function showItemDetail(item: any) {
  selectedItem.value = item
  showDetailDialog.value = true
}

async function loadLoot() {
  loading.value = true
  try {
    const [lootData, bossData] = await Promise.all([
      bossApi.getBossLoot(bossId),
      bossApi.lookupByBossId(bossId).catch(() => null)
    ])

    // axios 拦截器已解包 response.data
    // lootData 直接是数组（后端已通过 LEFT JOIN items 获取了物品详情）
    const loot: any[] = Array.isArray(lootData) ? lootData : []
    lootItems.value = loot

    if (bossData) {
      const boss: any = bossData
      bossName.value = boss.name || `Boss #${bossId}`
      dungeonName.value = boss.dungeon_name || ''
      dungeonId.value = boss.dungeon_id || 0
      bossIcon.value = boss.icon_url || ''
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
  margin-bottom: 24px;
}

.boss-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.boss-icon-container {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3f1f1f 0%, #1f1f2e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.boss-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.boss-icon-placeholder {
  font-size: 32px;
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

/* 装备卡片网格 */
.loot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

/* 装备卡片 */
.item-card {
  background: linear-gradient(145deg, #1f2937 0%, #111827 100%);
  border-radius: 12px;
  padding: 16px;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.item-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3);
}

/* 品质边框 */
.q-poor { border-color: #9d9d9d; }
.q-common { border-color: #374151; }
.q-uncommon { border-color: #1eff00; }
.q-rare { border-color: #4d9dff; }
.q-epic { border-color: #c875ff; }
.q-legendary { border-color: #ff8000; }

/* 装备图标 */
.item-icon-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 8px;
  background: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  overflow: hidden;
}

.item-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-icon-placeholder {
  font-size: 32px;
}

/* 装备信息 */
.item-info {
  margin-bottom: 8px;
}

.item-name {
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #e5e7eb;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.quality-tag {
  font-size: 11px;
}

.item-level {
  font-size: 12px;
  color: #6b7280;
}

/* 装备部位 */
.item-slot {
  font-size: 12px;
  color: #9ca3af;
  margin-bottom: 12px;
  padding: 4px 8px;
  background: rgba(55, 65, 81, 0.5);
  border-radius: 4px;
  display: inline-block;
}

/* 装备属性 */
.item-stats {
  margin-bottom: 12px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
  font-size: 12px;
}

.stat-name {
  color: #9ca3af;
}

.stat-value {
  color: #4ade80;
  font-weight: 500;
}

/* 装备底部 */
.item-footer {
  border-top: 1px solid #374151;
  padding-top: 8px;
}

.item-id {
  font-size: 11px;
  color: #6b7280;
}

/* 装备品质颜色 */
.q-poor .item-name { color: #9d9d9d; }
.q-common .item-name { color: #e5e7eb; }
.q-uncommon .item-name { color: #1eff00; }
.q-rare .item-name { color: #4d9dff; }
.q-epic .item-name { color: #c875ff; }
.q-legendary .item-name { color: #ff8000; }

/* 详情弹窗 */
.item-detail {
  padding: 16px;
}

.detail-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.detail-icon-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  background: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 3px solid;
}

.detail-icon {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.detail-icon-placeholder {
  font-size: 40px;
}

.detail-info {
  flex: 1;
}

.detail-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.detail-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.detail-ilvl,
.detail-slot {
  font-size: 13px;
  color: #9ca3af;
  padding: 4px 8px;
  background: rgba(55, 65, 81, 0.5);
  border-radius: 4px;
}

.detail-stats {
  margin-bottom: 16px;
}

.detail-stats h4 {
  font-size: 14px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0 0 12px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 10px;
  background: rgba(55, 65, 81, 0.5);
  border-radius: 6px;
}

.stat-label {
  font-size: 13px;
  color: #9ca3af;
}

.stat-val {
  font-size: 13px;
  color: #4ade80;
  font-weight: 500;
}

.no-stats {
  color: #6b7280;
  font-size: 13px;
  text-align: center;
  padding: 16px;
}

.detail-footer {
  border-top: 1px solid #374151;
  padding-top: 12px;
}

.detail-id {
  font-size: 12px;
  color: #6b7280;
}

/* 详情弹窗品质边框 */
.detail-icon-wrapper.q-poor { border-color: #9d9d9d; }
.detail-icon-wrapper.q-common { border-color: #374151; }
.detail-icon-wrapper.q-uncommon { border-color: #1eff00; }
.detail-icon-wrapper.q-rare { border-color: #4d9dff; }
.detail-icon-wrapper.q-epic { border-color: #c875ff; }
.detail-icon-wrapper.q-legendary { border-color: #ff8000; }

.detail-name.q-poor { color: #9d9d9d; }
.detail-name.q-common { color: #e5e7eb; }
.detail-name.q-uncommon { color: #1eff00; }
.detail-name.q-rare { color: #4d9dff; }
.detail-name.q-epic { color: #c875ff; }
.detail-name.q-legendary { color: #ff8000; }
</style>
