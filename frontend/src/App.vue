<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="24"><Monitor /></el-icon>
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
          <el-menu-item index="/bosses">Boss管理</el-menu-item>
          <el-menu-item index="/item-needs">装备需求</el-menu-item>
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
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  padding: 0;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
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
  color: rgba(255, 255, 255, 0.8);
  font-size: 15px;
}

.header-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.header-menu .el-menu-item.is-active {
  background: rgba(243, 156, 18, 0.2);
  color: #f39c12;
  border-bottom: 2px solid #f39c12;
}

.app-main {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

.app-footer {
  background: #1a1a2e;
  color: rgba(255, 255, 255, 0.6);
  padding: 0;
  height: 40px;
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
  color: rgba(255, 255, 255, 0.4);
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
}

#app {
  height: 100vh;
}
</style>