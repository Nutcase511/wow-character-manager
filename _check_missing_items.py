import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 装备表7个缺失物品在bis_lists中是否有数据？
print('=== 7个装备物品在BiS表中是否存在 ===')
c.execute("SELECT DISTINCT item_id, item_name, slot, quality, item_level, icon_url FROM bis_lists WHERE item_id IN (9767, 14168, 14370, 38042, 38219, 41763, 44400) ORDER BY item_id")
rows = c.fetchall()
if rows:
    for r in rows:
        print(f'  ID={r[0]}, 名称={r[1]}, 槽位={r[2]}, 品质={r[3]}, 装等={r[4]}, 图标={r[5]}')
else:
    print('  均不存在于BiS表')

# BiS缺失物品 - 检查是否有真实数据
print('\n=== BiS缺失物品数据采样 ===')
c.execute("""
    SELECT item_id, item_name, slot, quality, item_level, icon_url, source, dungeon_name
    FROM bis_lists
    WHERE item_id IN (
        SELECT DISTINCT b.item_id FROM bis_lists b
        LEFT JOIN items i ON b.item_id = i.item_id
        WHERE i.item_id IS NULL
    )
    GROUP BY item_id
    HAVING item_name IS NOT NULL AND item_name != ''
    LIMIT 20
""")
rows = c.fetchall()
print(f'有真实名称的BiS物品(采样20个):')
for r in rows[:10]:
    print(f'  ID={r[0]}, 名称={r[1]}, 槽位={r[2]}, 品质={r[3]}, 装等={r[4]}, 图标={r[5]}, 来源={r[6]}')

# 统计BiS缺失物品中有完整数据的
c.execute("""
    SELECT COUNT(DISTINCT b.item_id)
    FROM bis_lists b
    LEFT JOIN items i ON b.item_id = i.item_id
    WHERE i.item_id IS NULL
    AND b.item_name IS NOT NULL AND b.item_name != ''
""")
with_name = c.fetchone()[0]

c.execute("""
    SELECT COUNT(DISTINCT b.item_id)
    FROM bis_lists b
    LEFT JOIN items i ON b.item_id = i.item_id
    WHERE i.item_id IS NULL
    AND b.icon_url IS NOT NULL AND b.icon_url != ''
""")
with_icon = c.fetchone()[0]

c.execute("""
    SELECT COUNT(DISTINCT b.item_id)
    FROM bis_lists b
    LEFT JOIN items i ON b.item_id = i.item_id
    WHERE i.item_id IS NULL
""")
total = c.fetchone()[0]

print(f'\n=== BiS缺失物品统计 ===')
print(f'总缺失: {total} 个')
print(f'有名称: {with_name} 个')
print(f'有图标: {with_icon} 个')

db.close()