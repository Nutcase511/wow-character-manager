"""
从tdInspect插件数据中同步角色等级、职业信息
数据来源：tdInspect插件的SavedVariables文件

tdInspect.lua 实际结构:
  TDDB_INSPECT2 = {
    ["userCache"] = {
      ["角色名-服务器"] = {
        ["proto"] = { ... },          -- proto内部有其他嵌套数据
        ["glyphs"] = { ... },         -- 同级字段
        ["class"] = 11,               -- 职业ID
        ["race"] = 6,                 -- 种族ID
        ["level"] = 80,               -- 等级
        ["activeGroup"] = 2,          -- 当前天赋组
        ["timestamp"] = 1777173557,
        ["equips"] = { "item:...", ... },
        ["talents"] = { { "053200310", "", "..." }, ... },
      }
    }
  }
  注意：class/level/race 和 proto 同级，都在角色块外层

tdInspect 角色名格式: "暮小晴-时光II理想国"（无空格）
数据库角色名格式:   "暮小晴-时光II - 理想国"（有空格）
"""

import re
import sqlite3
import os
from datetime import datetime

# tdInspect 职业ID -> 数据库职业名 (WoW Classic Wrath)
CLASS_ID_MAP_WOTLK = {
    1: "warrior",
    2: "paladin",
    3: "hunter",
    4: "rogue",
    5: "priest",
    6: "death_knight",
    7: "shaman",
    8: "mage",
    9: "warlock",
    10: "druid",
    11: "druid",  # Wrath Classic 中 class 11 = Druid
}

# tdInspect 种族ID -> 种族名
RACE_ID_MAP = {
    1: "human",
    2: "orc",
    3: "dwarf",
    4: "night_elf",
    5: "undead",
    6: "tauren",
    7: "gnome",
    8: "troll",
    9: "goblin",
    10: "blood_elf",
    11: "draenei",
    22: "worgen",
    24: "pandaren",
}

# 插件目录
ADDON_DIR = r"C:\WOW\World of Warcraft\_classic_titan_\WTF\Account\224692699#1\SavedVariables"
TDINSPECT_FILE = os.path.join(ADDON_DIR, "tdInspect.lua")


def extract_block(content: str, start: int) -> str:
    """从 start 位置（{ 之后）提取配对 {} 块，返回块内容（不含大括号）"""
    depth = 0
    block_start = start + 1
    i = start
    while i < len(content):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth < 0:
                break
        i += 1
    return content[block_start:i]


def parse_char_block_fields(block: str) -> dict:
    """
    解析角色块中的所有字段（class, level, race, talents, equips 等）。
    这些字段和 proto 同级，都在角色块外层。
    proto/glyphs 等子块直接跳过（深度 >= 1 时遇到的 { 不计入顶层字段）。
    """
    result = {
        "class": None,
        "race": None,
        "level": None,
        "activeGroup": None,
        "timestamp": None,
        "talents": [],
        "equips": [],
    }

    # 首先提取整个块的 equips 和 talents 数组
    # equips = { "item:1234:...", "item:5678:...", ... }
    equips_match = re.search(r'\["equips"\]\s*=\s*\{([^}]*)\}', block, re.DOTALL)
    if equips_match:
        equips_content = equips_match.group(1)
        # 提取所有 "item:..." 字符串
        equips = re.findall(r'"(item:[^"]+)"', equips_content)
        result["equips"] = equips
    
    # talents = { { "053200310", "", ... }, { ... } }
    talents_match = re.search(r'\["talents"\]\s*=\s*\{([^}]*\{[^}]*\}[^}]*)\}', block, re.DOTALL)
    if talents_match:
        talents_content = talents_match.group(1)
        # 提取每个天赋组
        talent_groups = re.findall(r'\{([^}]*)\}', talents_content)
        for group in talent_groups:
            # 提取字符串
            talents = re.findall(r'"([^"]*)"', group)
            if talents:
                result["talents"].append(talents)

    lines = block.split("\n")
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line == "{" or line == "}," or line == "}":
            continue
        line = line.rstrip(",")

        # 匹配 ["key"] = value (Lua中可能有空格: [ "class" ] = 11)
        m = re.match(r'^\["\s*(\w+)\s*"\]\s*=\s*(.+)$', line)
        if not m:
            m = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue

        key = m.group(1)
        raw_value = m.group(2).strip()

        # 跳过子块（值以 { 开头）
        if raw_value == "{" or raw_value.startswith("{}"):
            continue

        if key == "level":
            try:
                result["level"] = int(raw_value)
            except ValueError:
                pass
        elif key == "class":
            try:
                result["class"] = int(raw_value)
            except ValueError:
                pass
        elif key == "race":
            try:
                result["race"] = int(raw_value)
            except ValueError:
                pass
        elif key == "activeGroup":
            try:
                result["activeGroup"] = int(raw_value)
            except ValueError:
                pass
        elif key == "timestamp":
            try:
                result["timestamp"] = int(raw_value)
            except ValueError:
                pass

    return result


def parse_tdinspect_lua(filepath: str) -> list:
    """解析tdInspect.lua，返回角色信息列表"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    result = []

    # 找 ["userCache"] = {
    user_cache_match = re.search(r'\["userCache"\]\s*=\s*\{', content)
    if not user_cache_match:
        print("未找到 [userCache] 节点")
        return result

    # 提取 userCache 块内容
    user_cache_start = user_cache_match.end()
    depth = 1
    i = user_cache_start
    while i < len(content) and depth > 0:
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
        i += 1
    user_cache_content = content[user_cache_start:i - 1]

    print(f"userCache 块长度: {len(user_cache_content)} 字符")

    # 逐字符解析每个角色块
    i = 0
    parsed_count = 0
    empty_count = 0

    while i < len(user_cache_content):
        ch = user_cache_content[i]
        if ch in (" ", "\t", "\n", "\r"):
            i += 1
            continue
        if ch != "[":
            i += 1
            continue

        # 匹配 ["name"] = {
        m = re.match(r'\[([=]?["\'])(.+?)\1\]\s*=\s*\{', user_cache_content[i:])
        if not m:
            i += 1
            continue

        char_name = m.group(2)
        i += m.end()  # 移动到 { 之后

        # 提取整个角色块（配对大括号）
        depth = 1
        block_start = i
        while i < len(user_cache_content) and depth > 0:
            if user_cache_content[i] == "{":
                depth += 1
            elif user_cache_content[i] == "}":
                depth -= 1
            i += 1
        char_block = user_cache_content[block_start:i - 1]

        # 解析角色块（class/level/race 等字段和 proto 同级）
        char_data = parse_char_block_fields(char_block)
        char_data["name"] = char_name

        if char_data["class"] is not None or char_data["level"] is not None:
            result.append(char_data)
            parsed_count += 1
        else:
            empty_count += 1

    print(f"解析结果: 有数据 {parsed_count} 个, 无数据 {empty_count} 个")
    return result


def name_to_key(name: str) -> str:
    """
    提取角色名（去掉 -服务器 部分）用于与数据库匹配
    tdInspect: "暮小晴-时光II理想国" → "暮小晴"
    数据库: "暮小晴" → "暮小晴"
    """
    if "-" in name:
        return name.split("-", 1)[0]
    return name


def main():
    print("=" * 50)
    print("tdInspect 角色数据同步工具")
    print("=" * 50)

    if not os.path.exists(TDINSPECT_FILE):
        print(f"\n文件不存在: {TDINSPECT_FILE}")
        return

    mtime = os.path.getmtime(TDINSPECT_FILE)
    print(f"\n读取文件: {TDINSPECT_FILE}")
    print(f"文件修改时间: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")

    characters = parse_tdinspect_lua(TDINSPECT_FILE)

    if not characters:
        print("没有解析到角色数据！")
        return

    print(f"\n共 {len(characters)} 个有数据的角色，预览前10个:")
    for c in characters[:10]:
        cls = CLASS_ID_MAP_WOTLK.get(c["class"], f"classID:{c['class']}")
        race = RACE_ID_MAP.get(c["race"], str(c["race"]) if c["race"] else "unknown")
        ts = datetime.fromtimestamp(c["timestamp"]) if c["timestamp"] else None
        # tdInspect name 格式: "暮小晴-时光II理想国"
        # 标准化: 去掉所有空格后与数据库比对
        tdi_norm = c["name"].replace(" ", "")
        print(f"  {c['name']}  Lv.{c['level']} {cls}/{race} "
              f"天赋组:{c['activeGroup']} 扫描:{ts.strftime('%m-%d %H:%M') if ts else '?'}")

    # 连接数据库
    db_path = r"C:\wow后台管理\wow-character-manager\backend\wow_character_manager.db"
    print(f"\n数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, realm, wow_class, level FROM characters")
    db_chars = list(cursor.fetchall())
    print(f"数据库中有 {len(db_chars)} 个角色")

    # 建立索引: 角色名（不含服务器）-> 数据库行
    by_char_name = {}
    for row in db_chars:
        by_char_name[row["name"]] = dict(row)

    now = datetime.utcnow().isoformat()
    updated = 0
    skipped = 0
    not_found = []

    for c in characters:
        cls_id = c["class"]
        char_class = CLASS_ID_MAP_WOTLK.get(cls_id, None)
        if not char_class:
            print(f"  跳过 {c['name']}: 未知职业ID {cls_id}")
            skipped += 1
            continue

        char_level = c["level"] or 0

        # 匹配: 提取 tdInspect 名字的角色名部分（-服务器前）
        char_name = name_to_key(c["name"])
        matched_row = by_char_name.get(char_name)

        if matched_row:
            updates = []
            if matched_row["wow_class"] != char_class:
                updates.append(f"职业 {matched_row['wow_class']}->{char_class}")
            if matched_row["level"] != char_level and char_level > 0:
                updates.append(f"等级 {matched_row['level']}->{char_level}")

            if updates:
                cursor.execute(
                    "UPDATE characters SET wow_class=?, level=?, updated_at=? WHERE id=?",
                    (char_class, char_level, now, matched_row["id"])
                )
                print(f"  [更新] {matched_row['name']}: {', '.join(updates)}")
                updated += 1
            else:
                print(f"  [跳过] {matched_row['name']}: 数据已是最新")
                skipped += 1
        else:
            not_found.append(c["name"])

    conn.commit()
    conn.close()

    print(f"\n同步完成! 更新 {updated} 条, 跳过 {skipped} 条")
    if not_found:
        print(f"\n未能匹配数据库的角色 ({len(not_found)} 个):")
        for n in not_found[:20]:
            print(f"  - {n}")
        if len(not_found) > 20:
            print(f"  ... 还有 {len(not_found) - 20} 个")


if __name__ == "__main__":
    main()
