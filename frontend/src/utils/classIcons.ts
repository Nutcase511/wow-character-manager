// 职业名称到图标路径的映射
export const classIconMap: Record<string, string> = {
  'warrior': '战士',
  'paladin': '圣骑士',
  'hunter': '猎人',
  'rogue': '盗贼',
  'priest': '牧师',
  'shaman': '萨满祭司',
  'mage': '法师',
  'warlock': '术士',
  'monk': '武僧',
  'druid': '德鲁伊',
  'death_knight': '死亡骑士',
  'demon_hunter': '恶魔猎手',
  'evoker': '唤魔师',
  '战士': '战士',
  '圣骑士': '圣骑士',
  '猎人': '猎人',
  '盗贼': '盗贼',
  '牧师': '牧师',
  '萨满祭司': '萨满祭司',
  '法师': '法师',
  '术士': '术士',
  '武僧': '武僧',
  '德鲁伊': '德鲁伊',
  '死亡骑士': '死亡骑士',
  '恶魔猎手': '恶魔猎手',
  '唤魔师': '唤魔师',
  '未知': '战士'
}

// 阵营图标映射
export const factionIconMap: Record<string, string> = {
  'alliance': '联盟',
  'horde': '部落',
  '联盟': '联盟',
  '部落': '部落',
  '未知': '联盟'
}

// 获取职业图标路径
export function getClassIcon(className: string): string {
  const iconName = classIconMap[className] || '战士'
  return `/images/${iconName}.webp`
}

// 获取阵营图标路径
export function getFactionIcon(faction: string): string {
  const iconName = factionIconMap[faction] || '联盟'
  return `/images/${iconName}.webp`
}

// 获取职业中文名称
export function getClassNameCN(className: string): string {
  const classNames: Record<string, string> = {
    'warrior': '战士',
    'paladin': '圣骑士',
    'hunter': '猎人',
    'rogue': '盗贼',
    'priest': '牧师',
    'shaman': '萨满祭司',
    'mage': '法师',
    'warlock': '术士',
    'monk': '武僧',
    'druid': '德鲁伊',
    'death_knight': '死亡骑士',
    'demon_hunter': '恶魔猎手',
    'evoker': '唤魔师'
  }
  return classNames[className] || className
}
