import axios from 'axios'
import type {
  Character,
  CharacterCreate,
  ItemNeed,
  ItemNeedCreate,
  Dungeon,
  Boss,
  ItemProgress,
  Realm
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
  (response) => response,
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
  delete: (id: string) => api.delete(`/characters/${id}`)
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
  getAll: () => api.get<Dungeon[]>('/dungeons'),
  getById: (id: string) => api.get<Dungeon>(`/dungeons/${id}`),
  create: (data: Partial<Dungeon>) => api.post<Dungeon>('/dungeons', data),
  syncFromBlizzard: (journalInstanceId: number) => api.post<Dungeon>(`/dungeons/sync/${journalInstanceId}`),
  delete: (id: string) => api.delete(`/dungeons/${id}`)
}

// Boss相关API
export const bossApi = {
  getAll: (params?: { dungeon_id?: number }) => api.get<Boss[]>('/bosses', { params }),
  getById: (id: string) => api.get<Boss>(`/bosses/${id}`),
  create: (data: Partial<Boss>) => api.post<Boss>('/bosses', data),
  syncFromBlizzard: (journalEncounterId: number) => api.post<Boss>(`/bosses/sync/${journalEncounterId}`),
  getByDungeon: (dungeonId: number) => api.get<Boss[]>(`/bosses/dungeon/${dungeonId}/bosses`),
  delete: (id: string) => api.delete(`/bosses/${id}`)
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

export default api