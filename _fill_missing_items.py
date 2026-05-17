"""将装备表和BiS表中缺失的物品补全到items表（使用占位数据）"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'
PLACEHOLDER_ICON = 'https://render.worldofwarcraft.com/icons/56/inv_misc_questionmark.jpg'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 收集所有缺失的item_id
missing = set()

# 1. 从character_equipment
c.execute("""
    SELECT DISTINCT ce.item_id
    FROM character_equipment ce
    LEFT JOIN items i ON ce.item_id = i.item_id
    WHERE i.item_id IS NULL
""")
for r in c.fetchall():
    missing.add(r[0])

# 2. 从bis_lists
c.execute("""
    SELECT DISTINCT b.item_id
    FROM bis_lists b
    LEFT JOIN items i ON b.item_id = i.item_id
    WHERE i.item_id IS NULL
""")
for r in c.fetchall():
    missing.add(r[0])

missing_list = sorted(missing)
print(f'共 {len(missing_list)} 个缺失物品需要补全')

# 插入占位数据
inserted = 0
for item_id in missing_list:
    try:
        c.execute("""
            INSERT INTO items (item_id, name, quality, item_level, icon_url, stats, slot)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id,
            f'未知物品 #{item_id}',
            'common',
            0,
            PLACEHOLDER_ICON,
            '{}',
            ''
        ))
        inserted += 1
    except sqlite3.IntegrityError:
        # 已存在则跳过
        pass

db.commit()
db.close()

print(f'成功插入 {inserted} 条记录')
print(f'占位图标: {PLACEHOLDER_ICON}')
print(f'名称格式: "未知物品 #ID"')