import axios from 'axios'
import type {
  Character,
  CharacterCreate,
  ItemNeed,
  ItemNeedCreate,
  Dungeon,
  Boss,
  ItemProgress,
  Realm,
  CharacterGold,
  GoldSummary,
  GoldTransaction,
  GoldSnapshot
} from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 角色相关API
export const characterApi = {
  getAll: () => api.get<Character[]>('/characters'),
  getById: (id: string) => api.get<Character>(`/characters/${id}`),
  create: (data: CharacterCreate) => api.post<Character>('/characters', data),
  update: (id: string, data: CharacterCreate) => api.put<Character>(`/characters/${id}`, data),
  delete: (id: string) => api.delete(`/characters/${id}`),
  refreshLevels: () => api.post<{ success: boolean; message: string; updated: number; skipped: number }>('/characters/refresh-levels'),
  refreshAllData: () => api.post<{ success: boolean; message: string; total: number; success_count: number; failed_count: number; results: any[] }>('/character-refresh/refresh-all'),
  refreshSingle: (characterId: string) => api.post(`/character-refresh/${characterId}/refresh`),
  getTalents: (characterId: string) => api.get(`/characters/${characterId}/talents`)
}

// 装备需求相关API
export const itemNeedApi = {
  getAll: (params?: { character_id?: string; obtained?: boolean }) =>
    api.get<ItemNeed[]>('/item-needs', { params }),
  getById: (id: string) => api.get<ItemNeed>(`/item-needs/${id}`),
  create: (data: ItemNeedCreate) => api.post<ItemNeed>('/item-needs', data),
  update: (id: string, data: ItemNeedCreate) => api.put<ItemNeed>(`/item-needs/${id}`, data),
  markObtained: (id: string) => api.patch<ItemNeed>(`/item-needs/${id}/obtain`),
  delete: (id: string) => api.delete(`/item-needs/${id}`),
  getProgress: (characterId: string) => api.get<ItemProgress>(`/item-needs/character/${characterId}/progress`)
}

// 副本相关API
export const dungeonApi = {
  getAll: (params?: { expansion?: string; category?: string; phase?: string }) => api.get<Dungeon[]>('/dungeons/', { params }),
  getById: (id: string) => api.get<Dungeon>(`/dungeons/${id}`),
  importAtlasLoot: () => api.post<{ success: boolean; message: string; stats: { instances: number; bosses: number; items: number; loot: number } }>('/dungeons/import-atlasloot')
}

// Boss相关API
export const bossApi = {
  getAll: (params?: { dungeon_id?: number }) => api.get<Boss[]>('/bosses/', { params }),
  getById: (id: string) => api.get<Boss>(`/bosses/${id}`),
  getByDungeon: (dungeonId: number) => api.get<Boss[]>(`/bosses/dungeon/${dungeonId}/bosses`),
  lookupByBossId: (bossId: number) => api.get<Boss>(`/bosses/lookup/${bossId}`),
  getBossLoot: (bossId: number) => api.get(`/bosses/${bossId}/loot`),
  getItemDetail: (itemId: number) => api.get(`/bosses/item/${itemId}`)
}

// 服务器相关API
export const realmApi = {
  getAll: (params?: { classic?: boolean; region?: string }) =>
    api.get<Realm[]>('/realms', { params }),
  getById: (slug: string, params?: { classic?: boolean }) =>
    api.get<Realm>(`/realms/${slug}`, { params }),
  getClassicRealms: (params?: { region?: string }) =>
    api.get<Realm[]>('/realms/classic/list', { params }),
  getRetailRealms: (params?: { region?: string }) =>
    api.get<Realm[]>('/realms/retail/list', { params })
}

// 金币相关API
export const goldApi = {
  getAllGold: () => api.get<CharacterGold[]>('/gold/all'),
  getCharacterSummary: (characterId: string, timeMode?: string) =>
    api.get<GoldSummary>(`/gold/character/${characterId}`, { params: { time_mode: timeMode } }),
  getCharacterTransactions: (characterId: string, timeMode?: string) =>
    api.get<GoldTransaction[]>(`/gold/character/${characterId}/transactions`, { params: { time_mode: timeMode } }),
  getCharacterSnapshots: (characterId: string, limit?: number) =>
    api.get<GoldSnapshot[]>(`/gold/character/${characterId}/snapshots`, { params: { limit } }),
  refreshGold: () => api.post<{ success: boolean; message: string; characters: number; transactions: number }>('/gold/refresh'),
  // 图表数据API
  getMonthlyStats: (period?: string) =>
    api.get(`/gold/stats/monthly`, { params: { period } }),
  getCharacterStats: () => api.get(`/gold/stats/characters`),
  getGoldTimeline: (characterId?: number) =>
    api.get(`/gold/stats/timeline`, { params: { character_id: characterId } }),
  // 每日快照API
  createDailySnapshot: () => api.post(`/gold/snapshot/daily`),
  getDailyStats: (characterId?: number) =>
    api.get(`/gold/stats/daily`, { params: { character_id: characterId } })
}

// 装备相关API
export const equipmentApi = {
  getCharacterEquipment: (characterId: string) => 
    api.get(`/characters/${characterId}/equipment`),
  syncEquipment: (characterId: string, data: any) => 
    api.post(`/characters/${characterId}/equipment/sync`, data),
  getEquipmentSlots: () => 
    api.get('/characters/equipment/slots'),
  getCharacterItemSets: (characterId: string) =>
    api.get(`/characters/${characterId}/item-sets`)
}

// 天赋相关API
export const talentApi = {
  getClasses: () => api.get('/talents/classes'),
  getClassTrees: (className: string) => api.get(`/talents/trees/${className}`),
  getTalentTree: (treeId: number) => api.get(`/talents/tree/${treeId}`),
  getTalentTreeBySpec: (className: string, specName: string) => 
    api.get(`/talents/tree/${className}/${specName}`),
  
  // 配点方案
  getBuilds: (params?: { class_name?: string; spec_name?: string }) => 
    api.get('/talents/builds', { params }),
  getBuild: (id: number) => api.get(`/talents/builds/${id}`),
  createBuild: (data: { name: string; class_name: string; spec_name: string; points: Record<string, number>; notes?: string }) => 
    api.post('/talents/builds', data),
  deleteBuild: (id: number) => api.delete(`/talents/builds/${id}`),
  uploadBuildImage: (id: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/talents/builds/${id}/upload-image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  }
}

// 物品相关API
export const itemApi = {
  getById: (itemId: number) => api.get(`/items/${itemId}`),
  getBatch: (itemIds: number[]) => api.post('/items/batch', itemIds)
}

// BiS 毕业装备相关API
export const bisApi = {
  getClasses: () => api.get('/bis/classes'),
  getBisList: (params: { class_name: string; spec_name: string; phase: string; max_rank?: number }) =>
    api.get('/bis/', { params }),
  importToNeeds: (characterId: number, data: { class_name: string; spec_name: string; phase: string; max_rank?: number }) =>
    api.post(`/bis/import-needs/${characterId}`, data),
  compareCharacter: (characterId: string) =>
    api.get(`/bis/compare/${characterId}`)
}

// 时光徽章 & 兑换相关API
export const exchangeApi = {
  getCurrentToken: () => api.get('/exchange/token/current'),
  getTokenHistory: (limit?: number) => api.get('/exchange/token/history', { params: { limit } }),
  recordToken: (price_gold: number, notes?: string) =>
    api.post('/exchange/token/record', null, { params: { price_gold, notes } }),
  getCurrentRate: () => api.get('/exchange/rate/current'),
  getRateHistory: (limit?: number) => api.get('/exchange/rate/history', { params: { limit } }),
  recordRate: (gold_per_cny: number, notes?: string) =>
    api.post('/exchange/rate/record', null, { params: { gold_per_cny, notes } }),
  calculate: (params: { gold?: number; cny?: number }) =>
    api.get('/exchange/calculate', { params })
}

export default api