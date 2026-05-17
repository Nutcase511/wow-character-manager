import sqlite3

db = sqlite3.connect(r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db')
c = db.cursor()

c.execute('SELECT icon_url FROM items WHERE icon_url LIKE "%questionmark%" LIMIT 5')
rows = c.fetchall()
print(f'问号图标: {len(rows)} 条')

c.execute('SELECT icon_url FROM items WHERE icon_url="" LIMIT 5')
print(f'空: {len(c.fetchall())} 条')

c.execute('SELECT icon_url FROM items LIMIT 5')
print(f'\n前5条icon_url样:')
for r in c.fetchall():
    print(f'  {r[0][:80]}')

c.execute('SELECT icon_url FROM items WHERE icon_url NOT LIKE "%render%" AND icon_url NOT LIKE "%questionmark%" AND icon_url != "" LIMIT 5')
for r in c.fetchall():
    print(f'  其他格式: {r[0][:80]}')

db.close()