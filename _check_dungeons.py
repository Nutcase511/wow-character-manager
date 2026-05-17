"""检查特定副本(如MC)的Boss和掉落"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# MC的dungeon_id = 43
print('=== 熔火之心(dungeon_id=43) ===')
c.execute('SELECT id, boss_id, name FROM bosses WHERE dungeon_id = 43')
bosses = c.fetchall()
print(f'Boss: {len(bosses)} 个')
ids_in_boss_loot = 0
for b in bosses:
    c.execute('SELECT COUNT(*) FROM boss_loot WHERE boss_id = ?', (b[1],))
    loot_cnt = c.fetchone()[0]
    if loot_cnt > 0:
        ids_in_boss_loot += 1
    print(f'  id={b[0]}, boss_id={b[1]}, {b[2]}: {loot_cnt}件掉落')
print(f'在boss_loot中有掉落数据的Boss: {ids_in_boss_loot}个')

# 再看看60级经典副本的dungeon_id列表
print('\n=== classic expansion 副本 ===')
c.execute('SELECT id, dungeon_id, name, phase FROM dungeons WHERE expansion = "classic" ORDER BY id')
dungeons = c.fetchall()
for d in dungeons:
    c.execute('SELECT COUNT(*) FROM bosses WHERE dungeon_id = ?', (d[1],))
    boss_cnt = c.fetchone()[0]
    c.execute('SELECT COUNT(DISTINCT bl.item_id) FROM boss_loot bl JOIN bosses b ON bl.boss_id = b.boss_id WHERE b.dungeon_id = ?', (d[1],))
    loot_cnt = c.fetchone()[0]
    print(f'  {d[1]}: {d[2]}(phase={d[3]}): {boss_cnt}个Boss, {loot_cnt}件掉落')

# 再看看哪些dungeon_id的Boss有掉落
print('\n=== 按dungeon_id统计有掉落的副本 ===')
c.execute("""
    SELECT b.dungeon_id, d.name, COUNT(DISTINCT bl.item_id) as loot_cnt
    FROM boss_loot bl
    JOIN bosses b ON bl.boss_id = b.boss_id
    LEFT JOIN dungeons d ON d.dungeon_id = b.dungeon_id
    GROUP BY b.dungeon_id
    HAVING loot_cnt > 0
    ORDER BY b.dungeon_id
""")
rows = c.fetchall()
print(f'有掉落数据的副本: {len(rows)} 个')
for r in rows[:15]:
    print(f'  dungeon_id={r[0]}, {r[1] or "未匹配"}: {r[2]}件')

# 复查boss_loot前10条记录
print('\n=== boss_loot 前10条记录 ===')
c.execute('SELECT * FROM boss_loot LIMIT 10')
for r in c.fetchall():
    print(f'  id={r[0]}, boss_id={r[1]}, item_id={r[2]}, item_name={r[3]}, difficulty={r[4]}')

db.close()