"""生成60/70级团本物品ID Lua文件"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

raid_ids = [409, 469, 509, 531, 249, 129, 43, 604,
            532, 550, 548, 564, 534, 565, 544, 568, 289, 230, 229]

all_ids = set()
for did in raid_ids:
    c.execute("""
        SELECT DISTINCT bl.item_id
        FROM boss_loot bl
        JOIN bosses b ON bl.boss_id = b.boss_id
        WHERE b.dungeon_id = ?
    """, (did,))
    for r in c.fetchall():
        all_ids.add(r[0])

sorted_ids = sorted(all_ids)

output_path = r'c:\wow后台管理\wow-character-manager\IconCollector\_raid_item_ids.lua'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write('-- 60/70级团本物品ID列表 (自动生成)\n')
    f.write(f'-- 总计: {len(sorted_ids)} 个物品\n')
    f.write('RAID_ITEM_IDS = {\n')
    for i in range(0, len(sorted_ids), 20):
        batch = sorted_ids[i:i+20]
        f.write('    ' + ', '.join([str(x) for x in batch]) + ',\n')
    f.write('}\n')

print(f'已生成 {output_path} ({len(sorted_ids)} 个物品)')
db.close()