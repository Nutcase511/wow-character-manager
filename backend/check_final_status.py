import sqlite3

def contains_chinese(text):
    if not text:
        return False
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 统计当前状态
cursor.execute('SELECT DISTINCT item_name FROM boss_loot')
all_names = [row[0] for row in cursor.fetchall()]

chinese_count = 0
english_count = 0
chinese_names = []
english_names = []

for name in all_names:
    if name:
        if contains_chinese(name):
            chinese_count += 1
            chinese_names.append(name)
        else:
            english_count += 1
            english_names.append(name)

print(f'Total distinct item names: {len(all_names)}')
print(f'Chinese names: {chinese_count} ({(chinese_count/len(all_names)*100):.1f}%)')
print(f'English names: {english_count} ({(english_count/len(all_names)*100):.1f}%)')

print('\nChinese item examples:')
for item in chinese_names[:10]:
    print(f'  {item}')

print('\nEnglish item examples (most common):')
cursor.execute('SELECT item_name, COUNT(*) as count FROM boss_loot WHERE item_name != "" GROUP BY item_name ORDER BY count DESC LIMIT 10')
for row in cursor.fetchall():
    if not contains_chinese(row[0]):
        print(f'  {row[0]} ({row[1]} occurrences)')

conn.close()
