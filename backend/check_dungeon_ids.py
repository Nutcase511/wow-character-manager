import sqlite3

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取所有副本ID
cursor.execute('SELECT dungeon_id, name, expansion FROM dungeons ORDER BY dungeon_id')
print('Current dungeon IDs:')
for row in cursor.fetchall():
    print(f'{row[0]} - {row[1]} - {row[2]}')

conn.close()
