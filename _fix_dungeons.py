"""清理重复的副本记录：删除空副本，保留有数据的并补全dungeon_id"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 1. 找出所有副本及其数据情况
print('=== 重复副本分析 ===')
c.execute("""
    SELECT d.id, d.dungeon_id, d.name, d.expansion, d.phase, d.category,
        (SELECT COUNT(*) FROM bosses WHERE dungeon_id = d.dungeon_id) as boss_cnt,
        (SELECT COUNT(*) FROM bosses b JOIN boss_loot bl ON bl.boss_id = b.boss_id WHERE b.dungeon_id = d.dungeon_id) as loot_cnt
    FROM dungeons d
    ORDER BY d.name, d.id
""")
dungeons = c.fetchall()

# 按名称分组找出重复
from collections import defaultdict
by_name = defaultdict(list)
for row in dungeons:
    by_name[row[2]].append(row)

to_delete = []
for name, entries in by_name.items():
    if len(entries) > 1:
        # 找有数据的那个
        has_data = [e for e in entries if e[6] > 0]
        no_data = [e for e in entries if e[6] == 0]
        if has_data and no_data:
            print(f'\n[{name}] 有重复:')
            for e in entries:
                print(f'  id={e[0]}, dungeon_id={e[1]}, expansion={e[3]}, phase={e[4]}, cat={e[5]}, boss={e[6]}, loot={e[7]}')
            for e in no_data:
                to_delete.append(e[0])
            print(f'  -> 删除{len(no_data)}条空记录, 保留id={has_data[0][0]}')

# 执行删除
if to_delete:
    print(f'\n=== 删除 {len(to_delete)} 条空副本记录 ===')
    for did in to_delete:
        c.execute("DELETE FROM dungeons WHERE id = ?", (did,))
        print(f'  已删除 id={did}')

# 2. 检查还有哪些副本没有Boss但可能有数据的dungeon_id
print('\n=== 剩余无Boss副本 ===')
c.execute("""
    SELECT d.id, d.dungeon_id, d.name, d.phase, d.category
    FROM dungeons d
    WHERE (SELECT COUNT(*) FROM bosses WHERE dungeon_id = d.dungeon_id) = 0
    ORDER BY d.id
""")
no_boss = c.fetchall()
if no_boss:
    print(f'共 {len(no_boss)} 个:')
    for r in no_boss[:20]:
        print(f'  id={r[0]}, dungeon_id={r[1]}, {r[2]}, phase={r[3]}, cat={r[4]}')
else:
    print('全部副本都有Boss数据')

db.commit()
db.close()

print('\n✅ 清理完成')