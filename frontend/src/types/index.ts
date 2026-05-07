// 角色相关类型
export interface Character {
  id: string
  name: string
  realm: string
  wow_class: string
  spec?: string
  level: number
  faction: string
  created_at: string
  updated_at: string
}

export interface CharacterCreate {
  name: string
  realm: string
  wow_class: string
  spec?: string
  level: number
  faction: string
}

// 装备相关类型
export interface Item {
  id: string
  item_id: number
  name: string
  quality: string
  item_level: number
  slot?: string
  stats: Record<string, number>
  icon_url?: string
  created_at: string
}

export interface ItemNeed {
  id: string
  character_id: string
  item_id: number
  item_name: string
  boss_id?: number
  boss_name?: string
  dungeon_name?: string
  priority: number
  obtained: boolean
  notes?: string
  created_at: string
  updated_at: string
}

export interface ItemNeedCreate {
  character_id: string
  item_id: number
  item_name: string
  boss_id?: number
  boss_name?: string
  dungeon_name?: string
  priority: number
  obtained: boolean
  notes?: string
}

// 副本相关类型
export interface Dungeon {
  id: string
  dungeon_id: number
  name: string
  description?: string
  map_name?: string
  minimum_level: number
  modes: string[]
  icon_url?: string
  created_at: string
}

// Boss相关类型
export interface Boss {
  id: string
  boss_id: number
  name: string
  description?: string
  dungeon_id: number
  dungeon_name: string
  category?: string
  icon_url?: string
  created_at: string
}

// 进度相关类型
export interface ItemProgress {
  character_id: string
  character_name: string
  total_needs: number
  obtained: number
  remaining: number
  progress_percentage: number
}

// 职业枚举
export enum WoWClass {
  WARRIOR = 'warrior',
  PALADIN = 'paladin',
  HUNTER = 'hunter',
  ROGUE = 'rogue',
  PRIEST = 'priest',
  DEATH_KNIGHT = 'death_knight',
  SHAMAN = 'shaman',
  MAGE = 'mage',
  WARLOCK = 'warlock',
  MONK = 'monk',
  DRUID = 'druid',
  DEMON_HUNTER = 'demon_hunter',
  EVOKER = 'evoker'
}

// 装备品质枚举
export enum ItemQuality {
  POOR = 'poor',
  COMMON = 'common',
  UNCOMMON = 'uncommon',
  RARE = 'rare',
  EPIC = 'epic',
  LEGENDARY = 'legendary'
}

// 服务器相关类型
export interface Realm {
  id: number
  name: string
  slug: string
  category: string
  locale: string
  timezone: string
  is_tournament: boolean
  region: string
}

// 职业与专精映射关系
export const ClassSpecsMap: Record<string, string[]> = {
  [WoWClass.WARRIOR]: ['防护', '武器', '狂暴'],
  [WoWClass.PALADIN]: ['神圣', '惩戒', '防护'],
  [WoWClass.HUNTER]: ['野兽', '射击', '生存'],
  [WoWClass.ROGUE]: ['刺杀', '战斗', '敏锐'],
  [WoWClass.PRIEST]: ['戒律', '神圣', '暗影'],
  [WoWClass.DEATH_KNIGHT]: ['鲜血', '冰霜', '邪恶'],
  [WoWClass.SHAMAN]: ['元素', '增强', '恢复'],
  [WoWClass.MAGE]: ['奥术', '火焰', '冰霜'],
  [WoWClass.WARLOCK]: ['痛苦', '恶魔', '毁灭'],
  [WoWClass.MONK]: ['酒仙', '织雾', '踏风'],
  [WoWClass.DRUID]: ['平衡', '野性', '守护', '恢复'],
  [WoWClass.DEMON_HUNTER]: ['浩劫', '复仇'],
  [WoWClass.EVOKER]: ['增辉', '湮灭', '恩护']
}