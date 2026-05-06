import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { itemNeedApi } from '@/api'
import type { ItemNeed, ItemNeedCreate, ItemProgress } from '@/types'

export const useItemNeedStore = defineStore('itemNeed', () => {
  // 状态
  const itemNeeds = ref<ItemNeed[]>([])
  const currentProgress = ref<ItemProgress | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const totalNeeds = computed(() => itemNeeds.value.length)
  const obtainedNeeds = computed(() => itemNeeds.value.filter(item => item.obtained))
  const pendingNeeds = computed(() => itemNeeds.value.filter(item => !item.obtained))

  // 方法
  async function fetchItemNeeds(params?: { character_id?: string; obtained?: boolean }) {
    loading.value = true
    error.value = null
    try {
      const response = await itemNeedApi.getAll(params)
      itemNeeds.value = response.data
    } catch (err) {
      error.value = '获取装备需求失败'
      console.error('Failed to fetch item needs:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchItemNeed(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await itemNeedApi.getById(id)
      return response.data
    } catch (err) {
      error.value = '获取装备需求失败'
      console.error('Failed to fetch item need:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createItemNeed(data: ItemNeedCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await itemNeedApi.create(data)
      itemNeeds.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = '创建装备需求失败'
      console.error('Failed to create item need:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateItemNeed(id: string, data: ItemNeedCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await itemNeedApi.update(id, data)
      const index = itemNeeds.value.findIndex(item => item.id === id)
      if (index !== -1) {
        itemNeeds.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = '更新装备需求失败'
      console.error('Failed to update item need:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function markAsObtained(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await itemNeedApi.markObtained(id)
      const index = itemNeeds.value.findIndex(item => item.id === id)
      if (index !== -1) {
        itemNeeds.value[index] = response.data
      }
      return response.data
    } catch (err) {
      error.value = '标记装备获取失败'
      console.error('Failed to mark item as obtained:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteItemNeed(id: string) {
    loading.value = true
    error.value = null
    try {
      await itemNeedApi.delete(id)
      itemNeeds.value = itemNeeds.value.filter(item => item.id !== id)
    } catch (err) {
      error.value = '删除装备需求失败'
      console.error('Failed to delete item need:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchProgress(characterId: string) {
    loading.value = true
    error.value = null
    try {
      const response = await itemNeedApi.getProgress(characterId)
      currentProgress.value = response.data
      return response.data
    } catch (err) {
      error.value = '获取进度失败'
      console.error('Failed to fetch progress:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function filterByCharacter(characterId: string) {
    return itemNeeds.value.filter(item => item.character_id === characterId)
  }

  function filterByStatus(obtained: boolean) {
    return itemNeeds.value.filter(item => item.obtained === obtained)
  }

  return {
    // 状态
    itemNeeds,
    currentProgress,
    loading,
    error,
    // 计算属性
    totalNeeds,
    obtainedNeeds,
    pendingNeeds,
    // 方法
    fetchItemNeeds,
    fetchItemNeed,
    createItemNeed,
    updateItemNeed,
    markAsObtained,
    deleteItemNeed,
    fetchProgress,
    filterByCharacter,
    filterByStatus
  }
})