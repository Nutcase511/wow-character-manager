<template>
  <div class="dungeon-bosses-view">
    <!-- 面包屑 -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/dungeons' }">副本管理</el-breadcrumb-item>
      <el-breadcrumb-item>{{ dungeonName }}</el-breadcrumb-item>
    </el-breadcrumb>

    <div class="page-header">
      <h2 class="page-title">{{ dungeonName }}</h2>
    </div>

    <!-- Boss 卡片网格 -->
    <div v-loading="loading" class="boss-grid">
      <el-card
        v-for="boss in bosses"
        :key="boss.id"
        class="boss-card"
        shadow="hover"
        @click="goToLoot(boss)"
      >
        <div class="card-content">
          <div class="boss-avatar">
            <span>{{ boss.name.charAt(0) }}</span>
          </div>
          <div class="boss-info">
            <h3 class="boss-name">{{ boss.name }}</h3>
            <p class="boss-dungeon">{{ boss.dungeon_name }}</p>
          </div>
          <el-icon class="card-arrow"><ArrowRight /></el-icon>
        </div>
      </el-card>
    </div>

    <el-empty v-if="!loading && bosses.length === 0" description="暂无Boss数据" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { bossApi } from '@/api'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import type { Boss } from '@/types'

const route = useRoute()
const router = useRouter()

const dungeonId = Number(route.params.dungeonId)
const dungeonName = ref('')
const bosses = ref<Boss[]>([])
const loading = ref(false)

function goToLoot(boss: Boss) {
  router.push({ name: 'BossLoot', params: { bossId: boss.boss_id } })
}

async function loadBosses() {
  loading.value = true
  try {
    const response = await bossApi.getByDungeon(dungeonId)
    bosses.value = response.data
    if (bosses.value.length > 0) {
      dungeonName.value = bosses.value[0].dungeon_name
    }
  } catch (error) {
    ElMessage.error('加载Boss列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => { loadBosses() })
</script>

<style scoped>
.dungeon-bosses-view {
  max-width: 1400px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 16px;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0;
}

.boss-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  min-height: 300px;
}

.boss-card {
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #374151;
}

.boss-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 14px;
}

.boss-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e3a5f 0%, #2d1f4e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.boss-avatar span {
  color: #e5e7eb;
  font-size: 18px;
  font-weight: 600;
}

.boss-info {
  flex: 1;
  min-width: 0;
}

.boss-name {
  font-size: 15px;
  font-weight: 600;
  color: #e5e7eb;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.boss-dungeon {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

.card-arrow {
  color: #4b5563;
  font-size: 18px;
  flex-shrink: 0;
}
</style>
