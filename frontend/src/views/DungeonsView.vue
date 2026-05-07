<template>
  <div class="dungeons-view">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon><Grid /></el-icon>
        副本管理
      </h2>
      <div class="header-actions">
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          添加副本
        </el-button>
      </div>
    </div>

    <!-- 资料片 Tab -->
    <el-tabs v-model="activeExpansion" @tab-change="handleExpansionChange">
      <el-tab-pane label="巫妖王之怒" name="wotlk" />
      <el-tab-pane label="燃烧的远征" name="tbc" />
      <el-tab-pane label="经典旧世" name="classic" />
    </el-tabs>

    <!-- 类型过滤 -->
    <div class="filter-bar">
      <el-radio-group v-model="activeCategory" @change="handleCategoryChange">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="dungeon">五人本</el-radio-button>
        <el-radio-button value="raid">团本</el-radio-button>
        <el-radio-button value="worldboss">世界Boss</el-radio-button>
      </el-radio-group>
      <span class="filter-count">共 {{ dungeons.length }} 个副本</span>
    </div>

    <!-- 副本卡片网格 -->
    <div v-loading="loading" class="dungeon-grid">
      <el-card
        v-for="dungeon in dungeons"
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

    <el-empty v-if="!loading && dungeons.length === 0" description="暂无副本数据" />

    <!-- 添加副本对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="添加副本"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="副本ID" prop="dungeon_id">
          <el-input-number v-model="form.dungeon_id" :min="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="副本名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入副本名称" />
        </el-form-item>
        <el-form-item label="资料片" prop="expansion">
          <el-select v-model="form.expansion" placeholder="选择资料片">
            <el-option label="巫妖王之怒" value="wotlk" />
            <el-option label="燃烧的远征" value="tbc" />
            <el-option label="经典旧世" value="classic" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" prop="category">
          <el-select v-model="form.category" placeholder="选择类型">
            <el-option label="五人本" value="dungeon" />
            <el-option label="团本" value="raid" />
            <el-option label="世界Boss" value="worldboss" />
          </el-select>
        </el-form-item>
        <el-form-item label="最低等级" prop="minimum_level">
          <el-input-number v-model="form.minimum_level" :min="1" :max="80" />
        </el-form-item>
        <el-form-item label="难度" prop="modes">
          <el-checkbox-group v-model="form.modes">
            <el-checkbox label="normal">普通</el-checkbox>
            <el-checkbox label="heroic">英雄</el-checkbox>
            <el-checkbox label="10">10人</el-checkbox>
            <el-checkbox label="25">25人</el-checkbox>
            <el-checkbox label="10h">10H</el-checkbox>
            <el-checkbox label="25h">25H</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入副本描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="loading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { dungeonApi } from '@/api'
import { ElMessage } from 'element-plus'
import { Grid, Plus, ArrowRight } from '@element-plus/icons-vue'
import type { Dungeon } from '@/types'

const router = useRouter()

// 筛选状态
const activeExpansion = ref('wotlk')
const activeCategory = ref('all')

// 数据状态
const dungeons = ref<Dungeon[]>([])
const loading = ref(false)

// 对话框状态
const showCreateDialog = ref(false)

// 表单数据
const form = reactive({
  dungeon_id: 0,
  name: '',
  map_name: '',
  minimum_level: 70,
  modes: [] as string[],
  expansion: 'wotlk',
  category: 'dungeon',
  description: ''
})

const formRef = ref()

const rules = {
  dungeon_id: [{ required: true, message: '请输入副本ID', trigger: 'blur' }],
  name: [{ required: true, message: '请输入副本名称', trigger: 'blur' }],
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

function getCategoryTagType(cat: string): string {
  const types: Record<string, string> = { dungeon: '', raid: 'danger', worldboss: 'warning' }
  return types[cat] || ''
}

function getCategoryClass(cat: string): string {
  return cat || 'dungeon'
}

function getCategoryIcon(cat: string): string {
  const icons: Record<string, string> = { dungeon: '⚔', raid: '🏰', worldboss: '💀' }
  return icons[cat] || '⚔'
}

// 跳转到Boss列表
function goToBosses(dungeon: Dungeon) {
  router.push({ name: 'DungeonBosses', params: { dungeonId: dungeon.dungeon_id } })
}

// 筛选变更
async function handleExpansionChange() { await loadDungeons() }
async function handleCategoryChange() { await loadDungeons() }

// 重置表单
function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, {
    dungeon_id: 0, name: '', map_name: '', minimum_level: 70, modes: [],
    expansion: activeExpansion.value, category: 'dungeon', description: ''
  })
}

// 提交表单
async function submitForm() {
  if (!formRef.value) return
  await formRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    try {
      await dungeonApi.create(form)
      ElMessage.success('副本添加成功')
      showCreateDialog.value = false
      resetForm()
      await loadDungeons()
    } catch (error) {
      ElMessage.error('副本添加失败')
    }
  })
}

// 加载副本列表
async function loadDungeons() {
  loading.value = true
  try {
    const params: { expansion?: string; category?: string } = { expansion: activeExpansion.value }
    if (activeCategory.value !== 'all') {
      params.category = activeCategory.value
    }
    const response = await dungeonApi.getAll(params)
    dungeons.value = response.data
  } catch (error) {
    ElMessage.error('加载副本列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadDungeons() })
</script>

<style scoped>
.dungeons-view {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.filter-count {
  font-size: 13px;
  color: #6b7280;
}

.dungeon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  min-height: 400px;
}

.dungeon-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #374151;
}

.dungeon-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.card-icon.dungeon {
  background: #1e3a5f;
}

.card-icon.raid {
  background: #3f1f1f;
}

.card-icon.worldboss {
  background: #3f2f1f;
}

.card-info {
  flex: 1;
  min-width: 0;
}

.card-name {
  font-size: 16px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0 0 6px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.card-level {
  font-size: 12px;
  color: #9ca3af;
}

.card-modes {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.mode-tag {
  font-size: 11px;
  color: #9ca3af;
  background: #252f3f;
  padding: 1px 6px;
  border-radius: 3px;
}

.card-arrow {
  color: #4b5563;
  font-size: 18px;
  flex-shrink: 0;
}
</style>
