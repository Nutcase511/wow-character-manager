"""检查祖尔格拉布和其他经典团本的掉落问题"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 祖尔格拉布 boss in boss_loot
print('=== 祖尔格拉布(dungeon_id=309) ===')
c.execute('SELECT id, boss_id, name FROM bosses WHERE dungeon_id = 309')
zg_bosses = c.fetchall()
for b in zg_bosses:
    c.execute('SELECT COUNT(*) FROM boss_loot WHERE boss_id = ?', (b[1],))
    loot = c.fetchone()[0]
    print(f'  boss_id={b[1]}, {b[2]}: {loot}件掉落')

# boss_loot中是否有这些ZG boss_id
print('\n=== boss_loot中查找ZG的boss_id ===')
zg_ids = [14517, 14507, 14510, 11382, 15082, 15083, 15084, 15085, 15114, 14509, 14515, 11380, 14834]
for bid in zg_ids:
    c.execute('SELECT COUNT(*) FROM boss_loot WHERE boss_id = ?', (bid,))
    cnt = c.fetchone()[0]
    if cnt > 0:
        print(f'  boss_id={bid}: {cnt}件')

# boss_loot中祖尔格拉布骷髅图标掉落
print('\n=== boss_loot中祖格相关的item ===')
c.execute('SELECT bl.boss_id, bl.item_id, bl.item_name, b.name FROM boss_loot bl JOIN bosses b ON bl.boss_id = b.boss_id WHERE b.name LIKE "%祖尔" OR b.name LIKE "%血领主" OR b.name LIKE "%哈卡" LIMIT 10')
for r in c.fetchall():
    print(f'  boss_id={r[0]}({r[3]}), item_id={r[1]}, {r[2]}')

# 看看熔火之心真正对应的数据
print('\n=== 熔火之心整理 ===')
print('P1版本(dungeon_id=409):')
c.execute('SELECT boss_id, name FROM bosses WHERE dungeon_id = 409')
for b in c.fetchall():
    c.execute('SELECT COUNT(*) FROM boss_loot WHERE boss_id = ?', (b[0],))
    loot = c.fetchone()[0]
    status = '有掉落' if loot > 0 else '无掉落'
    print(f'  {b[0]}: {b[1]} -> {loot}件 {status}')

print('\nwotlk版本(dungeon_id=43, 实际是哀嚎洞穴的ID):')
c.execute('SELECT boss_id, name FROM bosses WHERE dungeon_id = 43')
for b in c.fetchall():
    c.execute('SELECT COUNT(*) FROM boss_loot WHERE boss_id = ?', (b[0],))
    loot = c.fetchone()[0]
    print(f'  {b[0]}: {b[1]} -> {loot}件')

db.close()