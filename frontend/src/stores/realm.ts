import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { realmApi } from '@/api'
import type { Realm } from '@/types'

export const useRealmStore = defineStore('realm', () => {
  // 状态
  const realms = ref<Realm[]>([])
  const classicRealms = ref<Realm[]>([])
  const retailRealms = ref<Realm[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const realmCount = computed(() => realms.value.length)
  const classicRealmCount = computed(() => classicRealms.value.length)
  const retailRealmCount = computed(() => retailRealms.value.length)
  const hasRealms = computed(() => realms.value.length > 0)

  // 方法
  async function fetchRealms(params?: { classic?: boolean; region?: string }) {
    loading.value = true
    error.value = null
    try {
      const response = await realmApi.getAll(params)
      realms.value = response.data
      return response.data
    } catch (err) {
      error.value = '获取服务器列表失败'
      console.error('Failed to fetch realms:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchClassicRealms(region?: string) {
    loading.value = true
    error.value = null
    try {
      const response = await realmApi.getClassicRealms({ region })
      classicRealms.value = response.data
      return response.data
    } catch (err) {
      error.value = '获取怀旧服服务器列表失败'
      console.error('Failed to fetch classic realms:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRetailRealms(region?: string) {
    loading.value = true
    error.value = null
    try {
      const response = await realmApi.getRetailRealms({ region })
      retailRealms.value = response.data
      return response.data
    } catch (err) {
      error.value = '获取正式服服务器列表失败'
      console.error('Failed to fetch retail realms:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchRealm(slug: string, classic: boolean = false) {
    loading.value = true
    error.value = null
    try {
      const response = await realmApi.getById(slug, { classic })
      return response.data
    } catch (err) {
      error.value = '获取服务器信息失败'
      console.error('Failed to fetch realm:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function searchRealms(query: string, realmList: Realm[] = realms.value): Realm[] {
    if (!query.trim()) {
      return realmList
    }

    const lowerQuery = query.toLowerCase()
    return realmList.filter(realm =>
      realm.name.toLowerCase().includes(lowerQuery) ||
      realm.slug.toLowerCase().includes(lowerQuery)
    )
  }

  function getRealmByName(name: string): Realm | undefined {
    return realms.value.find(realm => realm.name === name)
  }

  function getRealmBySlug(slug: string): Realm | undefined {
    return realms.value.find(realm => realm.slug === slug)
  }

  function getRealmsByRegion(region: string): Realm[] {
    return realms.value.filter(realm => realm.region === region.toLowerCase())
  }

  function getRealmsByCategory(category: string): Realm[] {
    return realms.value.filter(realm => realm.category === category)
  }

  return {
    // 状态
    realms,
    classicRealms,
    retailRealms,
    loading,
    error,
    // 计算属性
    realmCount,
    classicRealmCount,
    retailRealmCount,
    hasRealms,
    // 方法
    fetchRealms,
    fetchClassicRealms,
    fetchRetailRealms,
    fetchRealm,
    searchRealms,
    getRealmByName,
    getRealmBySlug,
    getRealmsByRegion,
    getRealmsByCategory
  }
})