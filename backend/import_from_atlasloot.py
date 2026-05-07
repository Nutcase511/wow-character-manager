"""
从AtlasLootMY插件数据文件中解析副本/Boss/掉落数据并导入SQLite
数据来源：本地插件文件，不需要暴雪API
"""
import re
import sqlite3
import os

# 插件数据目录
ADDON_DIR = r"C:\WOW\World of Warcraft\_classic_titan_\Interface\AddOns"
DATA_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wow_character_manager.db")


def parse_cn_locales(filepath: str) -> dict:
    """解析中文本地化文件，返回 英文->中文 映射"""
    cn_map = {}
    if not os.path.exists(filepath):
        return cn_map
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            # AL["English Name"] = "中文名"
            m = re.match(r'AL\["(.+?)"\]\s*=\s*"(.+?)"', line)
            if m:
                cn_map[m.group(1)] = m.group(2)
    return cn_map


def parse_locales_dir(locales_dir: str) -> dict:
    """解析所有本地化文件"""
    cn_map = {}
    cn_file = os.path.join(locales_dir, "constants.cn.lua")
    if os.path.exists(cn_file):
        cn_map.update(parse_cn_locales(cn_file))
    return cn_map


def parse_dungeon_data(filepath: str, cn_map: dict):
    """解析副本数据文件，提取副本/Boss/物品"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    instances = []
    current_instance = None
    current_boss = None
    boss_comment_name = None
    current_diff = None

    for line in content.split('\n'):
        stripped = line.strip()

        # 检测副本定义: data["InstanceKey"] = {
        m = re.match(r'data\["(\w+)"\]\s*=\s*\{', stripped)
        if m:
            current_instance = {
                'key': m.group(1),
                'name': None,
                'instance_id': None,
                'encounter_journal_id': None,
                'bosses': [],
            }
            continue

        # 副本属性
        if current_instance and not current_boss:
            # name = AL["xxx"] 或 name = format(AL["xxx"], ...)
            m_name = re.match(r'name\s*=\s*format\(AL\["(.+?)"\]', stripped)
            if not m_name:
                m_name = re.match(r'name\s*=\s*AL\["(.+?)"\]', stripped)
            if m_name:
                en_name = m_name.group(1)
                current_instance['name'] = cn_map.get(en_name, en_name)

            m_id = re.match(r'InstanceID\s*=\s*(\d+)', stripped)
            if m_id:
                current_instance['instance_id'] = int(m_id.group(1))

            m_ej = re.match(r'EncounterJournalID\s*=\s*(\d+)', stripped)
            if m_ej:
                current_instance['encounter_journal_id'] = int(m_ej.group(1))

        # 检测Boss块: { -- BossKey / npcID
        m_boss = re.match(r'\{\s*--\s*(\S+)', stripped)
        if m_boss and current_instance is not None:
            boss_comment_name = m_boss.group(1)
            current_boss = {
                'key': boss_comment_name,
                'name': None,
                'npc_id': None,
                'encounter_journal_id': None,
                'items_normal': [],
                'items_heroic': [],
                'items_10': [],
                'items_25': [],
                'items_10h': [],
                'items_25h': [],
            }
            current_diff = None
            continue

        # Boss块关闭
        if stripped.startswith('},') and current_boss is not None and current_diff:
            current_diff = None
            continue

        # 中等层级的Boss块关闭（没有逗号）
        if stripped == '}' and current_boss is not None:
            if current_instance is not None:
                current_instance['bosses'].append(current_boss)
            current_boss = None
            boss_comment_name = None
            current_diff = None
            continue

        # 另一种Boss块关闭方式
        if stripped.startswith('},') and current_boss is not None and not current_diff:
            current_instance['bosses'].append(current_boss)
            current_boss = None
            boss_comment_name = None
            current_diff = None
            continue

        # Boss属性
        if current_boss:
            # name = AL["BossName"]
            m_bname = re.match(r'name\s*=\s*AL\["(.+?)"\]', stripped)
            if m_bname:
                en_name = m_bname.group(1)
                current_boss['name'] = cn_map.get(en_name, en_name)

            m_npc = re.match(r'npcID\s*=\s*(\{[\d,\s]+\}|\d+)', stripped)
            if m_npc:
                npc_val = m_npc.group(1)
                if npc_val.startswith('{'):
                    nums = re.findall(r'\d+', npc_val)
                    current_boss['npc_id'] = int(nums[0]) if nums else None
                else:
                    current_boss['npc_id'] = int(npc_val)

            m_ej = re.match(r'EncounterJournalID\s*=\s*(\d+)', stripped)
            if m_ej:
                current_boss['encounter_journal_id'] = int(m_ej.group(1))

            # 难度标记
            if 'NORMAL_DIFF' in stripped or 'P1_DIFF' in stripped or 'P2_DIFF' in stripped or 'P3_DIFF' in stripped:
                current_diff = 'normal'
            elif 'HEROIC_DIFF' in stripped or 'ALPHA_DIFF' in stripped or 'BETA_DIFF' in stripped:
                current_diff = 'heroic'
            elif 'RAID10_DIFF' in stripped and 'RAID10H_DIFF' not in stripped:
                current_diff = '10'
            elif 'RAID25_DIFF' in stripped and 'RAID25H_DIFF' not in stripped:
                current_diff = '25'
            elif 'RAID10H_DIFF' in stripped:
                current_diff = '10h'
            elif 'RAID25H_DIFF' in stripped:
                current_diff = '25h'

            # 物品行: { 位置, 物品ID } -- 物品名
            m_item = re.match(r'\{\s*\d+\s*,\s*(\d+)\s*\}\s*,?\s*--\s*(.+)', stripped)
            if not m_item:
                m_item = re.match(r'\{\s*\d+\s*,\s*(\d+)\s*\}', stripped)
            if m_item and current_diff:
                item_id = int(m_item.group(1))
                item_name = m_item.group(2).strip() if m_item.lastindex >= 2 else ""

                item_data = {'item_id': item_id, 'name': item_name}

                if current_diff == 'normal':
                    current_boss['items_normal'].append(item_data)
                elif current_diff == 'heroic':
                    current_boss['items_heroic'].append(item_data)
                elif current_diff == '10':
                    current_boss['items_10'].append(item_data)
                elif current_diff == '25':
                    current_boss['items_25'].append(item_data)
                elif current_diff == '10h':
                    current_boss['items_10h'].append(item_data)
                elif current_diff == '25h':
                    current_boss['items_25h'].append(item_data)

        # 副本块关闭（items表结束）
        if stripped == '}' and current_instance is not None and current_boss is None:
            # 检查是否是副本的最外层关闭
            # 需要判断是否在items块内
            pass

    return instances


def _extract_boss_blocks(inst_block: str, items_start: int) -> list:
    """从副本块中提取所有Boss块"""
    blocks = []
    # 在items区域内找所有 { -- comment 开头的顶层块
    search_area = inst_block[items_start:] if items_start > 0 else inst_block

    i = 0
    while i < len(search_area):
        # 找 { -- 开头
        if search_area[i] == '{':
            # 检查后面是否跟着 -- comment
            rest = search_area[i+1:i+50].lstrip()
            if rest.startswith('--'):
                # 找到Boss块起始，匹配到对应的 }
                depth = 1
                j = i + 1
                while j < len(search_area) and depth > 0:
                    if search_area[j] == '{':
                        depth += 1
                    elif search_area[j] == '}':
                        depth -= 1
                    j += 1
                blocks.append(search_area[i+1:j-1])
                i = j
                continue
        i += 1
    return blocks


def parse_dungeon_data_v2(filepath: str, cn_map: dict):
    """
    更健壮的解析器 - 按块提取
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    instances = []

    # 找到所有 data["XXX"] = { ... } 块
    for m in re.finditer(r'data\["(\w+)"\]\s*=\s*\{', content):
        inst_key = m.group(1)
        start = m.end()

        # 找到匹配的 }
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
            i += 1
        inst_block = content[start:i-1]

        # 解析副本属性
        inst = {
            'key': inst_key,
            'name': None,
            'instance_id': None,
            'encounter_journal_id': None,
            'bosses': [],
        }

        # 提取name
        m_name = re.search(r'name\s*=\s*(?:format\()?AL\["(.+?)"\]', inst_block)
        if m_name:
            inst['name'] = cn_map.get(m_name.group(1), m_name.group(1))

        # 提取InstanceID
        m_id = re.search(r'InstanceID\s*=\s*(\d+)', inst_block)
        if m_id:
            inst['instance_id'] = int(m_id.group(1))

        # 提取EncounterJournalID（副本的）
        m_ej = re.search(r'^\s*EncounterJournalID\s*=\s*(\d+)', inst_block, re.MULTILINE)
        if m_ej:
            inst['encounter_journal_id'] = int(m_ej.group(1))

        # 提取Boss块 - 找所有以 { -- comment 开头的块
        # 不再依赖items_content，直接在整个inst_block中查找Boss
        # Boss块特征: 以 { -- SomeBossKey 开头，包含 name = AL["..."] 和 npcID

        # 先找 items = { 的起始位置
        items_start_match = re.search(r'items\s*=\s*\{', inst_block)
        if items_start_match:
            items_start_pos = items_start_match.end()
        else:
            items_start_pos = 0

        # 找所有Boss块: { -- BossComment
        # 用简单的逐字符扫描来找嵌套的Boss块
        boss_list = _extract_boss_blocks(inst_block, items_start_pos)

        for boss_block in boss_list:
            boss = {
                'key': '',
                'name': None,
                'npc_id': None,
                'encounter_journal_id': None,
                'loot': [],
            }

            # Boss comment key
            bm_key = re.match(r'\s*--\s*(\S+)', boss_block)
            if bm_key:
                boss['key'] = bm_key.group(1)

            # Boss name
            bm_name = re.search(r'name\s*=\s*AL\["(.+?)"\]', boss_block)
            if bm_name:
                boss['name'] = cn_map.get(bm_name.group(1), bm_name.group(1))

            # Boss npcID
            bm_npc = re.search(r'npcID\s*=\s*\{?(\d+)', boss_block)
            if bm_npc:
                boss['npc_id'] = int(bm_npc.group(1))

            # Boss EncounterJournalID
            bm_ej = re.search(r'EncounterJournalID\s*=\s*(\d+)', boss_block)
            if bm_ej:
                boss['encounter_journal_id'] = int(bm_ej.group(1))

            # 提取物品: { 数字, 数字 } 模式
            for item_m in re.finditer(r'\{\s*\d+\s*,\s*(\d+)\s*\}', boss_block):
                item_id = int(item_m.group(1))
                # 检查行尾是否有注释
                line_start = boss_block.rfind('\n', 0, item_m.start()) + 1
                line_end = boss_block.find('\n', item_m.end())
                if line_end == -1:
                    line_end = len(boss_block)
                full_line = boss_block[line_start:line_end]
                comment_m = re.search(r'--\s*(.+)', full_line)
                item_comment = comment_m.group(1).strip() if comment_m else ""
                boss['loot'].append({
                    'item_id': item_id,
                    'name': item_comment,
                })

            inst['bosses'].append(boss)

        instances.append(inst)

    return instances


def get_boss_icon_url(npc_id: int, boss_name: str = "") -> str:
    """
    生成Boss图标URL
    使用WoW经典服的图标服务
    """
    if not npc_id or npc_id <= 0:
        return None
    
    # 根据Boss名字选择不同的图标
    boss_name_lower = boss_name.lower() if boss_name else ""
    
    # 龙类Boss
    if any(keyword in boss_name_lower for keyword in ["dragon", "wyrm", "drake", "龙"]):
        return "https://wow.zamimg.com/images/wow/icons/large/inv_misc_head_dragon_01.jpg"
    
    # 亡灵/骷髅Boss
    elif any(keyword in boss_name_lower for keyword in ["lich", "undead", "skeleton", "lich king", "亡灵", "骷髅"]):
        return "https://wow.zamimg.com/images/wow/icons/large/inv_misc_monsterscull_06.jpg"
    
    # 恶魔Boss
    elif any(keyword in boss_name_lower for keyword in ["demon", "demonic", "恶魔"]):
        return "https://wow.zamimg.com/images/wow/icons/large/inv_misc_head_demon_01.jpg"
    
    # 巨人Boss
    elif any(keyword in boss_name_lower for keyword in ["giant", "titan", "巨人", "泰坦"]):
        return "https://wow.zamimg.com/images/wow/icons/large/inv_misc_monsterscull_07.jpg"
    
    # 元素Boss
    elif any(keyword in boss_name_lower for keyword in ["elemental", "fire", "water", "earth", "air", "元素"]):
        return "https://wow.zamimg.com/images/wow/icons/large/inv_elemental_primal_fire.jpg"
    
    # 默认Boss图标
    else:
        return "https://wow.zamimg.com/images/wow/icons/large/inv_misc_monsterscull_06.jpg"




def import_to_sqlite(instances: list, db_path: str):
    """导入SQLite"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 清空旧数据
    cursor.execute("DELETE FROM boss_loot")
    cursor.execute("DELETE FROM bosses")
    cursor.execute("DELETE FROM dungeons")
    cursor.execute("DELETE FROM items")
    conn.commit()

    d_count = 0
    b_count = 0
    i_count = 0
    l_count = 0

    for inst in instances:
        if not inst.get('name'):
            continue

        # 插入副本
        dungeon_id = inst.get('instance_id') or hash(inst['key']) % 100000
        try:
            cursor.execute(
                """INSERT OR REPLACE INTO dungeons (dungeon_id, name, minimum_level, modes)
                   VALUES (?, ?, ?, ?)""",
                (dungeon_id, inst['name'], 70, '["normal","heroic","10","25"]')
            )
            d_count += 1
        except Exception as e:
            print(f"  副本导入失败 {inst['name']}: {e}")
            continue

        # 插入Boss和掉落
        for boss in inst.get('bosses', []):
            if not boss.get('name'):
                continue

            boss_id = boss.get('npc_id') or boss.get('encounter_journal_id') or hash(boss['key']) % 100000
            icon_url = get_boss_icon_url(boss.get('npc_id'), boss.get('name', ''))
            try:
                cursor.execute(
                    """INSERT OR REPLACE INTO bosses (boss_id, name, dungeon_id, dungeon_name, icon_url)
                       VALUES (?, ?, ?, ?, ?)""",
                    (boss_id, boss['name'], dungeon_id, inst['name'], icon_url)
                )
                b_count += 1
            except Exception as e:
                print(f"  Boss导入失败 {boss['name']}: {e}")
                continue

            # 插入掉落物品
            for loot in boss.get('loot', []):
                item_id = loot.get('item_id')
                if not item_id or item_id < 1:
                    continue
                try:
                    cursor.execute(
                        """INSERT OR REPLACE INTO items (item_id, name, quality)
                           VALUES (?, ?, ?)""",
                        (item_id, loot.get('name', ''), 'common')
                    )
                    i_count += 1
                except Exception:
                    pass
                # 插入boss→item关联
                try:
                    cursor.execute(
                        """INSERT OR IGNORE INTO boss_loot (boss_id, item_id, item_name)
                           VALUES (?, ?, ?)""",
                        (boss_id, item_id, loot.get('name', ''))
                    )
                    l_count += 1
                except Exception:
                    pass

    conn.commit()
    conn.close()

    print(f"\n导入完成！")
    print(f"  副本: {d_count}")
    print(f"  Boss: {b_count}")
    print(f"  物品: {i_count}")
    print(f"  掉落关联: {l_count}")


def main():
    print("AtlasLootMY 数据导入工具")
    print("=" * 50)

    # 1. 加载中文翻译
    cn_map = {}

    # 加载副本模块的翻译
    cn_file = os.path.join(ADDON_DIR, "AtlasLootMY_DungeonsAndRaids", "Locales", "constants.cn.lua")
    cn_map.update(parse_cn_locales(cn_file))
    print(f"加载中文翻译: {len(cn_map)} 条")

    # 2. 解析数据文件
    all_instances = []

    # WotLK 副本数据
    wrath_file = os.path.join(ADDON_DIR, "AtlasLootMY_DungeonsAndRaids", "data-wrath.lua")
    if os.path.exists(wrath_file):
        print(f"解析: {wrath_file}")
        instances = parse_dungeon_data_v2(wrath_file, cn_map)
        print(f"  找到 {len(instances)} 个副本")
        all_instances.extend(instances)

    # TBC 副本数据
    tbc_file = os.path.join(ADDON_DIR, "AtlasLootMY_DungeonsAndRaids", "data-tbc.lua")
    if os.path.exists(tbc_file):
        print(f"解析: {tbc_file}")
        instances = parse_dungeon_data_v2(tbc_file, cn_map)
        print(f"  找到 {len(instances)} 个副本")
        all_instances.extend(instances)

    # 经典副本数据
    classic_file = os.path.join(ADDON_DIR, "AtlasLootMY_DungeonsAndRaids", "data.lua")
    if os.path.exists(classic_file):
        print(f"解析: {classic_file}")
        instances = parse_dungeon_data_v2(classic_file, cn_map)
        print(f"  找到 {len(instances)} 个副本")
        all_instances.extend(instances)

    # 3. 导入
    print(f"\n目标数据库: {DATA_DB}")
    import_to_sqlite(all_instances, DATA_DB)


if __name__ == "__main__":
    main()
