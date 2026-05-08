import sqlite3
import json

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 使用一个新的ID添加WotLK的纳克萨玛斯
cursor.execute('''
    INSERT INTO dungeons (dungeon_id, name, description, map_name, minimum_level, modes, expansion, category)
    VALUES (10001, "纳克萨玛斯", "巫妖王之怒团本", "纳克萨玛斯", 80, ?, "wotlk", "raid")
''', (json.dumps(["10", "25", "10h", "25h"]),))
conn.commit()
print('已添加WotLK纳克萨玛斯')

# 检查最终统计
cursor.execute('SELECT expansion, category, COUNT(*) FROM dungeons GROUP BY expansion, category ORDER BY expansion, category')
print('\nFinal Summary:')
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]}: {row[2]}')

# 列出WotLK团本
cursor.execute('SELECT name, dungeon_id FROM dungeons WHERE expansion = "wotlk" AND category = "raid" ORDER BY dungeon_id')
print('\nWotLK Raids:')
for row in cursor.fetchall():
    print(f'{row[0]}')

conn.close()
