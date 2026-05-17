"""将数据库中所有 wow.zamimg.com 图标 URL 替换为 render.worldofwarcraft.com"""
import sqlite3
import re

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

OLD_DOMAIN = 'https://wow.zamimg.com/images/wow/icons/large/'
NEW_DOMAIN = 'https://render.worldofwarcraft.com/icons/56/'

def convert_url(old_url):
    if not old_url or OLD_DOMAIN not in old_url:
        return old_url
    icon_name = old_url.replace(OLD_DOMAIN, '').replace('.jpg', '').replace('.png', '')
    return f'{NEW_DOMAIN}{icon_name}.jpg'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 先统计受影响的数据量
tables = [
    ('items', 'icon_url'),
    ('bis_lists', 'icon_url'),
    ('character_equipment', 'icon_url'),
    ('dungeons', 'icon_url'),
    ('bosses', 'icon_url'),
]

total = 0
for table, column in tables:
    c.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} LIKE ?", (f'{OLD_DOMAIN}%',))
    count = c.fetchone()[0]
    if count > 0:
        print(f'{table}.{column}: {count} 条待转换')
        total += count

print(f'\n共计 {total} 条记录需要转换')

# 执行替换
updated = 0
for table, column in tables:
    c.execute(f"SELECT rowid, {column} FROM {table} WHERE {column} LIKE ?", (f'{OLD_DOMAIN}%',))
    rows = c.fetchall()
    for rowid, old_url in rows:
        new_url = convert_url(old_url)
        c.execute(f"UPDATE {table} SET {column} = ? WHERE rowid = ?", (new_url, rowid))
        updated += 1

db.commit()
db.close()

print(f'已更新 {updated} 条记录')
print(f'\n示例转换:')
print(f'  旧: https://wow.zamimg.com/images/wow/icons/large/inv_helmet_133.jpg')
print(f'  新: https://render.worldofwarcraft.com/icons/56/inv_helmet_133.jpg')