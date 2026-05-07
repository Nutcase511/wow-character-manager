"""
解析WoW插件导出的SavedVariables数据并导入SQLite
"""
import json
import os
import re
import sqlite3
import sys


def parse_lua_table(filepath: str) -> dict:
    """简单的Lua表解析器，提取WoWDataExporterDB数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        "instances": [],
        "bosses": [],
        "items": {},
    }

    # 使用简单的方式：逐行解析
    # 找到instances数组
    current_section = None
    current_instance = None
    current_boss = None
    current_loot = None

    lines = content.split('\n')
    for line in lines:
        line = line.strip()

        # 检测section
        if '["instances"]' in line and '{' in line:
            current_section = "instances"
            continue
        elif '["bosses"]' in line and '{' in line:
            current_section = "bosses"
            continue
        elif '["items"]' in line and '{' in line:
            current_section = "items"
            continue

        # 解析键值对
        if '=' not in line:
            continue

        # 提取 key = value
        match = re.match(r'^\["?(\w+)"?\]\s*=\s*(.+)$', line)
        if not match:
            match = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if not match:
            continue

        key = match.group(1).strip('"')
        value = match.group(2).strip().rstrip(',')

        # 跳过table类型的值
        if value == '{' or value == '{}':
            continue
        if value == 'nil' or value == 'None':
            continue

        # 解析值
        parsed_value = _parse_value(value)
        if parsed_value is None:
            continue

        # 根据当前上下文存储
        if key == 'instanceID':
            current_instance = _ensure_current(result['instances'], 'instanceID', parsed_value)
        elif key == 'encounterID':
            current_boss = _ensure_current(result['bosses'], 'encounterID', parsed_value)
        elif key == 'itemID' and current_section == 'items':
            pass  # items表用itemID作为key
        elif current_section == 'items' and key not in ('instanceID', 'encounterID'):
            # 全局items表
            pass

        if current_instance is not None and key in ('instanceID', 'name', 'description', 'tierName', 'minimumLevel'):
            current_instance[key] = parsed_value

        if current_boss is not None and key in ('encounterID', 'name', 'description', 'instanceID', 'instanceName'):
            current_boss[key] = parsed_value

    return result


def _parse_value(value: str):
    """解析Lua值"""
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value == 'true':
        return True
    if value == 'false':
        return False
    if value == 'nil' or value == 'None':
        return None
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _ensure_current(lst, id_key, id_val):
    """确保列表中有对应ID的条目"""
    for item in lst:
        if item.get(id_key) == id_val:
            return item
    new_item = {id_key: id_val}
    lst.append(new_item)
    return new_item


def parse_saved_vars(filepath: str) -> dict:
    """
    更健壮的解析器 - 将Lua表转为Python字典
    使用正则表达式逐块解析
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    instances = []
    bosses = []
    items = {}
    export_time = None

    # 提取 exportTime
    m = re.search(r'exportTime\s*=\s*(\d+)', content)
    if m:
        export_time = int(m.group(1))

    # 提取 instances 数组中的每个instance块
    # 找到 ["instances"] = { ... } 块
    inst_section = _extract_section(content, '["instances"]')
    if inst_section:
        # 找到每个 { ... } 子块
        inst_blocks = _extract_blocks(inst_section)
        for block in inst_blocks:
            inst = _parse_block(block)
            if inst and inst.get('instanceID'):
                # 提取instance内的bosses子块
                boss_section = _extract_section(block, 'bosses')
                inst_bosses = []
                if boss_section:
                    boss_blocks = _extract_blocks(boss_section)
                    for bb in boss_blocks:
                        boss = _parse_block(bb)
                        if boss and boss.get('encounterID'):
                            # 提取boss内的loot子块
                            loot_section = _extract_section(bb, 'loot')
                            loot_list = []
                            if loot_section:
                                loot_blocks = _extract_blocks(loot_section)
                                for lb in loot_blocks:
                                    loot = _parse_block(lb)
                                    if loot and loot.get('itemID'):
                                        loot_list.append(loot)
                                        # 同时加入全局items
                                        items[loot['itemID']] = loot
                            boss['_loot'] = loot_list
                            inst_bosses.append(boss)
                inst['_bosses'] = inst_bosses
                instances.append(inst)

    # 提取 bosses 数组（扁平列表，用于参考）
    boss_section = _extract_section(content, '["bosses"]')
    if boss_section:
        boss_blocks = _extract_blocks(boss_section)
        for bb in boss_blocks:
            boss = _parse_block(bb)
            if boss and boss.get('encounterID'):
                bosses.append(boss)

    # 提取全局items
    items_section = _extract_section(content, '["items"]')
    if items_section:
        # items 是 dict 形式: [itemID] = { ... }
        item_blocks = _extract_blocks(items_section)
        for ib in item_blocks:
            item = _parse_block(ib)
            if item and item.get('itemID'):
                items[item['itemID']] = item

    return {
        'export_time': export_time,
        'instances': instances,
        'bosses': bosses,
        'items': items,
    }


def _extract_section(content: str, key: str) -> str:
    """提取指定key对应的 {} 块内容"""
    # 查找 key = { 的位置
    pattern = re.escape(key) + r'\s*=\s*\{'
    m = re.search(pattern, content)
    if not m:
        return ""

    start = m.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1

    return content[start:i-1]


def _extract_blocks(content: str) -> list:
    """提取内容中所有顶层 { ... } 块"""
    blocks = []
    i = 0
    while i < len(content):
        if content[i] == '{':
            depth = 1
            start = i + 1
            i += 1
            while i < len(content) and depth > 0:
                if content[i] == '{':
                    depth += 1
                elif content[i] == '}':
                    depth -= 1
                i += 1
            blocks.append(content[start:i-1])
        else:
            i += 1
    return blocks


def _parse_block(block: str) -> dict:
    """解析 { key = value, ... } 块"""
    result = {}
    for line in block.split('\n'):
        line = line.strip().rstrip(',')
        if '=' not in line:
            continue

        # 匹配 ["key"] = value 或 key = value
        m = re.match(r'^\["?(\w+)"?\]\s*=\s*(.+)$', line)
        if not m:
            m = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue

        key = m.group(1).strip('"')
        value = m.group(2).strip()

        if value == '{' or value == '{}' or value == 'nil':
            continue

        result[key] = _parse_value(value)

    return result


def import_to_sqlite(data: dict, db_path: str = "./wow_character_manager.db"):
    """将解析后的数据导入SQLite"""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 清空旧数据
    cursor.execute("DELETE FROM bosses")
    cursor.execute("DELETE FROM dungeons")
    cursor.execute("DELETE FROM items")
    conn.commit()

    # 导入副本
    dungeon_count = 0
    for inst in data.get('instances', []):
        if not inst.get('instanceID'):
            continue
        try:
            cursor.execute(
                """INSERT OR REPLACE INTO dungeons (dungeon_id, name, description, minimum_level, modes)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    inst['instanceID'],
                    inst.get('name', ''),
                    inst.get('description', ''),
                    inst.get('minimumLevel', 70),
                    '["normal", "heroic"]',
                )
            )
            dungeon_count += 1

            # 导入该副本下的Boss
            for boss in inst.get('_bosses', []):
                if not boss.get('encounterID'):
                    continue
                try:
                    cursor.execute(
                        """INSERT OR REPLACE INTO bosses (boss_id, name, description, dungeon_id, dungeon_name)
                           VALUES (?, ?, ?, ?, ?)""",
                        (
                            boss['encounterID'],
                            boss.get('name', ''),
                            boss.get('description', ''),
                            inst['instanceID'],
                            inst.get('name', ''),
                        )
                    )

                    # 导入Boss掉落物品
                    for loot in boss.get('_loot', []):
                        if not loot.get('itemID'):
                            continue
                        try:
                            cursor.execute(
                                """INSERT OR REPLACE INTO items (item_id, name, quality, item_level, slot)
                                   VALUES (?, ?, ?, ?, ?)""",
                                (
                                    loot['itemID'],
                                    loot.get('name', ''),
                                    loot.get('quality', 'common'),
                                    loot.get('itemLevel', 0),
                                    loot.get('slot'),
                                )
                            )
                        except Exception as e:
                            print(f"  导入物品失败 {loot.get('name', '?')}: {e}")

                except Exception as e:
                    print(f"  导入Boss失败 {boss.get('name', '?')}: {e}")

        except Exception as e:
            print(f"导入副本失败 {inst.get('name', '?')}: {e}")

    conn.commit()

    # 统计
    cursor.execute("SELECT COUNT(*) FROM dungeons")
    d_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM bosses")
    b_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM items")
    i_count = cursor.fetchone()[0]

    conn.close()

    print(f"\n导入完成！")
    print(f"  副本: {d_count}")
    print(f"  Boss: {b_count}")
    print(f"  物品: {i_count}")


def main():
    print("WoW数据导入工具 (SavedVariables -> SQLite)")
    print("=" * 50)

    # 查找SavedVariables文件
    default_path = r"C:\WOW\World of Warcraft\_classic_titan_\WTF\Account\*\SavedVariables\WoWDataExporter.lua"

    import glob
    files = glob.glob(default_path)

    if not files:
        # 尝试当前目录
        if os.path.exists("WoWDataExporter.lua"):
            files = ["WoWDataExporter.lua"]

    if not files:
        print("未找到WoWDataExporter.lua文件！")
        print("请确保：")
        print("  1. 已安装WoWDataExporter插件")
        print("  2. 在游戏中输入 /wowexport 导出数据")
        print("  3. 退出游戏或 /reload 保存数据")
        print(f"\n预期路径: {default_path}")
        filepath = input("请手动输入文件路径（或按Enter退出）: ").strip()
        if filepath and os.path.exists(filepath):
            files = [filepath]
        else:
            return

    filepath = files[0]
    print(f"读取文件: {filepath}")

    if not os.path.exists(filepath):
        print(f"文件不存在: {filepath}")
        return

    # 解析数据
    print("\n解析数据...")
    data = parse_saved_vars(filepath)

    inst_count = len(data.get('instances', []))
    boss_count = len(data.get('bosses', []))
    item_count = len(data.get('items', {}))

    print(f"解析结果:")
    print(f"  副本: {inst_count}")
    print(f"  Boss: {boss_count}")
    print(f"  物品: {item_count}")

    if inst_count == 0:
        print("\n没有解析到副本数据！可能原因：")
        print("  1. 尚未在游戏中输入 /wowexport")
        print("  2. 导出后未退出游戏或 /reload")
        return

    # 确认导入
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wow_character_manager.db")
    print(f"\n目标数据库: {db_path}")
    confirm = input("确认导入？这将清空现有副本/Boss/物品数据 (y/n): ").strip().lower()
    if confirm != 'y':
        print("操作取消")
        return

    # 导入
    import_to_sqlite(data, db_path)


if __name__ == "__main__":
    main()
