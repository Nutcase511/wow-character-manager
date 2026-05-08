import sqlite3
import json

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取Classic纳克萨玛斯的Boss数据
cursor.execute('SELECT boss_id, name, description, dungeon_name, category, icon_url FROM bosses WHERE dungeon_id = 595')
classic_bosses = cursor.fetchall()

print(f'Found {len(classic_bosses)} bosses in Classic Naxxramas')

# 获取WotLK纳克萨玛斯的dungeon_id
cursor.execute('SELECT dungeon_id FROM dungeons WHERE name = "纳克萨玛斯" AND expansion = "wotlk"')
wotlk_dungeon_id = cursor.fetchone()[0]
print(f'WotLK Naxxramas dungeon_id: {wotlk_dungeon_id}')

# 检查是否已有Boss
cursor.execute('SELECT COUNT(*) FROM bosses WHERE dungeon_id = ?', (wotlk_dungeon_id,))
existing_count = cursor.fetchone()[0]
print(f'Existing bosses in WotLK Naxxramas: {existing_count}')

if existing_count == 0:
    # 复制Boss数据到WotLK版本
    for boss in classic_bosses:
        boss_id, name, description, dungeon_name, category, icon_url = boss
        # 使用新的boss_id避免冲突
        new_boss_id = boss_id + 10000
        cursor.execute('''
            INSERT INTO bosses (boss_id, name, description, dungeon_id, dungeon_name, category, icon_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (new_boss_id, name, description, wotlk_dungeon_id, '纳克萨玛斯', category, icon_url))
    
    conn.commit()
    print(f'Added {len(classic_bosses)} bosses to WotLK Naxxramas')
else:
    print('Bosses already exist')

# 最终统计
cursor.execute('''
    SELECT d.name, COUNT(b.id) as boss_count 
    FROM dungeons d 
    LEFT JOIN bosses b ON d.dungeon_id = b.dungeon_id 
    WHERE d.category = 'raid' AND d.expansion = 'wotlk'
    GROUP BY d.name 
    ORDER BY boss_count DESC
''')
print('\nWotLK Raid Bosses after update:')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} bosses')

conn.close()
