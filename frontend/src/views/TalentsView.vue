<template>
  <div class="talents-page">
    <div class="page-header">
      <h1>🌟 天赋模拟器</h1>
      <p>查看各职业天赋树，保存和分享你的天赋配点</p>
    </div>

    <!-- 职业选择 -->
    <div class="class-selector">
      <h3>选择职业</h3>
      <div class="class-grid">
        <div
          v-for="cls in classes"
          :key="cls.id"
          class="class-card"
          :class="{ active: selectedClass === cls.id }"
          @click="selectClass(cls.id)"
        >
          <img :src="cls.icon" class="class-icon-img" :alt="cls.name">
          <span class="class-name">{{ cls.name }}</span>
        </div>
      </div>
    </div>

    <!-- 天赋选择 -->
    <div v-if="selectedClass && classSpecs.length > 0" class="spec-selector">
      <h3>选择天赋</h3>
      <div class="spec-tabs">
        <button
          v-for="spec in classSpecs"
          :key="spec"
          class="spec-tab"
          :class="{ active: selectedSpec === spec }"
          @click="selectSpec(spec)"
        >
          {{ spec }}
        </button>
      </div>
    </div>

    <!-- 天赋树展示 -->
    <div v-if="talentTree.tree" class="talent-tree-container">
      <div class="tree-header">
        <h2>{{ talentTree.tree.spec_name }} 天赋</h2>
        <p v-if="talentTree.tree.description">{{ talentTree.tree.description }}</p>
      </div>

      <!-- 参考图片展示 -->
      <div v-if="referenceImages.length > 0" class="reference-images">
        <h3>📷 参考配点</h3>
        <div class="image-gallery">
          <div 
            v-for="img in referenceImages" 
            :key="img.id" 
            class="image-card"
            @click="viewImage(img)"
          >
            <img :src="getImageUrl(img.image_path)" :alt="img.name">
            <div class="image-overlay">
              <span class="image-name">{{ img.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 天赋网格 -->
      <div class="talent-grid">
        <div
          v-for="row in 11"
          :key="row"
          class="talent-row"
        >
          <div
            v-for="col in 4"
            :key="col"
            class="talent-cell"
          >
            <TalentNode
              v-if="getNodeAt(row, col)"
              :node="getNodeAt(row, col)"
              :points="getPoints(getNodeAt(row, col).id)"
              @click="onNodeClick(getNodeAt(row, col))"
            />
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="tree-actions">
        <button class="btn btn-primary" @click="showSaveDialog = true">
          💾 保存配点
        </button>
        <button class="btn btn-secondary" @click="resetPoints">
          🔄 重置
        </button>
        <button class="btn btn-secondary" @click="showBuilds = true">
          📋 我的配点
        </button>
      </div>
    </div>

    <!-- 图片查看器 -->
    <div v-if="showImageViewer && viewingImage" class="image-viewer-overlay" @click.self="closeImageViewer">
      <div class="image-viewer">
        <button class="close-btn" @click="closeImageViewer">✕</button>
        <img :src="getImageUrl(viewingImage.image_path)" :alt="viewingImage.name">
        <div class="image-info">
          <h4>{{ viewingImage.name }}</h4>
          <p v-if="viewingImage.notes">{{ viewingImage.notes }}</p>
        </div>
      </div>
    </div>

    <!-- 保存配点对话框 -->
    <div v-if="showSaveDialog" class="modal-overlay" @click.self="showSaveDialog = false">
      <div class="modal">
        <h3>保存天赋配点</h3>
        <div class="form-group">
          <label>方案名称</label>
          <input v-model="buildName" type="text" placeholder="例如：PVE 戒律治疗">
        </div>
        <div class="form-group">
          <label>备注</label>
          <textarea v-model="buildNotes" rows="3" placeholder="可选：描述这个配点的用途"></textarea>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showSaveDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveBuild">保存</button>
        </div>
      </div>
    </div>

    <!-- 我的配点列表 -->
    <div v-if="showBuilds" class="modal-overlay" @click.self="showBuilds = false">
      <div class="modal modal-large">
        <h3>我的天赋配点</h3>
        <div class="builds-list">
          <div v-for="build in myBuilds" :key="build.id" class="build-card">
            <div class="build-info">
              <h4>{{ build.name }}</h4>
              <p class="build-class">{{ build.class_name }} - {{ build.spec_name }}</p>
              <p v-if="build.notes" class="build-notes">{{ build.notes }}</p>
              <p class="build-date">{{ formatDate(build.created_at) }}</p>
            </div>
            <div class="build-actions">
              <button class="btn btn-sm" @click="loadBuild(build)">加载</button>
              <button class="btn btn-sm btn-danger" @click="deleteBuild(build.id)">删除</button>
            </div>
          </div>
          <div v-if="myBuilds.length === 0" class="empty-state">
            还没有保存的配点方案
          </div>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showBuilds = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { talentApi } from '@/api'
import TalentNode from '@/components/TalentNode.vue'

// 职业列表
const classes = ref([
  { id: 'priest', name: '牧师', specs: ['戒律', '神圣', '暗影'], icon: '/images/牧师.webp' },
  { id: 'mage', name: '法师', specs: ['奥术', '火焰', '冰霜'], icon: '/images/法师.webp' },
  { id: 'warlock', name: '术士', specs: ['痛苦', '恶魔学识', '毁灭'], icon: '/images/术士.webp' },
  { id: 'rogue', name: '潜行者', specs: ['刺杀', '战斗', '敏锐'], icon: '/images/盗贼.webp' },
  { id: 'warrior', name: '战士', specs: ['武器', '狂怒', '防护'], icon: '/images/战士.webp' },
  { id: 'hunter', name: '猎人', specs: ['野兽控制', '射击', '生存'], icon: '/images/猎人.webp' },
  { id: 'paladin', name: '圣骑士', specs: ['神圣', '防护', '惩戒'], icon: '/images/圣骑士.webp' },
  { id: 'shaman', name: '萨满祭司', specs: ['元素', '增强', '恢复'], icon: '/images/萨满祭司.webp' },
  { id: 'druid', name: '德鲁伊', specs: ['平衡', '野性战斗', '恢复'], icon: '/images/德鲁伊.webp' },
  { id: 'deathknight', name: '死亡骑士', specs: ['鲜血', '冰霜', '邪恶'], icon: '/images/死亡骑士.webp' },
])

// 状态
const selectedClass = ref('')
const selectedSpec = ref('')
const talentTree = ref({ tree: null as any, nodes: [] as any[] })
const points = ref<Record<number, number>>({})
const myBuilds = ref<any[]>([])
const referenceImages = ref<any[]>([])
const showSaveDialog = ref(false)
const showBuilds = ref(false)
const showImageViewer = ref(false)
const viewingImage = ref<any>(null)
const buildName = ref('')
const buildNotes = ref('')

// 计算属性
const classSpecs = computed(() => {
  const cls = classes.value.find(c => c.id === selectedClass.value)
  return cls ? cls.specs : []
})

// 方法
const selectClass = (classId: string) => {
  selectedClass.value = classId
  selectedSpec.value = ''
  points.value = {}
}

const selectSpec = async (spec: string) => {
  selectedSpec.value = spec
  await loadTalentTree()
  await loadReferenceImages()
}

const loadTalentTree = async () => {
  if (!selectedClass.value || !selectedSpec.value) return
  
  try {
    const data = await talentApi.getTalentTreeBySpec(selectedClass.value, selectedSpec.value)
    talentTree.value = data
    points.value = {}
  } catch (error) {
    console.error('Failed to load talent tree:', error)
    talentTree.value = { tree: null, nodes: [] }
  }
}

const loadReferenceImages = async () => {
  if (!selectedClass.value || !selectedSpec.value) return

  const images: any[] = []

  // 1. 从后端加载保存的配点图片
  try {
    const data = await talentApi.getBuilds({
      class_name: selectedClass.value,
      spec_name: selectedSpec.value
    })
    const buildsWithImages = data.builds.filter((b: any) => b.image_path)
    images.push(...buildsWithImages)
  } catch (error) {
    console.error('Failed to load builds:', error)
  }

  // 2. 加载本地参考图片，失败时使用 CDN 专精图标
  const classNameMap: Record<string, string> = {
    'priest': '牧师',
    'mage': '法师',
    'warlock': '术士',
    'rogue': '盗贼',
    'warrior': '战士',
    'hunter': '猎人',
    'paladin': '圣骑士',
    'shaman': '萨满祭司',
    'druid': '德鲁伊',
    'deathknight': '死亡骑士'
  }

  const specIconMap: Record<string, string> = {
    '战士-武器': 'ability_warrior_savageblow',
    '战士-狂怒': 'ability_warrior_innerrage',
    '战士-防护': 'ability_warrior_defense',
    '圣骑士-神圣': 'spell_holy_holybolt',
    '圣骑士-防护': 'spell_holy_devotionaura',
    '圣骑士-惩戒': 'spell_holy_auraoflight',
    '猎人-野兽控制': 'ability_hunter_bestialdiscipline',
    '猎人-射击': 'ability_hunter_focusedaim',
    '猎人-生存': 'ability_hunter_camouflage',
    '盗贼-刺杀': 'ability_rogue_eviscerate',
    '盗贼-战斗': 'ability_rogue_sabreslash',
    '盗贼-敏锐': 'ability_rogue_masterofsubtlety',
    '牧师-戒律': 'spell_holy_powerwordshield',
    '牧师-神圣': 'spell_holy_guardianspirit',
    '牧师-暗影': 'spell_shadow_shadowwordpain',
    '萨满祭司-元素': 'spell_nature_lightningbolt',
    '萨满祭司-增强': 'spell_nature_lightningshield',
    '萨满祭司-恢复': 'spell_nature_healingwave',
    '法师-奥术': 'spell_nature_astralrecal',
    '法师-火焰': 'spell_fire_fireball',
    '法师-冰霜': 'spell_frost_frostbolt',
    '术士-痛苦': 'spell_shadow_curseofagony',
    '术士-恶魔学识': 'spell_shadow_metamorphosis',
    '术士-毁灭': 'spell_shadow_rainoffire',
    '德鲁伊-平衡': 'spell_nature_starfall',
    '德鲁伊-野性战斗': 'ability_druid_catform',
    '德鲁伊-恢复': 'spell_nature_healingtouch',
    '死亡骑士-鲜血': 'spell_deathknight_bloodpresence',
    '死亡骑士-冰霜': 'spell_deathknight_frostpresence',
    '死亡骑士-邪恶': 'spell_deathknight_unholypresence'
  }

  const cnClassName = classNameMap[selectedClass.value]
  if (cnClassName) {
    const localImagePath = `/images/天赋/${cnClassName}-${selectedSpec.value}.png`
    const img = new Image()
    img.onload = () => {
      if (!images.some((img: any) => img.image_path === localImagePath)) {
        images.push({
          id: `local-${selectedClass.value}-${selectedSpec.value}`,
          name: `${cnClassName}${selectedSpec.value}参考`,
          image_path: localImagePath,
          notes: '本地参考图片'
        })
        referenceImages.value = images
      }
    }
    img.onerror = () => {
      const iconName = specIconMap[`${cnClassName}-${selectedSpec.value}`]
      if (iconName) {
        const cdnUrl = `https://wow.zamimg.com/images/wow/icons/medium/${iconName}.jpg`
        if (!images.some((img: any) => img.image_path === cdnUrl)) {
          images.push({
            id: `cdn-${selectedClass.value}-${selectedSpec.value}`,
            name: `${cnClassName}${selectedSpec.value}专精图标`,
            image_path: cdnUrl,
            notes: 'CDN专精图标'
          })
          referenceImages.value = images
        }
      }
    }
    img.src = localImagePath
  }

  referenceImages.value = images
}

const getImageUrl = (path: string) => {
  if (!path) return ''

  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }

  if (path.startsWith('/images/')) {
    return path
  }

  const filename = path.split('\\').pop() || path.split('/').pop()
  return `/uploads/talent_images/${filename}`
}

const viewImage = (img: any) => {
  viewingImage.value = img
  showImageViewer.value = true
}

const closeImageViewer = () => {
  showImageViewer.value = false
  viewingImage.value = null
}

const getNodeAt = (row: number, col: number) => {
  return talentTree.value.nodes.find(n => n.row === row && n.col === col)
}

const getPoints = (nodeId: number) => {
  return points.value[nodeId] || 0
}

const onNodeClick = (node: any) => {
  const current = getPoints(node.id)
  if (current < node.max_points) {
    points.value[node.id] = current + 1
  } else {
    points.value[node.id] = 0
  }
}

const resetPoints = () => {
  points.value = {}
}

const saveBuild = async () => {
  if (!buildName.value.trim()) return
  
  try {
    await talentApi.createBuild({
      name: buildName.value,
      class_name: selectedClass.value,
      spec_name: selectedSpec.value,
      points: points.value,
      notes: buildNotes.value
    })
    
    showSaveDialog.value = false
    buildName.value = ''
    buildNotes.value = ''
    alert('配点方案已保存！')
    loadMyBuilds()
    loadReferenceImages()
  } catch (error) {
    console.error('Failed to save build:', error)
    alert('保存失败')
  }
}

const loadMyBuilds = async () => {
  try {
    const data = await talentApi.getBuilds()
    myBuilds.value = data.builds
  } catch (error) {
    console.error('Failed to load builds:', error)
  }
}

const loadBuild = (build: any) => {
  selectedClass.value = build.class_name
  selectedSpec.value = build.spec_name
  points.value = { ...build.points }
  loadTalentTree()
  loadReferenceImages()
  showBuilds.value = false
}

const deleteBuild = async (id: number) => {
  if (!confirm('确定要删除这个配点方案吗？')) return
  
  try {
    await talentApi.deleteBuild(id)
    loadMyBuilds()
    loadReferenceImages()
  } catch (error) {
    console.error('Failed to delete build:', error)
  }
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

// 监听
watch([selectedClass, selectedSpec], () => {
  if (selectedClass.value && selectedSpec.value) {
    loadTalentTree()
    loadReferenceImages()
  }
})

onMounted(() => {
  loadMyBuilds()
})
</script>

<style scoped>
.talents-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 8px;
}

.page-header p {
  color: #888;
}

/* 职业选择 */
.class-selector {
  margin-bottom: 30px;
}

.class-selector h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.class-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 12px;
}

.class-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px;
  background: rgba(26, 26, 46, 0.65);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.class-card:hover {
  background: rgba(37, 37, 66, 0.75);
  transform: translateY(-2px);
}

.class-card.active {
  border-color: #ffd700;
  background: rgba(42, 42, 74, 0.8);
}

.class-icon {
  width: 48px;
  height: 48px;
  background: #333;
  border-radius: 8px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.class-icon-img {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-bottom: 8px;
  object-fit: cover;
}

.class-name {
  font-size: 14px;
  color: #ddd;
}

/* 天赋选择 */
.spec-selector {
  margin-bottom: 30px;
}

.spec-selector h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

.spec-tabs {
  display: flex;
  gap: 10px;
}

.spec-tab {
  padding: 10px 24px;
  background: #1a1a2e;
  border: 2px solid transparent;
  border-radius: 8px;
  color: #ddd;
  cursor: pointer;
  transition: all 0.2s;
}

.spec-tab:hover {
  background: #252542;
}

.spec-tab.active {
  border-color: #ffd700;
  background: #2a2a4a;
  color: #ffd700;
}

/* 天赋树 */
.talent-tree-container {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 30px;
}

.tree-header {
  text-align: center;
  margin-bottom: 30px;
}

.tree-header h2 {
  font-size: 24px;
  margin-bottom: 8px;
}

.tree-header p {
  color: #888;
}

/* 参考图片 */
.reference-images {
  margin-bottom: 30px;
}

.reference-images h3 {
  font-size: 16px;
  margin-bottom: 15px;
  color: #ffd700;
}

.image-gallery {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.image-card {
  width: 200px;
  height: 120px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  border: 2px solid #333;
  transition: all 0.2s;
}

.image-card:hover {
  border-color: #ffd700;
  transform: scale(1.02);
}

.image-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  padding: 10px;
}

.image-name {
  font-size: 12px;
  color: #fff;
}

/* 图片查看器 */
.image-viewer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.image-viewer {
  position: relative;
  max-width: 90%;
  max-height: 90%;
}

.image-viewer img {
  max-width: 100%;
  max-height: 80vh;
  border-radius: 8px;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.image-info {
  text-align: center;
  margin-top: 15px;
}

.image-info h4 {
  color: #ffd700;
  margin-bottom: 5px;
}

.image-info p {
  color: #888;
  font-size: 14px;
}

/* 天赋网格 */
.talent-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 30px;
}

.talent-row {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.talent-cell {
  width: 64px;
  height: 64px;
}

/* 操作按钮 */
.tree-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #ffd700;
  color: #000;
}

.btn-primary:hover {
  background: #ffed4e;
}

.btn-secondary {
  background: #333;
  color: #ddd;
}

.btn-secondary:hover {
  background: #444;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #1a1a2e;
  border-radius: 16px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 700px;
}

.modal h3 {
  margin-bottom: 20px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #aaa;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 12px;
  background: #252542;
  border: 1px solid #333;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

/* 配点列表 */
.builds-list {
  max-height: 400px;
  overflow-y: auto;
}

.build-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: rgba(37, 37, 66, 0.6);
  border-radius: 8px;
  margin-bottom: 10px;
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.build-info h4 {
  margin-bottom: 4px;
}

.build-class {
  color: #ffd700;
  font-size: 14px;
}

.build-notes {
  color: #888;
  font-size: 13px;
  margin-top: 4px;
}

.build-date {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
}

.build-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

/* 职业图标颜色 */
.class_priest { background: linear-gradient(135deg, #fff, #ddd); }
.class_mage { background: linear-gradient(135deg, #69ccf0, #3c85a5); }
.class_warlock { background: linear-gradient(135deg, #9482c9, #584c7b); }
.class_rogue { background: linear-gradient(135deg, #fff569, #b5ad45); }
.class_warrior { background: linear-gradient(135deg, #c79c6e, #8c6a45); }
.class_hunter { background: linear-gradient(135deg, #abd473, #7a994f); }
.class_paladin { background: linear-gradient(135deg, #f58cba, #b56485); }
.class_shaman { background: linear-gradient(135deg, #0070de, #004c96); }
.class_druid { background: linear-gradient(135deg, #ff7d0a, #b55807); }
.class_deathknight { background: linear-gradient(135deg, #c41f3b, #8a152a); }
</style>
