import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { characterApi } from '@/api'
import type { Character, CharacterCreate } from '@/types'

export const useCharacterStore = defineStore('character', () => {
  // 状态
  const characters = ref<Character[]>([])
  const currentCharacter = ref<Character | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const characterCount = computed(() => characters.value.length)
  const hasCharacters = computed(() => characters.value.length > 0)

  // 方法
  async function fetchCharacters() {
    loading.value = true
    error.value = null
    try {
      const response = await characterApi.getAll()
      characters.value = response.data
    } catch (err) {
      error.value = '获取角色列表失败'
      console.error('Failed to fetch characters:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchCharacter(id: string) {
    loading.value = true
    error.value = null
    try {
      const response = await characterApi.getById(id)
      currentCharacter.value = response.data
      return response.data
    } catch (err) {
      error.value = '获取角色信息失败'
      console.error('Failed to fetch character:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function createCharacter(data: CharacterCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await characterApi.create(data)
      characters.value.push(response.data)
      return response.data
    } catch (err) {
      error.value = '创建角色失败'
      console.error('Failed to create character:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateCharacter(id: string, data: CharacterCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await characterApi.update(id, data)
      const index = characters.value.findIndex(c => c.id === id)
      if (index !== -1) {
        characters.value[index] = response.data
      }
      if (currentCharacter.value?.id === id) {
        currentCharacter.value = response.data
      }
      return response.data
    } catch (err) {
      error.value = '更新角色失败'
      console.error('Failed to update character:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCharacter(id: string) {
    loading.value = true
    error.value = null
    try {
      await characterApi.delete(id)
      characters.value = characters.value.filter(c => c.id !== id)
      if (currentCharacter.value?.id === id) {
        currentCharacter.value = null
      }
    } catch (err) {
      error.value = '删除角色失败'
      console.error('Failed to delete character:', err)
      throw err
    } finally {
      loading.value = false
    }
  }

  function setCurrentCharacter(character: Character | null) {
    currentCharacter.value = character
  }

  return {
    // 状态
    characters,
    currentCharacter,
    loading,
    error,
    // 计算属性
    characterCount,
    hasCharacters,
    // 方法
    fetchCharacters,
    fetchCharacter,
    createCharacter,
    updateCharacter,
    deleteCharacter,
    setCurrentCharacter
  }
})