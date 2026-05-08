import sqlite3
from chinese_item_names import chinese_item_names

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取所有需要更新的装备名称
cursor.execute('SELECT DISTINCT item_name FROM boss_loot')
english_names = [row[0] for row in cursor.fetchall()]

print(f'Total distinct items in boss_loot: {len(english_names)}')

# 统计有多少可以翻译
translatable_count = sum(1 for name in english_names if name in chinese_item_names)
print(f'Items that can be translated: {translatable_count}')

# 更新boss_loot表中的装备名称
updated_count = 0
for english_name in english_names:
    if english_name in chinese_item_names:
        chinese_name = chinese_item_names[english_name]
        cursor.execute('''
            UPDATE boss_loot 
            SET item_name = ? 
            WHERE item_name = ?
        ''', (chinese_name, english_name))
        updated_count += cursor.rowcount

conn.commit()
print(f'Updated {updated_count} loot entries')

# 更新items表中的装备名称
cursor.execute('SELECT DISTINCT name FROM items')
item_names = [row[0] for row in cursor.fetchall()]

item_updates = 0
for english_name in item_names:
    if english_name in chinese_item_names:
        chinese_name = chinese_item_names[english_name]
        cursor.execute('''
            UPDATE items 
            SET name = ? 
            WHERE name = ?
        ''', (chinese_name, english_name))
        item_updates += cursor.rowcount

conn.commit()
print(f'Updated {item_updates} items')

# 验证结果
cursor.execute('SELECT item_name FROM boss_loot LIMIT 10')
updated_items = cursor.fetchall()

print('\nUpdated loot items (first 10):')
for item in updated_items:
    print(f'  {item[0]}')

conn.close()
