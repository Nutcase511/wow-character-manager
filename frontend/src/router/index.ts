import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    redirect: '/characters'
  },
  {
    path: '/characters',
    name: 'Characters',
    component: () => import('@/views/CharactersView.vue'),
    meta: { title: '角色管理' }
  },
  {
    path: '/characters/:id',
    name: 'CharacterDetail',
    component: () => import('@/views/CharacterDetailView.vue'),
    meta: { title: '角色详情' }
  },
  {
    path: '/dungeons',
    name: 'Dungeons',
    component: () => import('@/views/DungeonsView.vue'),
    meta: { title: '副本管理' }
  },
  {
    path: '/dungeons/:dungeonId/bosses',
    name: 'DungeonBosses',
    component: () => import('@/views/DungeonBossesView.vue'),
    meta: { title: '副本Boss' }
  },
  {
    path: '/bosses/:bossId/loot',
    name: 'BossLoot',
    component: () => import('@/views/BossLootView.vue'),
    meta: { title: 'Boss掉落' }
  },
  {
    path: '/bosses',
    name: 'Bosses',
    component: () => import('@/views/BossesView.vue'),
    meta: { title: 'Boss管理' }
  },
  {
    path: '/item-needs',
    name: 'ItemNeeds',
    component: () => import('@/views/ItemNeedsView.vue'),
    meta: { title: '装备需求' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 魔兽世界角色管理系统`
  }
  next()
})

export default router
