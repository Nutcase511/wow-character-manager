import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取items表结构
cursor.execute("PRAGMA table_info(items)")
items_columns = cursor.fetchall()
print('Items table columns:')
for col in items_columns:
    print(f'  {col[1]} ({col[2]})')

# 获取boss_loot表结构
cursor.execute("PRAGMA table_info(boss_loot)")
loot_columns = cursor.fetchall()
print('\nBoss_loot table columns:')
for col in loot_columns:
    print(f'  {col[1]} ({col[2]})')

# 检查数据
cursor.execute('SELECT * FROM items LIMIT 5')
items_data = cursor.fetchall()
print('\nItems data sample:')
for item in items_data:
    print(f'  {item}')

cursor.execute('SELECT * FROM boss_loot LIMIT 5')
loot_data = cursor.fetchall()
print('\nBoss loot data sample:')
for loot in loot_data:
    print(f'  {loot}')

conn.close()
