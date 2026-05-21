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
  expansion: string
  category: string
  phase?: string
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

// 金币相关类型
export interface CharacterGold {
  id: string
  character_id: string
  character_name: string
  realm: string
  current_gold: number
  last_updated: string
}

export interface GoldTransaction {
  id: string
  character_id: string
  source: string
  source_title: string
  time_mode: string
  amount_in: number
  amount_out: number
  recorded_at: string
}

export interface GoldSnapshot {
  id: string
  character_id: string
  gold_amount: number
  snapshot_date: string
}

export interface GoldSummary {
  character_gold?: CharacterGold | null
  total_in: number
  total_out: number
  net: number
  transactions: GoldTransaction[]
}

export interface TokenPrice {
  id: number
  price_gold: number
  source: string
  notes?: string
  recorded_at: string
}

export interface ExchangeRate {
  id: number
  gold_per_cny: number
  source: string
  notes?: string
  recorded_at: string
}

export interface ExchangeResult {
  gold: number | null
  cny: number | null
  rate: number
  token_price: number | null
  token_count: number | null
  message?: string
}

export const TimeModes = ['Session', 'Day', 'Week', 'Total'] as const
export const TimeModeLabels: Record<string, string> = {
  'Session': '本次会话',
  'Day': '今日',
  'Week': '本周',
  'Total': '总计'
}

// BiS 毕业装备相关类型
export interface BiSItem {
  id: number
  class_name: string
  spec_name: string
  phase: string
  slot: string
  rank: number
  item_id: number
  item_name: string | null
  quality: string | null
  item_level: number | null
  icon_url: string | null
  stats: string | null
  source: string | null
  boss_name: string | null
  dungeon_name: string | null
}

export interface BiSClasses {
  [className: string]: {
    [specName: string]: string[]
  }
}

// BiS 职业名称映射（bis_lists 缩写 → 显示名）
export const BisClassNameMap: Record<string, string> = {
  'dk': '死亡骑士',
  'druid': '德鲁伊',
  'hunter': '猎人',
  'mage': '法师',
  'paladin': '圣骑士',
  'priest': '牧师',
  'rogue': '潜行者',
  'shaman': '萨满',
  'warlock': '术士',
  'warrior': '战士'
}

// BiS 职业缩写 → characters 表 wow_class 映射
export const BisClassToCharClass: Record<string, string> = {
  'dk': 'death_knight',
  'druid': 'druid',
  'hunter': 'hunter',
  'mage': 'mage',
  'paladin': 'paladin',
  'priest': 'priest',
  'rogue': 'rogue',
  'shaman': 'shaman',
  'warlock': 'warlock',
  'warrior': 'warrior'
}

// BiS 天赋中文名映射
export const SpecNameMap: Record<string, string> = {
  // DK
  'Blood dps': '鲜血DPS',
  'Blood tank': '鲜血坦克',
  'Frost': '冰霜',
  'Unholy': '邪恶',
  // Druid
  'Balance': '平衡',
  'Feral dps': '野性DPS',
  'Feral tank': '野性坦克',
  'Restoration': '恢复',
  // Hunter
  'Beast mastery': '野兽控制',
  'Marksmanship': '射击',
  'Survival': '生存',
  // Mage
  'Arcane': '奥术',
  'Fire': '火焰',
  'Fire FFB': '霜火',
  // Paladin
  'Holy': '神圣',
  'Protection': '防护',
  'Retribution': '惩戒',
  // Priest
  'Discipline': '戒律',
  'Shadow': '暗影',
  // Rogue
  'Assassination': '刺杀',
  'Combat': '战斗',
  'Subtlety': '敏锐',
  // Shaman
  'Elemental': '元素',
  'Enhancement': '增强',
  // Warlock
  'Affliction': '痛苦',
  'Demonology': '恶魔学识',
  'Destruction': '毁灭',
  // Warrior
  'Arms': '武器',
  'Fury': '狂暴'
}

// 装备部位中文名
export const SlotNameMap: Record<string, string> = {
  'Head': '头部',
  'Neck': '颈部',
  'Shoulder': '肩部',
  'Back': '背部',
  'Chest': '胸部',
  'Wrist': '手腕',
  'Hands': '手套',
  'Waist': '腰部',
  'Legs': '腿部',
  'Feet': '脚部',
  'Finger': '手指',
  'Trinket': '饰品',
  'Weapon': '武器',
  'Off hand': '副手',
  'Ranged': '远程',
  'Relic': '圣物'
}

// 阶段中文名
export const PhaseNameMap: Record<string, string> = {
  'PR': '团本前',
  'P1': 'P1',
  'P2': 'P2',
  'P3': 'P3',
  'P4': 'P4',
  'P5': 'P5',
  'P6': 'P6',
  'P7': 'P7',
  'P8': 'P8',
  'P9': 'P9',
  'P10': 'P10',
  'P11': 'P11'
}