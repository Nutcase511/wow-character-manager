import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取Classic纳克萨玛斯的Boss
cursor.execute('SELECT boss_id, name FROM bosses WHERE dungeon_id = 595 ORDER BY boss_id')
classic_bosses = cursor.fetchall()

print('Classic Naxxramas Bosses:')
for row in classic_bosses:
    print(f'{row[0]} - {row[1]}')

# 检查掉落数据
cursor.execute('SELECT COUNT(*) FROM boss_loot WHERE boss_id IN (SELECT boss_id FROM bosses WHERE dungeon_id = 595)')
loot_count = cursor.fetchone()[0]
print(f'\nTotal loot items in Classic Naxxramas: {loot_count}')

# 检查前几个掉落记录
cursor.execute('''
    SELECT b.name, l.item_id, l.item_name 
    FROM bosses b 
    JOIN boss_loot l ON b.boss_id = l.boss_id 
    WHERE b.dungeon_id = 595 
    LIMIT 10
''')
print('\nSample loot items:')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} - {row[2]}')

conn.close()
