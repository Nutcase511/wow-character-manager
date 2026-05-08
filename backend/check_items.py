import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 检查装备名称的语言
cursor.execute('SELECT item_name FROM items LIMIT 10')
items = cursor.fetchall()

print('Current item names (first 10):')
for item in items:
    print(f'  {item[0]}')

# 检查装备总数
cursor.execute('SELECT COUNT(*) FROM items')
total = cursor.fetchone()[0]
print(f'\nTotal items: {total}')

# 检查boss_loot中的装备名称
cursor.execute('SELECT DISTINCT item_name FROM boss_loot LIMIT 10')
loot_items = cursor.fetchall()

print('\nBoss loot item names (first 10):')
for item in loot_items:
    print(f'  {item[0]}')

conn.close()
