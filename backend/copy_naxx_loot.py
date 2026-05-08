import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取Classic纳克萨玛斯的Boss和掉落数据
cursor.execute('''
    SELECT b.boss_id, b.name, l.item_id, l.item_name, l.difficulty
    FROM bosses b
    LEFT JOIN boss_loot l ON b.boss_id = l.boss_id
    WHERE b.dungeon_id = 595  -- Classic Naxxramas
''')
classic_data = cursor.fetchall()

print(f'Found {len(classic_data)} loot entries from Classic Naxxramas')

# 创建Boss名称到新Boss ID的映射
wotlk_boss_map = {
    '阿努巴拉克': 10001,
    '法琳娜': 10002,
    '迈克斯纳': 10003,
    '诺斯': 10004,
    '洛欧塞布': 10005,
    '肮脏的希尔盖': 10006,
    '格拉斯': 10007,
    '帕奇维克': 10008,
    '教官拉苏维奥斯': 10009,
    '收割者戈提克': 10010,
    '天启四骑士': 10011,
    '塔迪乌斯': 10012,
    '格罗布鲁斯': 10013,
    '费尔根': 10014,
    '斯塔拉格': 10015,
    '萨菲隆': 10016,
    '克尔苏加德': 10017,
}

# 复制掉落数据
copied_count = 0
for row in classic_data:
    classic_boss_id, boss_name, item_id, item_name, difficulty = row
    if boss_name in wotlk_boss_map and item_id:
        new_boss_id = wotlk_boss_map[boss_name]
        cursor.execute('''
            INSERT INTO boss_loot (boss_id, item_id, item_name, difficulty)
            VALUES (?, ?, ?, ?)
        ''', (new_boss_id, item_id, item_name, difficulty))
        copied_count += 1

conn.commit()
print(f'Copied {copied_count} loot entries to WotLK Naxxramas')

# 验证结果
cursor.execute('''
    SELECT b.name, COUNT(l.id) as loot_count 
    FROM bosses b 
    LEFT JOIN boss_loot l ON b.boss_id = l.boss_id 
    WHERE b.dungeon_name = '纳克萨玛斯' 
    GROUP BY b.name 
    ORDER BY loot_count DESC
''')
print('\nWotLK Naxxramas Boss Loot Counts after update:')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} items')

conn.close()
