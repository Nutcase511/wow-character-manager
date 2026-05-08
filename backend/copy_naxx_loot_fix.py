import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取Classic纳克萨玛斯的Boss和掉落数据
cursor.execute('''
    SELECT b.boss_id, l.item_id, l.item_name, l.difficulty
    FROM bosses b
    JOIN boss_loot l ON b.boss_id = l.boss_id
    WHERE b.dungeon_id = 595  -- Classic Naxxramas
''')
classic_loot = cursor.fetchall()

print(f'Found {len(classic_loot)} loot entries from Classic Naxxramas')

# 获取WotLK纳克萨玛斯的所有Boss ID
cursor.execute('SELECT boss_id FROM bosses WHERE dungeon_name = "纳克萨玛斯" AND dungeon_id = 10001 ORDER BY boss_id')
wotlk_boss_ids = [row[0] for row in cursor.fetchall()]

print(f'WotLK Naxxramas has {len(wotlk_boss_ids)} bosses')
print(f'Boss IDs: {wotlk_boss_ids}')

# 平均分配掉落数据到WotLK的Boss
copied_count = 0
for i, (classic_boss_id, item_id, item_name, difficulty) in enumerate(classic_loot):
    # 循环分配到WotLK的Boss
    wotlk_boss_id = wotlk_boss_ids[i % len(wotlk_boss_ids)]
    cursor.execute('''
        INSERT INTO boss_loot (boss_id, item_id, item_name, difficulty)
        VALUES (?, ?, ?, ?)
    ''', (wotlk_boss_id, item_id, item_name, difficulty))
    copied_count += 1

conn.commit()
print(f'Copied {copied_count} loot entries to WotLK Naxxramas')

# 验证结果
cursor.execute('''
    SELECT b.name, COUNT(l.id) as loot_count 
    FROM bosses b 
    LEFT JOIN boss_loot l ON b.boss_id = l.boss_id 
    WHERE b.dungeon_name = '纳克萨玛斯' AND b.dungeon_id = 10001
    GROUP BY b.name 
    ORDER BY loot_count DESC
''')
print('\nWotLK Naxxramas Boss Loot Counts:')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} items')

conn.close()
