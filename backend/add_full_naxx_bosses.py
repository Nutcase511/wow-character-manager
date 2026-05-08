import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取WotLK纳克萨玛斯的dungeon_id
cursor.execute('SELECT dungeon_id FROM dungeons WHERE name = "纳克萨玛斯" AND expansion = "wotlk"')
wotlk_dungeon_id = cursor.fetchone()[0]

# 删除现有的Boss（如果有）
cursor.execute('DELETE FROM bosses WHERE dungeon_id = ?', (wotlk_dungeon_id,))

# WotLK纳克萨玛斯完整Boss列表
naxx_bosses = [
    # 蜘蛛区
    (10001, '阿努巴拉克', '蜘蛛区最终Boss', '纳克萨玛斯', 'raid'),
    (10002, '法琳娜', '蜘蛛区Boss', '纳克萨玛斯', 'raid'),
    (10003, '迈克斯纳', '蜘蛛区Boss', '纳克萨玛斯', 'raid'),
    (10004, '诺斯', '蜘蛛区Boss', '纳克萨玛斯', 'raid'),
    # 瘟疫区
    (10005, '洛欧塞布', '瘟疫区最终Boss', '纳克萨玛斯', 'raid'),
    (10006, '肮脏的希尔盖', '瘟疫区Boss', '纳克萨玛斯', 'raid'),
    (10007, '格拉斯', '瘟疫区Boss', '纳克萨玛斯', 'raid'),
    (10008, '帕奇维克', '瘟疫区Boss', '纳克萨玛斯', 'raid'),
    # 军事区
    (10009, '教官拉苏维奥斯', '军事区Boss', '纳克萨玛斯', 'raid'),
    (10010, '收割者戈提克', '军事区Boss', '纳克萨玛斯', 'raid'),
    (10011, '天启四骑士', '军事区最终Boss', '纳克萨玛斯', 'raid'),
    # 构造区
    (10012, '塔迪乌斯', '构造区最终Boss', '纳克萨玛斯', 'raid'),
    (10013, '格罗布鲁斯', '构造区Boss', '纳克萨玛斯', 'raid'),
    (10014, '费尔根', '构造区Boss', '纳克萨玛斯', 'raid'),
    (10015, '斯塔拉格', '构造区Boss', '纳克萨玛斯', 'raid'),
    # 冰龙区
    (10016, '萨菲隆', '冰龙区Boss', '纳克萨玛斯', 'raid'),
    (10017, '克尔苏加德', '纳克萨玛斯最终Boss', '纳克萨玛斯', 'raid'),
]

# 添加Boss
for boss in naxx_bosses:
    boss_id, name, description, dungeon_name, category = boss
    cursor.execute('''
        INSERT INTO bosses (boss_id, name, description, dungeon_id, dungeon_name, category)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (boss_id, name, description, wotlk_dungeon_id, dungeon_name, category))

conn.commit()
print(f'Added {len(naxx_bosses)} bosses to WotLK Naxxramas')

# 最终统计
cursor.execute('''
    SELECT d.name, COUNT(b.id) as boss_count 
    FROM dungeons d 
    LEFT JOIN bosses b ON d.dungeon_id = b.dungeon_id 
    WHERE d.category = 'raid' AND d.expansion = 'wotlk'
    GROUP BY d.name 
    ORDER BY boss_count DESC
''')
print('\nWotLK Raid Bosses:')
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} bosses')

# 列出纳克萨玛斯的Boss
cursor.execute('SELECT name FROM bosses WHERE dungeon_id = ? ORDER BY boss_id', (wotlk_dungeon_id,))
print('\nNaxxramas Bosses:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

conn.close()
