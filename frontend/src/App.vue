<template>
  <div class="app-wrapper">
    <video class="bg-video" autoplay muted loop playsinline poster="/images/wow.png">
      <source src="/videos/wow-bg.mp4" type="video/mp4">
    </video>
    <div class="bg-overlay" />

    <div class="app-layout">
      <aside class="app-sidebar">
        <div class="sidebar-header">
          <div class="sidebar-logo-wrap">
            <img src="/images/wow.png" alt="WoW Logo" class="sidebar-logo">
          </div>
          <div class="sidebar-title">
            <span class="title-main">魔兽世界</span>
            <span class="title-sub">角色管理系统</span>
          </div>
        </div>

        <nav class="sidebar-nav">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="sidebar-menu-item"
            :class="{ active: isActive(item.path) }"
          >
            <div class="menu-item-glow" />
            <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
            <span class="menu-text">{{ item.label }}</span>
          </router-link>
        </nav>
      </aside>

      <main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import {
  User, Grid, Goods, TrophyBase, Money, MagicStick, Setting
} from '@element-plus/icons-vue'

const route = useRoute()

interface MenuItem {
  path: string
  label: string
  icon: object
}

const menuItems: MenuItem[] = [
  { path: '/characters', label: '角色管理', icon: User },
  { path: '/dungeons', label: '副本管理', icon: Grid },
  { path: '/item-needs', label: '装备需求', icon: Goods },
  { path: '/bis', label: '毕业装备', icon: TrophyBase },
  { path: '/gold', label: '金币统计', icon: Money },
  { path: '/talents', label: '天赋模拟器', icon: MagicStick },
  { path: '/settings', label: '系统配置', icon: Setting }
]

function isActive(path: string): boolean {
  const currentPath = route.path
  if (path === '/characters' && (currentPath === '/characters' || currentPath.startsWith('/characters/'))) return true
  if (path === '/dungeons' && (currentPath === '/dungeons' || currentPath.startsWith('/dungeons/'))) return true
  if (path === '/gold' && (currentPath === '/gold' || currentPath.startsWith('/gold/'))) return true
  if (path === '/bis' && (currentPath === '/bis' || currentPath.startsWith('/bis/'))) return true
  return currentPath === path
}
</script>

<style scoped>
.app-wrapper {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  position: relative;
}

/* ===== 视频背景 ===== */
.bg-video {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  min-width: 100vw;
  min-height: 100vh;
  width: auto;
  height: auto;
  object-fit: cover;
  z-index: 0;
}

.bg-overlay {
  position: fixed;
  inset: 0;
  z-index: 1;
  background:
    linear-gradient(180deg, rgba(0, 0, 0, 0.55) 0%, rgba(0, 0, 0, 0.75) 100%),
    linear-gradient(90deg, rgba(0, 0, 0, 0.5) 0%, rgba(0, 0, 0, 0.2) 50%, rgba(0, 0, 0, 0.4) 100%);
}

/* ===== 主布局 ===== */
.app-layout {
  position: relative;
  z-index: 2;
  height: 100vh;
  display: flex;
}

/* ===== 左侧玻璃拟态菜单 ===== */
.app-sidebar {
  width: 240px;
  min-width: 240px;
  height: 100vh;
  background: rgba(8, 8, 24, 0.72);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border-right: 1px solid rgba(243, 156, 18, 0.15);
  box-shadow:
    4px 0 40px rgba(0, 0, 0, 0.5),
    inset -1px 0 0 rgba(243, 156, 18, 0.08);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ---- 侧栏头部 ---- */
.sidebar-header {
  padding: 28px 20px 24px;
  display: flex;
  align-items: center;
  gap: 14px;
  border-bottom: 1px solid rgba(243, 156, 18, 0.1);
}

.sidebar-logo-wrap {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.15), rgba(231, 76, 60, 0.1));
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 16px rgba(243, 156, 18, 0.15);
}

.sidebar-logo {
  width: 32px;
  height: 32px;
  border-radius: 6px;
}

.sidebar-title {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.title-main {
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(90deg, #f39c12, #e74c3c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1.2;
}

.title-sub {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.45);
  letter-spacing: 1px;
  text-transform: uppercase;
}

/* ---- 导航菜单 ---- */
.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  overflow-y: auto;
}

.sidebar-menu-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 13px 16px 13px 18px;
  border-radius: 10px;
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;
  border-left: 3px solid transparent;
}

/* 发光背景元素 */
.menu-item-glow {
  position: absolute;
  inset: 0;
  border-radius: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.08), rgba(231, 76, 60, 0.04));
}

.menu-icon {
  position: relative;
  z-index: 1;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
}

.menu-text {
  position: relative;
  z-index: 1;
  transition: all 0.3s ease;
}

/* 悬停效果 */
.sidebar-menu-item:hover {
  color: rgba(255, 255, 255, 0.9);
  border-left-color: rgba(243, 156, 18, 0.4);
}

.sidebar-menu-item:hover .menu-item-glow {
  opacity: 1;
}

.sidebar-menu-item:hover .menu-icon {
  color: #f39c12;
  transform: scale(1.1);
}

/* 激活效果 - WoW 金色发光 */
.sidebar-menu-item.active {
  color: #f39c12;
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.12), rgba(231, 76, 60, 0.06));
  border-left: 3px solid #f39c12;
  box-shadow:
    inset 0 0 20px rgba(243, 156, 18, 0.06),
    0 0 16px rgba(243, 156, 18, 0.1);
}

.sidebar-menu-item.active .menu-item-glow {
  opacity: 1;
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.15), rgba(231, 76, 60, 0.08));
}

.sidebar-menu-item.active .menu-icon {
  color: #f39c12;
  filter: drop-shadow(0 0 6px rgba(243, 156, 18, 0.5));
}

.sidebar-menu-item.active .menu-text {
  text-shadow: 0 0 12px rgba(243, 156, 18, 0.3);
}

/* ===== 主内容区 ===== */
.app-main {
  flex: 1;
  padding: 24px 28px;
  overflow-y: auto;
  overflow-x: hidden;
  background: rgba(17, 24, 39, 0.55);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
}

/* ===== 页面切换动画 ===== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background: #000;
  overflow: hidden;
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}

#app {
  height: 100vh;
}

/* ===== 全局深色主题覆盖 ===== */
html.dark {
  --el-bg-color: #1f2937;
  --el-bg-color-overlay: #1f2937;
  --el-bg-color-page: transparent;
  --el-text-color-primary: #e5e7eb;
  --el-text-color-regular: #d1d5db;
  --el-text-color-secondary: #9ca3af;
  --el-text-color-placeholder: #6b7280;
  --el-border-color: rgba(55, 65, 81, 0.6);
  --el-border-color-light: rgba(45, 55, 72, 0.5);
  --el-border-color-lighter: rgba(31, 41, 55, 0.5);
  --el-fill-color: rgba(31, 41, 55, 0.8);
  --el-fill-color-light: rgba(37, 47, 63, 0.7);
  --el-fill-color-lighter: rgba(31, 41, 55, 0.6);
  --el-fill-color-blank: rgba(26, 35, 50, 0.7);
  --el-mask-color: rgba(0, 0, 0, 0.6);

  color-scheme: dark;
}

/* 深色卡片 */
html.dark .el-card {
  --el-card-bg-color: #1f2937;
  border-color: #374151;
}

html.dark .el-table {
  --el-table-bg-color: #1f2937;
  --el-table-tr-bg-color: #1f2937;
  --el-table-header-bg-color: #172033;
  --el-table-row-hover-bg-color: #252f3f;
  --el-table-border-color: #374151;
}

html.dark .el-table--striped .el-table__body tr.el-table__row--striped td.el-table__cell {
  background: #172033;
}

/* 深色对话框 */
html.dark .el-dialog {
  --el-dialog-bg-color: #1f2937;
  border: 1px solid #374151;
}

/* 深色输入框 */
html.dark .el-input__wrapper,
html.dark .el-textarea__inner {
  background-color: #172033;
  box-shadow: 0 0 0 1px #374151 inset;
}

html.dark .el-input__wrapper:hover,
html.dark .el-textarea__inner:hover {
  box-shadow: 0 0 0 1px #4b5563 inset;
}

html.dark .el-select .el-input__wrapper {
  background-color: #172033;
}

/* 深色面包屑 */
html.dark .el-breadcrumb__inner,
html.dark .el-breadcrumb__separator {
  color: #9ca3af;
}

html.dark .el-breadcrumb__inner a,
html.dark .el-breadcrumb__inner.is-link {
  color: #9ca3af;
}

html.dark .el-breadcrumb__inner a:hover,
html.dark .el-breadcrumb__inner.is-link:hover {
  color: #f39c12;
}

/* 深色 Tabs */
html.dark .el-tabs__item {
  color: #9ca3af;
}

html.dark .el-tabs__item.is-active {
  color: #f39c12;
}

html.dark .el-tabs__nav-wrap::after {
  background-color: #374151;
}

/* 深色 Radio 按钮组 */
html.dark .el-radio-button__inner {
  background-color: #1f2937;
  border-color: #374151;
  color: #9ca3af;
}

html.dark .el-radio-button__original-radio:checked + .el-radio-button__inner {
  background-color: #f39c12;
  border-color: #f39c12;
  color: #000;
}

/* 深色 Tag */
html.dark .el-tag {
  border-color: #374151;
}

/* 深色描述列表 */
html.dark .el-descriptions__body {
  background-color: #1f2937;
}

html.dark .el-descriptions__label {
  color: #9ca3af;
}

/* 深色空状态 */
html.dark .el-empty__description p {
  color: #6b7280;
}

/* 页面标题通用深色 */
html.dark .page-title {
  color: #e5e7eb;
}

/* 页面主文本 */
html.dark .filter-count {
  color: #6b7280;
}

/* 品质颜色在深色背景下保持鲜艳 */
html.dark .q-poor { color: #9d9d9d; }
html.dark .q-common { color: #e5e7eb; }
html.dark .q-uncommon { color: #1eff00; }
html.dark .q-rare { color: #4d9dff; }
html.dark .q-epic { color: #c875ff; }
html.dark .q-legendary { color: #ff8000; }
</style>
