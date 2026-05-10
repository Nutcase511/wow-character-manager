<template>
  <div
    class="talent-node"
    :class="{
      'has-points': points > 0,
      'maxed': points >= node.max_points,
      'clickable': true
    }"
    @click="$emit('click')"
  >
    <div class="node-icon" :style="iconStyle">
      <img v-if="node.icon" :src="iconUrl" :alt="node.name">
      <div v-else class="placeholder-icon">?</div>
    </div>
    <div class="node-points" v-if="points > 0">
      {{ points }}/{{ node.max_points }}
    </div>
    <div class="node-tooltip" v-if="showTooltip">
      <div class="tooltip-name">{{ node.name }}</div>
      <div class="tooltip-desc">{{ node.description }}</div>
      <div class="tooltip-rank">等级: {{ points }}/{{ node.max_points }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{
  node: {
    id: number
    name: string
    icon?: string
    max_points: number
    description?: string
  }
  points: number
}>()

defineEmits<{
  click: []
}>()

const showTooltip = ref(false)

const iconUrl = computed(() => {
  if (!props.node.icon) return ''
  // 使用 WoWHead 图标
  return `https://wow.zamimg.com/images/wow/icons/medium/${props.node.icon}.jpg`
})

const iconStyle = computed(() => {
  if (props.points === 0) {
    return { filter: 'grayscale(100%) brightness(0.5)' }
  }
  if (props.points >= props.node.max_points) {
    return { 
      boxShadow: '0 0 10px #ffd700, 0 0 20px #ffd700',
      borderColor: '#ffd700'
    }
  }
  return {}
})
</script>

<style scoped>
.talent-node {
  position: relative;
  width: 64px;
  height: 64px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
}

.node-icon {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid #444;
  background: #1a1a2e;
  transition: all 0.2s;
}

.node-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.placeholder-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #666;
}

.talent-node:hover .node-icon {
  border-color: #888;
  transform: scale(1.05);
}

.talent-node.has-points .node-icon {
  border-color: #4a9eff;
}

.talent-node.maxed .node-icon {
  border-color: #ffd700;
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.node-points {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #1a1a2e;
  border: 2px solid #4a9eff;
  border-radius: 10px;
  padding: 2px 6px;
  font-size: 11px;
  font-weight: bold;
  color: #fff;
  min-width: 24px;
  text-align: center;
}

.talent-node.maxed .node-points {
  border-color: #ffd700;
  color: #ffd700;
}

/* 提示框 */
.node-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.95);
  border: 1px solid #444;
  border-radius: 8px;
  padding: 12px;
  width: 200px;
  margin-bottom: 8px;
  z-index: 100;
  pointer-events: none;
}

.node-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 6px solid transparent;
  border-top-color: #444;
}

.tooltip-name {
  font-weight: bold;
  color: #ffd700;
  margin-bottom: 4px;
}

.tooltip-desc {
  font-size: 12px;
  color: #aaa;
  line-height: 1.4;
  margin-bottom: 8px;
}

.tooltip-rank {
  font-size: 11px;
  color: #4a9eff;
}
</style>
