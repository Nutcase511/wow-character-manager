<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <img src="/images/wow.png" alt="WoW Logo" class="logo-image">
          <span class="logo-text">魔兽世界角色管理系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          router
          class="header-menu"
        >
          <el-menu-item index="/characters">角色管理</el-menu-item>
          <el-menu-item index="/dungeons">副本管理</el-menu-item>
          <el-menu-item index="/item-needs">装备需求</el-menu-item>
          <el-menu-item index="/bis">毕业装备</el-menu-item>
          <el-menu-item index="/gold">金币统计</el-menu-item>
          <el-menu-item index="/talents">天赋模拟器</el-menu-item>
          <el-menu-item index="/settings">系统配置</el-menu-item>
        </el-menu>
      </div>
    </el-header>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>

    <el-footer class="app-footer">
      <div class="footer-content">
        <span>© 2024 魔兽世界角色管理系统</span>
        <span class="version">v1.0.0</span>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Monitor } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #0d0d1a 0%, #111827 100%);
  color: #fff;
  padding: 0;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
  border-bottom: 1px solid #1f2937;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 40px;
  font-size: 18px;
  font-weight: 600;
}

.logo-image {
  width: 32px;
  height: 32px;
  border-radius: 6px;
}

.logo-text {
  background: linear-gradient(45deg, #f39c12, #e74c3c);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-menu {
  background: transparent;
  border: none;
  flex: 1;
}

.header-menu .el-menu-item {
  color: rgba(255, 255, 255, 0.7);
  font-size: 15px;
  border-bottom: 2px solid transparent;
}

.header-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.header-menu .el-menu-item.is-active {
  background: rgba(243, 156, 18, 0.15);
  color: #f39c12;
  border-bottom: 2px solid #f39c12;
}

.app-main {
  flex: 1;
  background: #111827;
  padding: 20px;
  overflow-y: auto;
}

.app-footer {
  background: #0d0d1a;
  color: rgba(255, 255, 255, 0.5);
  padding: 0;
  height: 40px;
  border-top: 1px solid #1f2937;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  font-size: 14px;
}

.version {
  color: rgba(255, 255, 255, 0.3);
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
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
  background: #111827;
}

#app {
  height: 100vh;
}

/* ===== 全局深色主题覆盖 ===== */
html.dark {
  --el-bg-color: #1f2937;
  --el-bg-color-overlay: #1f2937;
  --el-bg-color-page: #111827;
  --el-text-color-primary: #e5e7eb;
  --el-text-color-regular: #d1d5db;
  --el-text-color-secondary: #9ca3af;
  --el-text-color-placeholder: #6b7280;
  --el-border-color: #374151;
  --el-border-color-light: #2d3748;
  --el-border-color-lighter: #1f2937;
  --el-fill-color: #1f2937;
  --el-fill-color-light: #252f3f;
  --el-fill-color-lighter: #1f2937;
  --el-fill-color-blank: #1a2332;
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
