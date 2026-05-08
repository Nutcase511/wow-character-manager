import sqlite3
import json

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 检查WotLK的纳克萨玛斯是否存在
cursor.execute('SELECT * FROM dungeons WHERE name = "纳克萨玛斯" AND expansion = "wotlk"')
result = cursor.fetchone()

if result:
    print('WotLK纳克萨玛斯已存在')
else:
    print('需要添加WotLK纳克萨玛斯')
    cursor.execute('''
        INSERT INTO dungeons (dungeon_id, name, description, map_name, minimum_level, modes, expansion, category)
        VALUES (624, "纳克萨玛斯", "巫妖王之怒团本", "纳克萨玛斯", 80, ?, "wotlk", "raid")
    ''', (json.dumps(["10", "25", "10h", "25h"]),))
    conn.commit()
    print('已添加WotLK纳克萨玛斯')

# 最终统计
cursor.execute('SELECT expansion, category, COUNT(*) FROM dungeons GROUP BY expansion, category ORDER BY expansion, category')
print('\nFinal Summary:')
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]}: {row[2]}')

conn.close()
