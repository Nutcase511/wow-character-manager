import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 统计中文和英文装备数量
cursor.execute('''
    SELECT 
        SUM(CASE WHEN item_name LIKE '%[\\u4e00-\\u9fff]%' THEN 1 ELSE 0 END) as chinese_count,
        SUM(CASE WHEN item_name NOT LIKE '%[\\u4e00-\\u9fff]%' AND item_name != '' THEN 1 ELSE 0 END) as english_count,
        COUNT(*) as total
    FROM boss_loot
''')
result = cursor.fetchone()
chinese_count, english_count, total = result

print(f'Total loot entries: {total}')
print(f'With Chinese names: {chinese_count} ({(chinese_count/total*100):.1f}%)')
print(f'With English names: {english_count} ({(english_count/total*100):.1f}%)')

# 显示一些示例
cursor.execute('SELECT DISTINCT item_name FROM boss_loot WHERE item_name LIKE "%[\\u4e00-\\u9fff]%" LIMIT 10')
chinese_items = [row[0] for row in cursor.fetchall()]
print('\nChinese item examples:')
for item in chinese_items:
    print(f'  {item}')

cursor.execute('SELECT DISTINCT item_name FROM boss_loot WHERE item_name NOT LIKE "%[\\u4e00-\\u9fff]%" AND item_name != "" LIMIT 10')
english_items = [row[0] for row in cursor.fetchall()]
print('\nEnglish item examples:')
for item in english_items:
    print(f'  {item}')

conn.close()
