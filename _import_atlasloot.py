"""
从喵影掉落插件(AtlasLootMY)提取所有团本掉落数据，导入数据库
支持 Classic + TBC
"""
import re
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'
DATA_FILES = [
    r'C:\WOW\World of Warcraft\_classic_titan_\Interface\AddOns\AtlasLootMY_DungeonsAndRaids\data.lua',
    r'C:\WOW\World of Warcraft\_classic_titan_\Interface\AddOns\AtlasLootMY_DungeonsAndRaids\data-tbc.lua',
]

def extract_balanced_block(text, start):
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return text[start:i+1], i
    return None, -1

def parse_raid_data(content):
    raids = {}
    # 匹配 data["AnyName"] 包括带引号的名称
    for m in re.finditer(r'data\["([^"]+)"\]\s*=\s*\{', content):
        raid_name = m.group(1)
        block_start = m.start()
        brace_pos = block_start + content[block_start:].find('{')
        if brace_pos == -1:
            continue

        block, _ = extract_balanced_block(content, brace_pos)
        if block is None:
            continue

        inst_m = re.search(r'InstanceID\s*=\s*(\d+)', block)
        if not inst_m:
            continue
        inst_id = int(inst_m.group(1))

        items_m = re.search(r'items\s*=\s*\{', block)
        if not items_m:
            continue

        items_block, _ = extract_balanced_block(block, items_m.start())
        if items_block is None:
            continue

        # 提取每个boss
        bosses = []
        pos = 0
        while True:
            n = items_block.find('npcID', pos)
            if n == -1:
                break

            brace_before = items_block.rfind('{', 0, n)
            if brace_before == -1:
                pos = n + 1
                continue

            boss_block, end_pos = extract_balanced_block(items_block, brace_before)
            if boss_block is None:
                pos = n + 1
                continue
            pos = brace_before + len(boss_block)

            npc_m = re.search(r'npcID\s*=\s*(\d+)', boss_block)
            name_m = re.search(r'name\s*=\s*AL\["(.*?)"\]', boss_block)
            if not npc_m:
                continue
            npc_id = int(npc_m.group(1))
            boss_name = name_m.group(1) if name_m else f"Boss_{npc_id}"

            nd_pos = boss_block.find('[NORMAL_DIFF]')
            if nd_pos == -1:
                continue
            nd_brace = boss_block.find('{', nd_pos)
            if nd_brace == -1:
                continue

            nd_block, _ = extract_balanced_block(boss_block, nd_brace)
            if nd_block is None:
                continue

            item_ids = list(set(int(m.group(1)) for m in re.finditer(r'\{\s*\d+\s*,\s*(\d+)\s*\}', nd_block)))
            if item_ids:
                bosses.append({'npc_id': npc_id, 'name': boss_name, 'item_ids': item_ids})

        if bosses:
            raids[inst_id] = {'name': raid_name, 'bosses': bosses}
            print(f"  {raid_name} (ID={inst_id}): {len(bosses)} 个Boss, {sum(len(b['item_ids']) for b in bosses)} 件掉落")

    return raids

# 解析所有数据文件
all_raids = {}
for f in DATA_FILES:
    print(f"\n读取: {f}")
    with open(f, 'r', encoding='utf-8') as fh:
        raids = parse_raid_data(fh.read())
    all_raids.update(raids)

print(f"\n共提取 {len(all_raids)} 个团本数据")

# 连接数据库
db = sqlite3.connect(DB_PATH)
c = db.cursor()

c.execute("SELECT id, dungeon_id, name, phase FROM dungeons WHERE category = 'raid'")
existing_dungeons = {r[1]: {'id': r[0], 'name': r[2], 'phase': r[3]} for r in c.fetchall()}

for inst_id, raid_data in all_raids.items():
    if inst_id not in existing_dungeons:
        print(f"\n[跳过] {raid_data['name']} (ID={inst_id}) 不在数据库")
        continue

    d = existing_dungeons[inst_id]
    print(f"\n=== {raid_data['name']} (Phase={d['phase']}) ===")

    c.execute("SELECT boss_id FROM bosses WHERE dungeon_id = ?", (inst_id,))
    existing_boss_ids = set(r[0] for r in c.fetchall())

    for boss in raid_data['bosses']:
        npc_id = boss['npc_id']

        if npc_id not in existing_boss_ids:
            c.execute("INSERT OR IGNORE INTO bosses (boss_id, name, dungeon_id) VALUES (?, ?, ?)",
                     (npc_id, boss['name'], inst_id))
            print(f"  [新增Boss] {boss['name']} (npcID={npc_id})")
            existing_boss_ids.add(npc_id)

        c.execute("SELECT item_id FROM boss_loot WHERE boss_id = ?", (npc_id,))
        existing_items = set(r[0] for r in c.fetchall())

        new_items = [i for i in boss['item_ids'] if i not in existing_items]
        if new_items:
            for item_id in new_items:
                c.execute("INSERT INTO boss_loot (boss_id, item_id, item_name) VALUES (?, ?, ?)",
                         (npc_id, item_id, ''))
            print(f"  [+{len(new_items)}] {boss['name']}: 新增 {len(new_items)} 件")

db.commit()
db.close()
print(f"\n[完成] 数据已导入数据库")