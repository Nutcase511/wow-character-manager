<template>
  <div class="character-detail-view">
    <div class="page-header">
      <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
      <div v-if="character" class="character-header-info">
        <img :src="getClassIcon(character.wow_class)" :alt="getClassDisplayName(character.wow_class)" class="class-icon-lg" />
        <h2 class="page-title">{{ character?.name }} - 角色详情</h2>
        <img :src="getFactionIcon(character.faction)" :alt="character.faction" class="faction-icon-lg" />
      </div>
      <h2 v-else class="page-title">角色详情</h2>
      <div class="header-actions">
        <el-button type="primary" @click="showAddNeedDialog = true">
          <el-icon><Plus /></el-icon>
          添加装备需求
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="character" class="character-content">
      <!-- 金币信息 -->
      <el-card class="gold-card">
        <template #header>
          <div class="card-header">
            <span>金币信息</span>
            <el-button size="small" @click="loadGold" :loading="goldLoading" :icon="Refresh">
              刷新
            </el-button>
          </div>
        </template>
        <div v-if="goldLoading" class="gold-loading">
          <el-skeleton :rows="1" animated />
        </div>
        <div v-else-if="goldData?.character_gold" class="gold-content">
            <span class="gold-amount">{{ formatGold(goldData.character_gold.current_gold) }}</span>
        </div>
        <el-empty v-else description="暂无金币数据，请先在金币统计页面刷新同步" :image-size="60" />
      </el-card>

      <!-- 当前装备 - 魔兽风格布局 -->
      <el-card class="equipment-card">
        <template #header>
          <div class="card-header">
            <span>当前装备</span>
            <div class="header-actions">
              <el-tag v-if="averageItemLevel > 0" type="warning" size="small" effect="dark">
                平均装等 {{ averageItemLevel }}
              </el-tag>
              <el-button size="small" @click="loadEquipment" :loading="equipmentLoading" :icon="Refresh">
                刷新
              </el-button>
            </div>
          </div>
        </template>
        <div v-if="equipmentLoading" class="equipment-loading">
          <el-skeleton :rows="8" animated />
        </div>
        <div v-else-if="equipment.length > 0" class="equipment-paperdoll">
          <!-- 上部：左右装备栏 + 中间角色 -->
          <div class="equipment-paperdoll-top">
            <!-- 左侧装备栏 -->
            <div class="equipment-column left-column">
              <div 
                v-for="slot in leftSlots" 
                :key="slot.key"
                class="paperdoll-slot"
                :class="{ 'has-item': getItemBySlot(slot.key) }"
                :style="getItemBySlot(slot.key) ? { borderColor: getQualityColor(getItemBySlot(slot.key).quality) } : {}"
              >
                <template v-if="getItemBySlot(slot.key)">
                  <div class="slot-icon">
                    <img :src="getItemBySlot(slot.key).icon" :alt="getItemBySlot(slot.key).name" />
                  </div>
                  <div class="slot-info">
                    <div class="item-header">
                      <div class="item-name" :style="{ color: getQualityColor(getItemBySlot(slot.key).quality) }">
                        {{ getItemBySlot(slot.key).name }}
                      </div>
                      <div class="item-ilvl">ilvl {{ getItemBySlot(slot.key).itemLevel || '?' }}</div>
                    </div>
                    
                    <!-- 属性列表 -->
                    <div class="item-stats" v-if="getItemBySlot(slot.key).stats && getItemBySlot(slot.key).stats.length > 0">
                      <div v-for="stat in getItemBySlot(slot.key).stats.slice(0, 6)" :key="stat.type?.type || stat.type" class="stat-line">
                        <span class="stat-text" :class="{ 'bonus': stat.is_equip_bonus }">
                          {{ formatStatDisplay(stat) }}
                        </span>
                      </div>
                    </div>

                    <!-- 附魔 -->
                    <div v-if="getItemBySlot(slot.key).enchantments && getItemBySlot(slot.key).enchantments.length > 0" class="item-enchants">
                      <div v-for="ench in getItemBySlot(slot.key).enchantments" :key="ench.enchantment_id" class="enchant-line">
                        <span class="enchant-text">{{ ench.display_string }}</span>
                      </div>
                    </div>

                    <!-- 宝石插槽 -->
                    <div v-if="getItemBySlot(slot.key).sockets && getItemBySlot(slot.key).sockets.length > 0" class="item-sockets">
                      <div v-for="(socket, idx) in getItemBySlot(slot.key).sockets" :key="idx" class="socket-line">
                        <span class="socket-icon" :class="socket.type?.type || 'prismatic'">◆</span>
                        <span v-if="socket.item" class="socket-gem">{{ socket.item.name }}</span>
                        <span v-else class="socket-empty">{{ socket.type?.name || '多彩插槽' }}</span>
                      </div>
                    </div>

                    <!-- 套装信息 -->
                    <div v-if="getItemBySlot(slot.key).itemSetName" class="item-set">
                      {{ getItemBySlot(slot.key).itemSetName }}
                    </div>

                    <!-- 装备特效（饰品/武器等） -->
                    <div v-if="getItemBySlot(slot.key).spells && getItemBySlot(slot.key).spells.length > 0" class="item-spells">
                      <div v-for="spell in getItemBySlot(slot.key).spells" :key="spell.spell?.id || spell.description" class="spell-line">
                        <span class="spell-name" v-if="spell.spell?.name">{{ spell.spell.name }}:</span>
                        <span class="spell-description">{{ spell.description }}</span>
                      </div>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <div class="slot-empty">
                    <span class="slot-label">{{ slot.label }}</span>
                  </div>
                </template>
              </div>
            </div>

          <!-- 中间角色信息 -->
          <div class="equipment-center">
            <div class="character-avatar">
              <img :src="getClassIcon(character.wow_class)" :alt="getClassDisplayName(character.wow_class)" />
              <div class="character-level">{{ character.level }}</div>
            </div>
            <div class="character-meta">
              <div class="meta-row">
                <span class="meta-label">职业</span>
                <span class="meta-value" :style="{ color: getClassColor(character.wow_class) }">
                  {{ getClassDisplayName(character.wow_class) }}
                </span>
              </div>
              <div class="meta-row">
                <span class="meta-label">专精</span>
                <span class="meta-value">{{ character.spec || '-' }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">阵营</span>
                <span class="meta-value" :class="character.faction">
                  {{ character.faction === 'alliance' ? '联盟' : '部落' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 右侧装备栏 -->
          <div class="equipment-column right-column">
            <div 
              v-for="slot in rightSlots" 
              :key="slot.key"
              class="paperdoll-slot"
              :class="{ 'has-item': getItemBySlot(slot.key) }"
              :style="getItemBySlot(slot.key) ? { borderColor: getQualityColor(getItemBySlot(slot.key).quality) } : {}"
            >
              <template v-if="getItemBySlot(slot.key)">
                <div class="slot-icon">
                  <img :src="getItemBySlot(slot.key).icon" :alt="getItemBySlot(slot.key).name" />
                </div>
                <div class="slot-info">
                  <div class="item-header">
                    <div class="item-name" :style="{ color: getQualityColor(getItemBySlot(slot.key).quality) }">
                      {{ getItemBySlot(slot.key).name }}
                    </div>
                    <div class="item-ilvl">ilvl {{ getItemBySlot(slot.key).itemLevel || '?' }}</div>
                  </div>
                  
                  <!-- 属性列表 -->
                  <div class="item-stats" v-if="getItemBySlot(slot.key).stats && getItemBySlot(slot.key).stats.length > 0">
                    <div v-for="stat in getItemBySlot(slot.key).stats.slice(0, 6)" :key="stat.type?.type || stat.type" class="stat-line">
                      <span class="stat-text" :class="{ 'bonus': stat.is_equip_bonus }">
                        {{ formatStatDisplay(stat) }}
                      </span>
                    </div>
                  </div>

                  <!-- 附魔 -->
                  <div v-if="getItemBySlot(slot.key).enchantments && getItemBySlot(slot.key).enchantments.length > 0" class="item-enchants">
                    <div v-for="ench in getItemBySlot(slot.key).enchantments" :key="ench.enchantment_id" class="enchant-line">
                      <span class="enchant-text">{{ ench.display_string }}</span>
                    </div>
                  </div>

                  <!-- 宝石插槽 -->
                  <div v-if="getItemBySlot(slot.key).sockets && getItemBySlot(slot.key).sockets.length > 0" class="item-sockets">
                    <div v-for="(socket, idx) in getItemBySlot(slot.key).sockets" :key="idx" class="socket-line">
                      <span class="socket-icon" :class="socket.type?.type || 'prismatic'">◆</span>
                      <span v-if="socket.item" class="socket-gem">{{ socket.item.name }}</span>
                      <span v-else class="socket-empty">{{ socket.type?.name || '多彩插槽' }}</span>
                    </div>
                  </div>

                  <!-- 套装信息 -->
                  <div v-if="getItemBySlot(slot.key).itemSetName" class="item-set">
                    {{ getItemBySlot(slot.key).itemSetName }}
                  </div>

                  <!-- 装备特效（饰品/武器等） -->
                  <div v-if="getItemBySlot(slot.key).spells && getItemBySlot(slot.key).spells.length > 0" class="item-spells">
                    <div v-for="spell in getItemBySlot(slot.key).spells" :key="spell.spell?.id || spell.description" class="spell-line">
                      <span class="spell-name" v-if="spell.spell?.name">{{ spell.spell.name }}:</span>
                      <span class="spell-description">{{ spell.description }}</span>
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="slot-empty">
                  <span class="slot-label">{{ slot.label }}</span>
                </div>
              </template>
            </div>
          </div>
          </div>
          
          <!-- 底部武器栏 -->
          <div class="equipment-weapons-row">
            <div 
              v-for="slot in weaponSlots" 
              :key="slot.key"
              class="paperdoll-slot weapon-slot"
              :class="{ 'has-item': getItemBySlot(slot.key) }"
              :style="getItemBySlot(slot.key) ? { borderColor: getQualityColor(getItemBySlot(slot.key).quality) } : {}"
            >
              <template v-if="getItemBySlot(slot.key)">
                <div class="slot-icon">
                  <img :src="getItemBySlot(slot.key).icon" :alt="getItemBySlot(slot.key).name" />
                </div>
                <div class="slot-info">
                  <div class="item-header">
                    <div class="item-name" :style="{ color: getQualityColor(getItemBySlot(slot.key).quality) }">
                      {{ getItemBySlot(slot.key).name }}
                    </div>
                    <div class="item-ilvl">ilvl {{ getItemBySlot(slot.key).itemLevel || '?' }}</div>
                  </div>
                  
                  <!-- 属性列表 -->
                  <div class="item-stats" v-if="getItemBySlot(slot.key).stats && getItemBySlot(slot.key).stats.length > 0">
                    <div v-for="stat in getItemBySlot(slot.key).stats.slice(0, 6)" :key="stat.type?.type || stat.type" class="stat-line">
                      <span class="stat-text" :class="{ 'bonus': stat.is_equip_bonus }">
                        {{ formatStatDisplay(stat) }}
                      </span>
                    </div>
                  </div>

                  <!-- 附魔 -->
                  <div v-if="getItemBySlot(slot.key).enchantments && getItemBySlot(slot.key).enchantments.length > 0" class="item-enchants">
                    <div v-for="ench in getItemBySlot(slot.key).enchantments" :key="ench.enchantment_id" class="enchant-line">
                      <span class="enchant-text">{{ ench.display_string }}</span>
                    </div>
                  </div>

                  <!-- 宝石插槽 -->
                  <div v-if="getItemBySlot(slot.key).sockets && getItemBySlot(slot.key).sockets.length > 0" class="item-sockets">
                    <div v-for="(socket, idx) in getItemBySlot(slot.key).sockets" :key="idx" class="socket-line">
                      <span class="socket-icon" :class="socket.type?.type || 'prismatic'">◆</span>
                      <span v-if="socket.item" class="socket-gem">{{ socket.item.name }}</span>
                      <span v-else class="socket-empty">{{ socket.type?.name || '多彩插槽' }}</span>
                    </div>
                  </div>

                  <!-- 套装信息 -->
                  <div v-if="getItemBySlot(slot.key).itemSetName" class="item-set">
                    {{ getItemBySlot(slot.key).itemSetName }}
                  </div>

                  <!-- 装备特效（饰品/武器等） -->
                  <div v-if="getItemBySlot(slot.key).spells && getItemBySlot(slot.key).spells.length > 0" class="item-spells">
                    <div v-for="spell in getItemBySlot(slot.key).spells" :key="spell.spell?.id || spell.description" class="spell-line">
                      <span class="spell-name" v-if="spell.spell?.name">{{ spell.spell.name }}:</span>
                      <span class="spell-description">{{ spell.description }}</span>
                    </div>
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="slot-empty">
                  <span class="slot-label">{{ slot.label }}</span>
                </div>
              </template>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无装备数据" :image-size="60">
          <template #description>
            <p>暂无装备数据</p>
            <p class="equipment-hint">需要在游戏内登录角色后，通过暴雪 API 获取</p>
          </template>
        </el-empty>
      </el-card>

      <!-- 角色基本信息 -->
      <el-card class="character-info-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
            <el-tag :type="character.faction === 'alliance' ? 'primary' : 'danger'">
              {{ character.faction === 'alliance' ? '联盟' : '部落' }}
            </el-tag>
          </div>
        </template>
        <el-descriptions :column="3" border>
          <el-descriptions-item label="角色名">{{ character.name }}</el-descriptions-item>
          <el-descriptions-item label="服务器">{{ character.realm }}</el-descriptions-item>
          <el-descriptions-item label="等级">{{ character.level }}</el-descriptions-item>
          <el-descriptions-item label="职业">
            <el-tag :type="getClassTagType(character.wow_class)">
              {{ getClassDisplayName(character.wow_class) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="专精">{{ character.spec || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(character.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 装备进度 -->
      <el-card class="progress-card">
        <template #header>
          <div class="card-header">
            <span>装备获取进度</span>
            <el-tag v-if="progress" type="success">
              {{ progress.progress_percentage }}%
            </el-tag>
          </div>
        </template>
        <div v-if="progress" class="progress-content">
          <el-progress
            :percentage="progress.progress_percentage"
            :stroke-width="20"
            :text-inside="true"
            status="success"
          />
          <div class="progress-stats">
            <el-statistic title="总需求" :value="progress.total_needs" />
            <el-statistic title="已获取" :value="progress.obtained" />
            <el-statistic title="剩余" :value="progress.remaining" />
          </div>
        </div>
        <el-empty v-else description="暂无装备需求数据" />
      </el-card>

      <!-- 装备需求列表 -->
      <el-card class="item-needs-card">
        <template #header>
          <div class="card-header">
            <span>装备需求列表</span>
            <div class="header-filters">
              <el-radio-group v-model="filterStatus" size="small">
                <el-radio-button label="all">全部</el-radio-button>
                <el-radio-button label="pending">待获取</el-radio-button>
                <el-radio-button label="obtained">已获取</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>

        <el-table :data="filteredItemNeeds" v-loading="itemNeedStore.loading" style="width: 100%">
          <el-table-column prop="item_name" label="装备名称" min-width="150">
            <template #default="{ row }">
              <div class="item-name-cell">
                <span class="item-priority" :class="`priority-${row.priority}`">
                  {{ '★'.repeat(row.priority) }}
                </span>
                <span>{{ row.item_name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="dungeon_name" label="副本" min-width="120" />
          <el-table-column prop="boss_name" label="Boss" min-width="120" />
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <el-rate v-model="row.priority" disabled :max="5" />
            </template>
          </el-table-column>
          <el-table-column prop="obtained" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.obtained ? 'success' : 'info'" size="small">
                {{ row.obtained ? '已获取' : '待获取' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button 
                v-if="!row.obtained" 
                type="success" 
                size="small" 
                @click="markAsObtained(row.id)"
              >
                标记获取
              </el-button>
              <el-button type="primary" size="small" @click="editNeed(row)">
                编辑
              </el-button>
              <el-button type="danger" size="small" @click="deleteNeed(row.id)">
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="filteredItemNeeds.length === 0" description="暂无装备需求" />
      </el-card>
    </div>

    <div v-else class="empty-container">
      <el-empty description="角色不存在或已删除" />
      <el-button @click="goBack" type="primary" style="margin-top: 20px;">
        返回角色列表
      </el-button>
    </div>

    <!-- 添加/编辑装备需求对话框 -->
    <el-dialog
      v-model="showAddNeedDialog"
      :title="isEditingNeed ? '编辑装备需求' : '添加装备需求'"
      width="600px"
      @close="resetNeedForm"
    >
      <el-form :model="needForm" :rules="needRules" ref="needFormRef" label-width="100px">
        <el-form-item label="装备ID" prop="item_id">
          <el-input-number v-model="needForm.item_id" :min="1" placeholder="请输入装备ID" />
          <div class="form-tip">提示：可以在魔兽世界数据库网站查找装备ID</div>
        </el-form-item>
        <el-form-item label="装备名称" prop="item_name">
          <el-input v-model="needForm.item_name" placeholder="请输入装备名称" />
        </el-form-item>
        <el-form-item label="副本名称" prop="dungeon_name">
          <el-input v-model="needForm.dungeon_name" placeholder="请输入副本名称（可选）" />
        </el-form-item>
        <el-form-item label="Boss名称" prop="boss_name">
          <el-input v-model="needForm.boss_name" placeholder="请输入Boss名称（可选）" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-rate v-model="needForm.priority" :max="5" show-text />
        </el-form-item>
        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="needForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddNeedDialog = false">取消</el-button>
        <el-button type="primary" @click="submitNeedForm" :loading="itemNeedStore.loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCharacterStore } from '@/stores/character'
import { useItemNeedStore } from '@/stores/itemNeed'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, Refresh } from '@element-plus/icons-vue'
import { goldApi, equipmentApi, itemApi } from '@/api'
import type { ItemNeed, ItemNeedCreate, ItemProgress } from '@/types'
import { WoWClass } from '@/types'
import { getClassIcon, getFactionIcon } from '@/utils/classIcons'

const route = useRoute()
const router = useRouter()
const characterStore = useCharacterStore()
const itemNeedStore = useItemNeedStore()

// 状态
const loading = ref(true)
const character = ref<any>(null)
const progress = ref<ItemProgress | null>(null)
const itemNeeds = ref<ItemNeed[]>([])
const goldData = ref<any>(null)
const goldLoading = ref(false)

// 装备状态
const equipment = ref<any[]>([])
const equipmentLoading = ref(false)
const averageItemLevel = ref(0)

// 装备槽位定义（魔兽风格布局）
const leftSlots = [
  { key: '头部', label: '头部' },
  { key: '颈部', label: '颈部' },
  { key: '肩部', label: '肩部' },
  { key: '背部', label: '背部' },
  { key: '胸部', label: '胸部' },
  { key: '衬衣', label: '衬衣' },
  { key: '战袍', label: '战袍' },
  { key: '手腕', label: '手腕' },
]

const rightSlots = [
  { key: '手', label: '手' },
  { key: '腰部', label: '腰部' },
  { key: '腿部', label: '腿部' },
  { key: '脚', label: '脚' },
  { key: '戒指1', label: '戒指' },
  { key: '戒指2', label: '戒指' },
  { key: '饰品1', label: '饰品' },
  { key: '饰品2', label: '饰品' },
]

// 武器槽位
const weaponSlots = [
  { key: '主手', label: '主手' },
  { key: '副手', label: '副手' },
  { key: '远程', label: '远程' },
]

// 过滤器
const filterStatus = ref<'all' | 'pending' | 'obtained'>('all')

// 对话框状态
const showAddNeedDialog = ref(false)
const isEditingNeed = ref(false)
const editingNeedId = ref<string | null>(null)

// 装备需求表单
const needForm = reactive<ItemNeedCreate>({
  character_id: '',
  item_id: 0,
  item_name: '',
  boss_id: undefined,
  boss_name: '',
  dungeon_name: '',
  priority: 1,
  obtained: false,
  notes: ''
})

const needFormRef = ref()

// 表单验证规则
const needRules = {
  item_id: [{ required: true, message: '请输入装备ID', trigger: 'blur' }],
  item_name: [{ required: true, message: '请输入装备名称', trigger: 'blur' }],
}

// 计算属性
const filteredItemNeeds = computed(() => {
  let needs = itemNeeds.value
  if (filterStatus.value === 'pending') {
    needs = needs.filter(n => !n.obtained)
  } else if (filterStatus.value === 'obtained') {
    needs = needs.filter(n => n.obtained)
  }
  return needs
})

// 获取指定槽位的装备
function getItemBySlot(slotName: string) {
  return equipment.value.find(item => item.slot === slotName)
}

// 格式化属性显示（包含数值）
function formatStatDisplay(stat: any): string {
  const displayString = stat.display?.display_string || stat.display
  // 如果有 value 且 display_string 不包含数值，则追加
  if (stat.value !== undefined && stat.value !== null) {
    // 检查 display_string 是否已经包含数值
    const valueStr = String(stat.value)
    if (displayString && !displayString.includes(valueStr)) {
      return `${displayString} ${stat.value}`
    }
  }
  return displayString || ''
}

// 职业颜色映射
function getClassColor(classKey: string): string {
  const colors: Record<string, string> = {
    [WoWClass.WARRIOR]: '#C79C6E',
    [WoWClass.PALADIN]: '#F58CBA',
    [WoWClass.HUNTER]: '#ABD473',
    [WoWClass.ROGUE]: '#FFF569',
    [WoWClass.PRIEST]: '#FFFFFF',
    [WoWClass.DEATH_KNIGHT]: '#C41F3B',
    [WoWClass.SHAMAN]: '#0070DE',
    [WoWClass.MAGE]: '#69CCF0',
    [WoWClass.WARLOCK]: '#9482C9',
    [WoWClass.MONK]: '#00FF96',
    [WoWClass.DRUID]: '#FF7D0A',
    [WoWClass.DEMON_HUNTER]: '#A330C9',
    [WoWClass.EVOKER]: '#33937F'
  }
  return colors[classKey] || '#888888'
}

// 获取职业显示名称
function getClassDisplayName(classKey: string): string {
  const names: Record<string, string> = {
    [WoWClass.WARRIOR]: '战士',
    [WoWClass.PALADIN]: '圣骑士',
    [WoWClass.HUNTER]: '猎人',
    [WoWClass.ROGUE]: '潜行者',
    [WoWClass.PRIEST]: '牧师',
    [WoWClass.DEATH_KNIGHT]: '死亡骑士',
    [WoWClass.SHAMAN]: '萨满祭司',
    [WoWClass.MAGE]: '法师',
    [WoWClass.WARLOCK]: '术士',
    [WoWClass.MONK]: '武僧',
    [WoWClass.DRUID]: '德鲁伊',
    [WoWClass.DEMON_HUNTER]: '恶魔猎手',
    [WoWClass.EVOKER]: '唤魔师'
  }
  return names[classKey] || classKey
}

// 获取职业标签类型
function getClassTagType(classKey: string): string {
  const typeMap: Record<string, string> = {
    [WoWClass.WARRIOR]: 'danger',
    [WoWClass.PALADIN]: 'warning',
    [WoWClass.HUNTER]: 'success',
    [WoWClass.ROGUE]: 'warning',
    [WoWClass.PRIEST]: 'info',
    [WoWClass.DEATH_KNIGHT]: 'danger',
    [WoWClass.SHAMAN]: 'primary',
    [WoWClass.MAGE]: 'info',
    [WoWClass.WARLOCK]: 'primary',
    [WoWClass.MONK]: 'success',
    [WoWClass.DRUID]: 'warning',
    [WoWClass.DEMON_HUNTER]: 'danger',
    [WoWClass.EVOKER]: 'primary'
  }
  return typeMap[classKey] || ''
}

// 品质颜色映射
function getQualityColor(quality: string): string {
  const colors: Record<string, string> = {
    'POOR': '#9d9d9d',
    'COMMON': '#ffffff',
    'UNCOMMON': '#1eff00',
    'RARE': '#0070dd',
    'EPIC': '#a335ee',
    'LEGENDARY': '#ff8000'
  }
  return colors[quality] || '#ffffff'
}

// 品质名称映射
function getQualityName(quality: string): string {
  const names: Record<string, string> = {
    'POOR': '粗糙',
    'COMMON': '普通',
    'UNCOMMON': '优秀',
    'RARE': '精良',
    'EPIC': '史诗',
    'LEGENDARY': '传说'
  }
  return names[quality] || quality
}

// 格式化日期
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化金币
function formatGold(copper: number): string {
  if (copper === 0) return '0金'
  const gold = Math.floor(copper / 10000)
  const silver = Math.floor((copper % 10000) / 100)
  const c = copper % 100
  const parts = []
  if (gold > 0) parts.push(`${gold}金`)
  if (silver > 0) parts.push(`${silver}银`)
  if (c > 0) parts.push(`${c}铜`)
  return parts.join(' ')
}

// 返回上一页
function goBack() {
  router.back()
}

// 重置装备需求表单
function resetNeedForm() {
  needFormRef.value?.resetFields()
  Object.assign(needForm, {
    character_id: '',
    item_id: 0,
    item_name: '',
    boss_id: undefined,
    boss_name: '',
    dungeon_name: '',
    priority: 1,
    obtained: false,
    notes: ''
  })
  isEditingNeed.value = false
  editingNeedId.value = null
}

// 提交装备需求表单
async function submitNeedForm() {
  if (!needFormRef.value) return

  await needFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return

    try {
      if (isEditingNeed.value && editingNeedId.value) {
        await itemNeedStore.updateItemNeed(editingNeedId.value, needForm)
        ElMessage.success('装备需求更新成功')
      } else {
        await itemNeedStore.createItemNeed(needForm)
        ElMessage.success('装备需求添加成功')
      }
      showAddNeedDialog.value = false
      resetNeedForm()
      await loadItemNeeds()
      await loadProgress()
    } catch (error) {
      ElMessage.error(isEditingNeed.value ? '装备需求更新失败' : '装备需求添加失败')
    }
  })
}

// 编辑装备需求
function editNeed(need: ItemNeed) {
  isEditingNeed.value = true
  editingNeedId.value = need.id
  Object.assign(needForm, {
    character_id: need.character_id,
    item_id: need.item_id,
    item_name: need.item_name,
    boss_id: need.boss_id,
    boss_name: need.boss_name || '',
    dungeon_name: need.dungeon_name || '',
    priority: need.priority,
    obtained: need.obtained,
    notes: need.notes || ''
  })
  showAddNeedDialog.value = true
}

// 标记装备为已获取
async function markAsObtained(id: string) {
  try {
    await itemNeedStore.markAsObtained(id)
    ElMessage.success('已标记为获取')
    await loadItemNeeds()
    await loadProgress()
  } catch (error) {
    ElMessage.error('标记失败')
  }
}

// 删除装备需求
async function deleteNeed(id: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个装备需求吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await itemNeedStore.deleteItemNeed(id)
    ElMessage.success('删除成功')
    await loadItemNeeds()
    await loadProgress()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 加载角色信息
async function loadCharacter() {
  const characterId = route.params.id as string
  try {
    character.value = await characterStore.fetchCharacter(characterId)
    needForm.character_id = characterId
  } catch (error) {
    ElMessage.error('加载角色信息失败')
    router.push('/characters')
  }
}

// 加载装备需求
async function loadItemNeeds() {
  const characterId = route.params.id as string
  await itemNeedStore.fetchItemNeeds({ character_id: characterId })
  itemNeeds.value = itemNeedStore.filterByCharacter(characterId)
}

// 加载进度
async function loadProgress() {
  const characterId = route.params.id as string
  try {
    progress.value = await itemNeedStore.fetchProgress(characterId)
  } catch (error) {
    console.error('加载进度失败:', error)
  }
}

// 加载角色金币
async function loadGold() {
  goldLoading.value = true
  try {
    // 从金币统计列表接口获取，和金币统计页面保持同一数据源
    const allGold = await goldApi.getAllGold()
    const found = allGold.data.find((g: any) => g.character_id === character.value?.id)
    goldData.value = found ? { character_gold: found } : null
  } catch {
    goldData.value = null
  } finally {
    goldLoading.value = false
  }
}

// 从 tdInspect 装备字符串解析装备信息
function parseTdInspectEquipment(equipString: string): any {
  // tdInspect 格式: item:itemId:enchantId:gemId1:gemId2:gemId3:gemId4:suffixId:uniqueId:level:upgradeId:instanceId:numBonusIds:bonusId1:bonusId2:...
  // 示例: item:257664:3820:41285:40026:::::80::::::::::
  const parts = equipString.split(':')
  if (parts.length < 2 || parts[0] !== 'item') {
    return null
  }
  
  const itemId = parseInt(parts[1]) || 0
  const enchantId = parseInt(parts[2]) || 0
  const gemIds = [
    parseInt(parts[3]) || 0,
    parseInt(parts[4]) || 0,
    parseInt(parts[5]) || 0,
    parseInt(parts[6]) || 0
  ].filter(id => id > 0)
  
  // 尝试从 bonus IDs 获取物品等级
  let itemLevel = 0
  const numBonusIds = parseInt(parts[13]) || 0
  if (numBonusIds > 0 && parts.length > 14) {
    // bonus IDs 可能包含物品等级信息
    // 这里简化处理，实际可能需要查询物品数据库
  }
  
  return {
    itemId,
    enchantId,
    gemIds,
    rawString: equipString
  }
}

// 从 equips_data 加载装备（tdInspect 数据）
async function loadEquipmentFromEquipsData() {
  if (!character.value?.equips_data) {
    equipment.value = []
    averageItemLevel.value = 0
    return
  }
  
  try {
    const equipsArray = JSON.parse(character.value.equips_data)
    if (!Array.isArray(equipsArray) || equipsArray.length === 0) {
      equipment.value = []
      averageItemLevel.value = 0
      return
    }
    
    // 装备槽位映射（根据 tdInspect 的顺序）
    const slotMapping = [
      '头部', '颈部', '肩部', '背部', '胸部', '衬衣', '战袍', '手腕',
      '手', '腰部', '腿部', '脚', '戒指1', '戒指2', '饰品1', '饰品2',
      '主手', '副手', '远程'
    ]
    
    // 解析所有装备并收集物品ID
    const parsedEquips: any[] = []
    const itemIds: number[] = []
    
    equipsArray.forEach((equipStr: string, index: number) => {
      const parsed = parseTdInspectEquipment(equipStr)
      if (parsed) {
        parsedEquips.push({
          index,
          slot: slotMapping[index] || `槽位${index}`,
          ...parsed
        })
        itemIds.push(parsed.itemId)
      }
    })
    
    // 批量查询物品信息
    let itemInfoMap: Record<number, any> = {}
    if (itemIds.length > 0) {
      try {
        itemInfoMap = await itemApi.getBatch(itemIds)
      } catch (e) {
        console.error('查询物品信息失败:', e)
      }
    }
    
    // 构建装备列表
    equipment.value = parsedEquips.map((parsed: any) => {
      const itemInfo = itemInfoMap[parsed.itemId] || {}
      
      return {
        slot: parsed.slot,
        slotType: '',
        name: itemInfo.name || `物品 #${parsed.itemId}`,
        itemId: parsed.itemId,
        quality: itemInfo.quality?.toUpperCase() || 'COMMON',
        qualityValue: getQualityValue(itemInfo.quality),
        itemLevel: itemInfo.item_level || 0,
        icon: itemInfo.icon_url || '',
        binding: '',
        armor: 0,
        stats: itemInfo.stats ? JSON.parse(itemInfo.stats) : [],
        enchantments: parsed.enchantId > 0 ? [{ enchantment_id: parsed.enchantId, display_string: `附魔 #${parsed.enchantId}` }] : [],
        sockets: parsed.gemIds.map((gemId: number) => ({ type: { type: 'prismatic', name: '棱彩' }, item: gemId > 0 ? { name: `宝石 #${gemId}` } : null })),
        durabilityCurrent: null,
        durabilityMax: null,
        itemSetName: null
      }
    }).filter((item: any) => item !== null)
    
    // 计算平均装等
    const validItems = equipment.value.filter((i: any) => i.itemLevel > 0)
    if (validItems.length > 0) {
      const total = validItems.reduce((sum: number, i: any) => sum + i.itemLevel, 0)
      averageItemLevel.value = Math.round(total / validItems.length)
    } else {
      averageItemLevel.value = 0
    }
    
  } catch (error) {
    console.error('解析装备数据失败:', error)
    equipment.value = []
    averageItemLevel.value = 0
  }
}

// 获取品质数值
function getQualityValue(quality: string): number {
  const values: Record<string, number> = {
    'poor': 0,
    'common': 1,
    'uncommon': 2,
    'rare': 3,
    'epic': 4,
    'legendary': 5
  }
  return values[quality?.toLowerCase()] || 1
}

// 加载角色装备（优先从 equips_data，其次从 API）
async function loadEquipment() {
  const characterId = route.params.id as string
  equipmentLoading.value = true
  
  try {
    // 首先尝试从角色的 equips_data 加载（tdInspect 数据）
    if (character.value?.equips_data) {
      await loadEquipmentFromEquipsData()
      if (equipment.value.length > 0) {
        equipmentLoading.value = false
        return
      }
    }
    
    // 如果没有 tdInspect 数据，尝试从 API 加载
    const data = await equipmentApi.getCharacterEquipment(characterId)
    
    if (data && data.equipped_items) {
      equipment.value = data.equipped_items.map((item: any) => ({
        slot: item.slot,
        slotType: item.slot_type || '',
        name: item.name,
        itemId: item.item_id,
        quality: item.quality,
        qualityValue: item.quality_value || 1,
        itemLevel: item.item_level || 0,
        icon: item.icon_url || '',
        binding: item.binding || '',
        armor: item.armor || 0,
        stats: JSON.parse(item.stats || '[]'),
        enchantments: JSON.parse(item.enchantments || '[]'),
        sockets: JSON.parse(item.sockets || '[]'),
        durabilityCurrent: item.durability_current,
        durabilityMax: item.durability_max,
        itemSetName: item.item_set_name
      }))
      
      // 计算平均装等
      const validItems = equipment.value.filter((i: any) => i.itemLevel > 0)
      if (validItems.length > 0) {
        const total = validItems.reduce((sum: number, i: any) => sum + i.itemLevel, 0)
        averageItemLevel.value = Math.round(total / validItems.length)
      }
    } else {
      equipment.value = []
      averageItemLevel.value = 0
    }
  } catch (error) {
    console.error('加载装备失败:', error)
    equipment.value = []
    averageItemLevel.value = 0
  } finally {
    equipmentLoading.value = false
  }
}

// 生命周期
onMounted(async () => {
  loading.value = true
  try {
    await loadCharacter()
    await Promise.all([loadItemNeeds(), loadProgress(), loadEquipment()])
    await loadGold()
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.character-detail-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  gap: 20px;
}

.character-header-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: center;
}

.class-icon-lg {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.3);
  padding: 2px;
  object-fit: cover;
}

.faction-icon-lg {
  width: 32px;
  height: 32px;
  border-radius: 6px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #e5e7eb;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.loading-container {
  padding: 40px;
}

.character-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.header-filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

.progress-content {
  padding: 20px 0;
}

.progress-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 30px;
  padding: 20px;
  background: #172033;
  border-radius: 8px;
  border: 1px solid #374151;
}

.empty-container {
  padding: 40px 20px;
  text-align: center;
}

.form-tip {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.gold-card .gold-content {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.gold-card .gold-amount {
  font-size: 28px;
  font-weight: 700;
  color: #fbbf24;
}

.gold-loading {
  padding: 10px 0;
}

/* ==================== 魔兽风格装备展示 ==================== */

.equipment-paperdoll {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
  border-radius: 12px;
}

.equipment-paperdoll-top {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
}

/* 底部武器栏 */
.equipment-weapons-row {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid #2d3748;
}

.weapon-slot {
  min-width: 320px;
  max-width: 380px;
}

.equipment-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.left-column {
  align-items: flex-end;
}

.right-column {
  align-items: flex-start;
}

.paperdoll-slot {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid #2d3748;
  border-left: 3px solid #2d3748;
  border-radius: 8px;
  min-width: 320px;
  max-width: 380px;
  transition: all 0.2s;
}

.left-column .paperdoll-slot {
  flex-direction: row-reverse;
  border-left: none;
  border-right: 3px solid #2d3748;
}

.paperdoll-slot:hover {
  background: rgba(23, 32, 51, 0.9);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.paperdoll-slot.has-item {
  background: rgba(23, 32, 51, 0.9);
}

.slot-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #4a5568;
  font-size: 13px;
  min-height: 60px;
}

.slot-icon {
  width: 48px;
  height: 48px;
  border-radius: 6px;
  background: #0f172a;
  border: 2px solid #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  flex-shrink: 0;
}

.slot-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.slot-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.item-name {
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
  flex: 1;
}

.item-ilvl {
  color: #fbbf24;
  font-weight: 700;
  font-size: 12px;
  flex-shrink: 0;
}

/* 属性列表 */
.item-stats {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.stat-line {
  font-size: 11px;
  line-height: 1.4;
}

.stat-text {
  color: #e2e8f0;
}

.stat-text.bonus {
  color: #1eff00;
}

/* 附魔 */
.item-enchants {
  margin-top: 2px;
}

.enchant-line {
  font-size: 11px;
  line-height: 1.4;
}

.enchant-text {
  color: #1eff00;
}

/* 宝石插槽 */
.item-sockets {
  display: flex;
  flex-direction: column;
  gap: 1px;
  margin-top: 2px;
}

.socket-line {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
}

.socket-icon {
  font-size: 10px;
}

.socket-icon.prismatic {
  color: #808080;
}

.socket-icon.red {
  color: #ff2020;
}

.socket-icon.blue {
  color: #4040ff;
}

.socket-icon.yellow {
  color: #ffff00;
}

.socket-icon.meta {
  color: #c0c0c0;
}

.socket-gem {
  color: #1eff00;
}

.socket-empty {
  color: #6b7280;
  font-style: italic;
}

/* 套装 */
.item-set {
  margin-top: 2px;
  font-size: 11px;
  color: #a335ee;
  font-weight: 500;
}

/* 装备特效 */
.item-spells {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 4px;
  padding-top: 4px;
  border-top: 1px dashed #374151;
}

.spell-line {
  font-size: 11px;
  line-height: 1.4;
}

.spell-name {
  color: #1eff00;
  font-weight: 500;
}

.spell-description {
  color: #1eff00;
}

/* 中间角色信息 */
.equipment-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 20px;
  min-width: 140px;
}

.character-avatar {
  position: relative;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 3px solid #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.character-avatar img {
  width: 80%;
  height: 80%;
  object-fit: contain;
}

.character-level {
  position: absolute;
  bottom: -5px;
  right: -5px;
  width: 32px;
  height: 32px;
  background: #fbbf24;
  color: #000;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  border: 2px solid #1a1f2e;
}

.character-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  font-size: 13px;
}

.meta-label {
  color: #6b7280;
}

.meta-value {
  font-weight: 600;
}

.meta-value.alliance {
  color: #0078ff;
}

.meta-value.horde {
  color: #ff2020;
}

.equipment-loading {
  padding: 20px 0;
}

.equipment-hint {
  font-size: 12px;
  color: #6b7280;
  margin-top: 8px;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .equipment-paperdoll-top {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .equipment-weapons-row {
    flex-direction: column;
    align-items: center;
  }
  
  .weapon-slot {
    min-width: 100%;
    max-width: 100%;
  }
  
  .equipment-column {
    align-items: center !important;
  }
  
  .left-column .paperdoll-slot {
    flex-direction: row;
    border-left: 3px solid #2d3748;
    border-right: none;
  }
  
  .equipment-center {
    order: -1;
    flex-direction: row;
    justify-content: center;
  }
  
  .character-meta {
    width: auto;
    min-width: 200px;
  }
}

@media (max-width: 640px) {
  .paperdoll-slot {
    min-width: 100%;
    max-width: 100%;
  }
  
  .equipment-center {
    flex-direction: column;
  }
}
</style>
