"""查找无Boss副本是否有对应的Boss（通过名字匹配或相似dungeon_id）"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# 剩余无Boss副本
c.execute("""
    SELECT d.id, d.dungeon_id, d.name, d.expansion, d.phase, d.category
    FROM dungeons d
    WHERE (SELECT COUNT(*) FROM bosses WHERE dungeon_id = d.dungeon_id) = 0
    ORDER BY d.id
""")
no_boss = c.fetchall()

print('=== 无Boss副本分析 ===')
for d in no_boss:
    did = d[1]
    name = d[2]
    
    # 1. 查bosses表里有没有名字相似的Boss
    keywords = name.replace('：', ':').replace('  ', ' ').split()
    keyword = keywords[0] if keywords else name
    c.execute('SELECT COUNT(*) FROM bosses WHERE name LIKE ?', (f'%{keyword}%',))
    similar_named = c.fetchone()[0]
    
    # 2. 查bosses表里有没有相近的dungeon_id
    c.execute('SELECT dungeon_id, COUNT(*) as cnt FROM bosses GROUP BY dungeon_id HAVING dungeon_id BETWEEN ? AND ? ORDER BY dungeon_id', (did-5, did+5))
    nearby = c.fetchall()
    
    details = []
    if similar_named > 0:
        c.execute('SELECT dungeon_id, name FROM bosses WHERE name LIKE ? LIMIT 3', (f'%{keyword}%',))
        samples = c.fetchall()
        for s in samples:
            c.execute('SELECT name FROM dungeons WHERE dungeon_id = ?', (s[0],))
            dn = c.fetchone()
            dn_name = dn[0] if dn else '无对应副本'
            print(f'  -> Boss"{s[1]}"在dungeon_id={s[0]}({dn_name})')
    
    nearby_info = ', '.join([f'{x[0]}({x[1]}Boss)' for x in nearby]) if nearby else '无'
    
    print(f'\n[{name}] dungeon_id={did}, phase={d[4]}')
    if details:
        for det in details:
            print(f'  {det}')
    if nearby:
        print(f'  附近dungeon_id: {nearby_info}')
    
    # 3. 特殊检查：黑石深渊、通灵学院这些
    c.execute('SELECT DISTINCT dungeon_id FROM bosses WHERE dungeon_id IN (1584, 2057, 1583, 1337, 722, 721, 718)')
    existing = c.fetchall()
    if existing:
        existing_ids = [x[0] for x in existing]
        print(f'  存在dungeon_id: {existing_ids} 但在bosses表中没有记录')

# 检查黑石深渊等经典副本的Boss在哪里
print('\n\n=== 经典副本Boss特殊排查 ===')
classic_dungeon_ids = [1584, 2057, 1583, 1337, 722, 721, 718, 3714, 3790, 3791, 3789, 3716, 3715, 2367, 3848, 3847, 3849, 3959]
for did in classic_dungeon_ids:
    c.execute('SELECT COUNT(*) FROM bosses WHERE dungeon_id = ?', (did,))
    cnt = c.fetchone()[0]
    c.execute('SELECT name FROM dungeons WHERE dungeon_id = ?', (did,))
    dn = c.fetchone()
    dn_name = dn[0] if dn else '无匹配'
    print(f'dungeon_id={did}({dn_name}): Boss={cnt}个')

db.close()