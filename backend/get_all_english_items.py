import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取所有英文装备名称（不含中文的）
cursor.execute('''
    SELECT DISTINCT item_name 
    FROM boss_loot 
    WHERE item_name NOT LIKE '%[\\u4e00-\\u9fff]%' 
    AND item_name != ''
    ORDER BY item_name
''')
english_items = [row[0] for row in cursor.fetchall()]

print(f'Total English items: {len(english_items)}')
print('\nFirst 50 English items:')
for i, item in enumerate(english_items[:50], 1):
    print(f'{i}. {item}')

# 保存到文件
with open('english_items.txt', 'w', encoding='utf-8') as f:
    for item in english_items:
        f.write(f'{item}\n')

print(f'\nSaved {len(english_items)} items to english_items.txt')

conn.close()
