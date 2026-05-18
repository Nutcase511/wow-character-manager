"""修复: 1. 十字军的试炼设为P4  2. 从AtlasLoot提取ZG物品英文名"""
import re
import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'
DATA_FILE = r'C:\WOW\World of Warcraft\_classic_titan_\Interface\AddOns\AtlasLootMY_DungeonsAndRaids\data.lua'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 1. 十字军的试炼 -> P4
print("=== 修复1: 十字军的试炼设为P4 ===")
c.execute("UPDATE dungeons SET phase = 'P4' WHERE dungeon_id = 4722")
print("  已设 phase='P4'")

# 2. 从data.lua行提取ZG物品名
print("\n=== 修复2: 提取祖尔格拉布物品名称 ===")
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到Zul'Gurub区块起点
zg_pos = content.find('data["Zul\'Gurub"]')
if zg_pos == -1:
    print("未找到Zul'Gurub数据块")
else:
    items_pos = content.find('items = {', zg_pos)
    brace_pos = content.find('{', items_pos + 8)
    if brace_pos == -1:
        print("未找到items块")
    else:
        depth = 0
        for i in range(brace_pos, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    block = content[brace_pos:i+1]
                    break
        
        # 从block中按行解析
        items_found = {}
        for line in block.split('\n'):
            # 匹配 { index, item_id }  -- Name
            m = re.match(r'\s*\{\s*(\d+)\s*,\s*(\d+)\s*\}\s*,?\s*--\s*(.+)', line)
            if m:
                item_id = int(m.group(2))
                item_name = m.group(3).strip()
                items_found[item_id] = item_name

        print(f"从插件提取到 {len(items_found)} 个ZG物品名称")

        updated = 0
        inserted = 0
        for item_id, name in items_found.items():
            c.execute("SELECT name FROM items WHERE item_id = ?", (item_id,))
            row = c.fetchone()
            if row:
                if not row[0] or '未知' in (row[0] or ''):
                    c.execute("UPDATE items SET name = ? WHERE item_id = ?", (name, item_id))
                    if c.rowcount > 0:
                        updated += 1
            else:
                c.execute("INSERT INTO items (item_id, name, quality, item_level, icon_url, stats, slot) VALUES (?, ?, 'uncommon', 0, '', '{}', '')",
                         (item_id, name))
                inserted += 1

        print(f"  items表更新: {updated} 条, 新增: {inserted} 条")

# 检查结果
print("\n=== 验证结果 ===")
c.execute("""
    SELECT COUNT(*) FROM boss_loot bl
    JOIN bosses b ON bl.boss_id = b.boss_id
    LEFT JOIN items i ON bl.item_id = i.item_id
    WHERE b.dungeon_id = 309 AND (i.name IS NULL OR i.name = '')
""")
still_missing = c.fetchone()[0]
print(f"  祖尔格拉布仍有名称缺失的掉落: {still_missing} 条")

db.commit()
db.close()
print("\n搞定!")