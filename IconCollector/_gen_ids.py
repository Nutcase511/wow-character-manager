import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('backend/wow_character_manager.db')

# 获取使用泛用CDN图标的物品（需要游戏插件提供准确图标）
cur = conn.execute("""
    SELECT item_id FROM items 
    WHERE icon_url LIKE '%render.worldofwarcraft.com%'
    ORDER BY item_id
""")
rows = cur.fetchall()
print(f'使用CDN泛用图标（需要游戏插件补全）: {len(rows)} 个')

ids = [r[0] for r in rows]
print('local MISSING_ITEM_IDS = {')
for i in range(0, len(ids), 20):
    chunk = ids[i:i+20]
    print('    ' + ', '.join(str(x) for x in chunk) + ',')
print('}')
print(f'\n-- 总计 {len(ids)} 个物品ID')

conn.close()