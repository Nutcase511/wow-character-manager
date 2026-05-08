import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取boss_loot中出现次数最多的装备名称
cursor.execute('''
    SELECT item_name, COUNT(*) as count 
    FROM boss_loot 
    GROUP BY item_name 
    ORDER BY count DESC 
    LIMIT 100
''')
common_items = cursor.fetchall()

print('Most common items in boss_loot (top 100):')
for i, (name, count) in enumerate(common_items, 1):
    print(f'{i}. {name} ({count} occurrences)')

conn.close()
