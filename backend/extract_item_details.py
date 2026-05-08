"""
从AtlasLoot插件提取装备详细信息
包括属性、物品等级、品质等
"""
import os
import re
import sqlite3
import json

# 装备品质映射
QUALITY_MAP = {
    "Poor": "poor",
    "Common": "common",
    "Uncommon": "uncommon",
    "Rare": "rare",
    "Epic": "epic",
    "Legendary": "legendary",
    "Artifact": "legendary"
}

# 部位映射
SLOT_MAP = {
    "头": "head", "头部": "head", "Head": "head",
    "项链": "neck", "Neck": "neck",
    "肩": "shoulder", "肩部": "shoulder", "Shoulder": "shoulder",
    "背": "back", "披风": "back", "Back": "back",
    "胸": "chest", "胸部": "chest", "Chest": "chest",
    "腕": "wrist", "护腕": "wrist", "Wrist": "wrist",
    "手": "hands", "手套": "hands", "手套": "hands", "Hands": "hands",
    "腰": "waist", "腰带": "waist", "Waist": "waist",
    "腿": "legs", "腿部": "legs", "Legs": "legs",
    "脚": "feet", "靴子": "feet", "Feet": "feet",
    "手指": "finger", "戒指": "finger", "Finger": "finger",
    "饰品": "trinket", "Trinket": "trinket",
    "主手": "mainhand", "Main Hand": "mainhand",
    "副手": "offhand", "Off Hand": "offhand",
    "双手": "twohand", "Two-Hand": "twohand",
    "远程": "ranged", "Ranged": "ranged",
    "圣物": "relic", "Relic": "relic"
}

# 属性名称映射
STAT_MAP = {
    "力量": "strength", "Strength": "strength",
    "敏捷": "agility", "Agility": "agility",
    "智力": "intellect", "Intellect": "intellect",
    "耐力": "stamina", "Stamina": "stamina",
    "精神": "spirit", "Spirit": "spirit",
    "攻击强度": "attack_power", "Attack Power": "attack_power",
    "法术强度": "spell_power", "Spell Power": "spell_power",
    "急速": "haste", "Haste": "haste",
    "暴击": "crit", "Critical Strike": "crit",
    "精通": "mastery", "Mastery": "mastery",
    "全能": "versatility", "Versatility": "versatility",
    "法术穿透": "spell_penetration",
    "护甲穿透": "armor_penetration",
    "躲闪": "dodge", "Dodge": "dodge",
    "招架": "parry", "Parry": "parry",
    "格挡": "block", "Block": "block",
    "韧性": "resilience", "Resilience": "resilience",
    "命中": "hit", "Hit": "hit",
    "精准": "expertise", "Expertise": "expertise",
    "生命": "health", "Health": "health",
    "法力": "mana", "Mana": "mana",
    "护甲": "armor", "Armor": "armor"
}

def find_atlasloot_files(base_path):
    """查找AtlasLoot插件文件"""
    atlasloot_dir = os.path.join(base_path, 'Interface', 'AddOns', 'AtlasLootClassic')
    files = []
    
    if os.path.exists(atlasloot_dir):
        for root, dirs, filenames in os.walk(atlasloot_dir):
            for filename in filenames:
                if filename.endswith('.lua') and ('Item' in filename or 'Loot' in filename):
                    files.append(os.path.join(root, filename))
    
    return files

def parse_lua_table(lua_str):
    """解析Lua表为Python字典"""
    result = {}
    lua_str = lua_str.strip()
    
    if not lua_str.startswith('{') or not lua_str.endswith('}'):
        return result
    
    content = lua_str[1:-1]
    depth = 0
    current_key = None
    current_value = ''
    in_string = False
    escape = False
    
    i = 0
    while i < len(content):
        char = content[i]
        
        if escape:
            current_value += char
            escape = False
            i += 1
            continue
        
        if char == '\\':
            escape = True
            i += 1
            continue
        
        if char == '"':
            in_string = not in_string
            i += 1
            continue
        
        if in_string:
            current_value += char
            i += 1
            continue
        
        if char == '{':
            depth += 1
            current_value += char
            i += 1
            continue
        
        if char == '}':
            depth -= 1
            current_value += char
            if depth == 0:
                result[current_key] = parse_lua_table(current_value)
                current_key = None
                current_value = ''
            else:
                current_value += char
            i += 1
            continue
        
        if depth == 0:
            if char == '=':
                current_key = current_value.strip()
                current_value = ''
                i += 1
                continue
            
            if char == ',' or char == '\n' or char == ';':
                if current_key is not None and current_value:
                    result[current_key] = current_value.strip()
                    current_key = None
                    current_value = ''
                i += 1
                continue
        
        current_value += char
        i += 1
    
    return result

def extract_item_from_lua(filepath):
    """从Lua文件提取装备数据"""
    items = {}
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 查找装备数据模式
        patterns = [
            r'AtlasLoot\.Items\[(\d+)\]\s*=\s*\{([^}]+)\}',
            r'\[(\d+)\]\s*=\s*\{([^}]+)\}',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.DOTALL)
            for item_id, item_data in matches:
                try:
                    item_id = int(item_id)
                    item_info = parse_lua_table('{' + item_data + '}')
                    
                    if item_info:
                        item = {
                            'item_id': item_id,
                            'name': item_info.get('name', '').replace('"', ''),
                            'quality': item_info.get('quality', 'common'),
                            'item_level': int(item_info.get('level', '0')),
                            'slot': item_info.get('slot', ''),
                            'stats': {},
                            'icon_url': ''
                        }
                        
                        # 解析属性
                        if 'stats' in item_info:
                            stats_str = item_info['stats']
                            stat_matches = re.findall(r'(\d+)\s+(.+)', stats_str)
                            for value, stat_name in stat_matches:
                                stat_key = STAT_MAP.get(stat_name.strip(), stat_name.strip())
                                item['stats'][stat_key] = int(value)
                        
                        items[item_id] = item
                except:
                    continue
    
    except Exception as e:
        print(f"解析文件失败 {filepath}: {e}")
    
    return items

def update_database(items, db_path):
    """更新数据库中的装备信息"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    updated = 0
    inserted = 0
    
    for item_id, item in items.items():
        # 转换品质
        quality = QUALITY_MAP.get(item['quality'], 'common').lower()
        
        # 转换部位
        slot = ''
        for key, value in SLOT_MAP.items():
            if key.lower() in item['slot'].lower():
                slot = value
                break
        
        # 检查是否已存在
        cursor.execute('SELECT id FROM items WHERE item_id = ?', (item_id,))
        existing = cursor.fetchone()
        
        stats_json = json.dumps(item['stats'])
        
        if existing:
            # 更新
            cursor.execute('''
                UPDATE items SET name = ?, quality = ?, item_level = ?, slot = ?, stats = ?
                WHERE item_id = ?
            ''', (item['name'], quality, item['item_level'], slot, stats_json, item_id))
            updated += 1
        else:
            # 插入
            cursor.execute('''
                INSERT INTO items (item_id, name, quality, item_level, slot, stats)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (item_id, item['name'], quality, item['item_level'], slot, stats_json))
            inserted += 1
    
    conn.commit()
    conn.close()
    
    print(f"更新完成: 更新 {updated} 条，插入 {inserted} 条")
    return updated + inserted

def main():
    # 游戏目录
    wow_path = r'C:\WOW\World of Warcraft\_classic_'
    
    # 查找AtlasLoot文件
    files = find_atlasloot_files(wow_path)
    print(f"找到 {len(files)} 个AtlasLoot文件")
    
    if not files:
        print("未找到AtlasLoot插件文件")
        return
    
    # 提取装备数据
    all_items = {}
    for filepath in files:
        print(f"处理: {os.path.basename(filepath)}")
        items = extract_item_from_lua(filepath)
        all_items.update(items)
    
    print(f"\n总计提取到 {len(all_items)} 个装备")
    
    # 更新数据库
    db_path = os.path.join(os.path.dirname(__file__), 'wow_character_manager.db')
    update_database(all_items, db_path)

if __name__ == '__main__':
    main()
