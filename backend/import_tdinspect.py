"""
从tdInspect插件数据中同步角色等级、职业信息
数据来源：tdInspect插件的SavedVariables文件

tdInspect.lua 结构:
  TDDB_INSPECT2 = {
    ["profileKeys"] = { ["角色名 - 服务器"] = "Default", ... }
    ["global"] = {
      ["characters"] = {
        ["角色名-服务器"] = {
          ["class"] = 11,       -- 职业ID
          ["race"] = 6,         -- 种族ID
          ["level"] = 80,       -- 等级
          ["talents"] = {
            { "053200310", "", "231013312231502431052313051" },
            { "510221310523130321332531113100", "", "205003012" },
          },
          ["equips"] = { "item:257664:...", ... },
          ["timestamp"] = 1777173557,
        }
      }
    }
  }
"""

import re
import sqlite3
import os
from datetime import datetime

# tdInspect 职业ID -> 数据库职业名 (Wrath Classic)
CLASS_ID_MAP = {
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
    11: "monk",   # Wrath Classic中11=Druid, Monk不存在
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


def parse_tdinspect_lua(filepath: str) -> list:
    """解析tdInspect.lua，返回角色信息列表"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    result = []

    # 提取 ["global"] = { ["characters"] = { ... } } 块
    # 先找 global = {
    global_match = re.search(r'\["global"\]\s*=\s*\{', content)
    if not global_match:
        print("未找到 [\"global\"] 节点")
        return result

    # 提取 global 块内容
    start = global_match.end()
    depth = 1
    i = start
    while i < len(content) and depth > 0:
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
        i += 1
    global_content = content[start:i - 1]

    # 在 global 块中找 ["characters"] = {
    chars_match = re.search(r'\["characters"\]\s*=\s*\{', global_content)
    if not chars_match:
        print("未找到 [\"characters\"] 节点")
        return result

    # 提取 characters 块内容
    start = chars_match.end()
    depth = 1
    i = start
    while i < len(global_content) and depth > 0:
        if global_content[i] == "{":
            depth += 1
        elif global_content[i] == "}":
            depth -= 1
        i += 1
    chars_content = global_content[start:i - 1]

    # 逐字符解析每个角色块 [name] = { ... }
    i = 0
    while i < len(chars_content):
        # 找 ["] 或 ['
        if chars_content[i] not in ("[", " "):
            i += 1
            continue

        if chars_content[i] == " ":
            i += 1
            continue

        # 提取 [key]
        m = re.match(r'\[(=?["\'])(.+?)\1\]\s*=\s*\{', chars_content[i:])
        if not m:
            i += 1
            continue

        char_name = m.group(2)
        i += m.end()

        # 提取该角色块内容（平衡括号）
        depth = 1
        start = i
        while i < len(chars_content) and depth > 0:
            if chars_content[i] == "{":
                depth += 1
            elif chars_content[i] == "}":
                depth -= 1
            i += 1
        char_block = chars_content[start:i - 1]

        # 解析该角色块中的字段
        char_data = _parse_char_block(char_block)
        char_data["name"] = char_name
        result.append(char_data)

    return result


def _parse_char_block(block: str) -> dict:
    """解析单个角色的 { key = value, ... } 块"""
    result = {
        "class": None,
        "race": None,
        "level": None,
        "talents": [],
        "equips": [],
        "timestamp": None,
    }

    # 简单逐行解析
    for line in block.split("\n"):
        line = line.strip().rstrip(",")
        if "=" not in line:
            continue

        # 提取 key = value
        m = re.match(r'^\["?(\w+)"?\]\s*=\s*(.+)$', line)
        if not m:
            m = re.match(r'^(\w+)\s*=\s*(.+)$', line)
        if not m:
            continue

        key = m.group(1)
        raw_value = m.group(2).strip()

        if key == "tdInspect":
            continue

        if key == "level":
            try:
                result["level"] = int(raw_value)
            except:
                pass
        elif key == "class":
            try:
                result["class"] = int(raw_value)
            except:
                pass
        elif key == "race":
            try:
                result["race"] = int(raw_value)
            except:
                pass
        elif key == "timestamp":
            try:
                result["timestamp"] = int(raw_value)
            except:
                pass
        elif key == "talents":
            # talents = { { "...", "", "..." }, { "...", "", "..." } }
            talents = _extract_array(raw_value)
            result["talents"] = talents
        elif key == "equips":
            # equips = { "item:...", "item:...", nil, ... }
            equips = _extract_array(raw_value)
            result["equips"] = [e for e in equips if e]

    return result


def _extract_array(block_str: str) -> list:
    """从 = { ... } 或直接数组块中提取值列表"""
    # 去掉前后 { }
    inner = block_str.strip()
    if inner.startswith("{"):
        inner = inner[1:]
    if inner.endswith("}"):
        inner = inner[:-1]
    inner = inner.strip()

    if not inner:
        return []

    results = []
    # 用逗号分割（忽略括号内的逗号）
    depth = 0
    current = ""
    for ch in inner:
        if ch in ("{", "["):
            depth += 1
            current += ch
        elif ch in ("}", "]"):
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            val = current.strip()
            if val:
                # 去掉引号
                if (val.startswith('"') and val.endswith('"')) or \
                   (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                elif val == "nil":
                    val = None
                results.append(val)
            current = ""
        else:
            current += ch
    if current.strip():
        val = current.strip()
        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
            val = val[1:-1]
        elif val == "nil":
            val = None
        results.append(val)

    return results


def _normalize_name(name: str) -> tuple:
    """
    标准化角色名为 (name, realm)
    tdInspect: "暮小晴-时光II理想国" → ("暮小晴", "时光II理想国")
    数据库:   "暮小晴-时光II - 理想国" → ("暮小晴", "时光II - 理想国")
    去除多余空格后对比
    """
    name = name.strip()
    # tdInspect 格式: "角色名-服务器"
    # 数据库格式: "角色名-服务器" (实际格式可能是 "角色名 - 服务器" 或 "角色名-服务器")
    
    # 找第一个 - 分隔
    if "-" in name:
        idx = name.index("-")
        char_name = name[:idx].strip()
        realm = name[idx + 1:].strip()
        return char_name, realm
    return name, ""


def normalize_for_match(name: str) -> tuple:
    """返回 (角色名, 服务器名) 标准化后，去掉多余空格"""
    name = name.strip()
    if "-" in name:
        idx = name.index("-")
        char_name = name[:idx].strip()
        realm = name[idx + 1:].strip()
        # 去掉多余空格: "时光II理想国" vs "时光II - 理想国"
        realm = " ".join(realm.split())  # normalize spaces
        return char_name, realm
    return name, ""


def main():
    print("=" * 50)
    print("tdInspect 角色数据同步工具")
    print("=" * 50)

    if not os.path.exists(TDINSPECT_FILE):
        print(f"\n文件不存在: {TDINSPECT_FILE}")
        print("请确认 tdInspect 插件已安装并在游戏中扫描过角色数据")
        return

    # 解析数据
    print(f"\n读取文件: {TDINSPECT_FILE}")
    characters = parse_tdinspect_lua(TDINSPECT_FILE)
    print(f"解析到 {len(characters)} 个角色的tdInspect数据")

    if not characters:
        print("没有解析到角色数据！")
        return

    # 显示解析结果
    print("\n角色数据预览:")
    for c in characters:
        class_name = CLASS_ID_MAP.get(c["class"], f"未知({c['class']})")
        race_name = RACE_ID_MAP.get(c["race"], f"未知({c['race']})")
        talent_count = len([t for t in c["talents"] if t and t[0]])
        equip_count = len(c["equips"])
        ts = datetime.fromtimestamp(c["timestamp"]) if c["timestamp"] else None
        print(f"  {c['name']}: Lv.{c['level']} {class_name}/{race_name}, "
              f"天赋: {talent_count}系, 装备: {equip_count}件, "
              f"扫描: {ts.strftime('%m-%d %H:%M') if ts else '?'}")

    # 连接数据库
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wow_character_manager.db")
    print(f"\n数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 获取数据库中的角色
    cursor.execute("SELECT id, name, realm, wow_class, level FROM characters")
    db_chars = {row["name"]: dict(row) for row in cursor.fetchall()}

    # 也按 (name, realm) 建立索引，用于模糊匹配
    db_index = {}  # (char_name, normalized_realm) -> row
    for row in db_chars.values():
        char_name, realm = normalize_for_match(row["name"])
        key = (char_name, realm)
        db_index[key] = row

    # 尝试直接用 name 做索引
    name_index = {}
    for row in db_chars.values():
        name_index[row["name"]] = row

    print(f"\n数据库中有 {len(db_chars)} 个角色")

    # 同步
    now = datetime.utcnow().isoformat()
    updated = 0
    not_found = []

    for c in characters:
        char_name_tdi, realm_tdi = _normalize_name(c["name"])
        realm_tdi_norm = " ".join(realm_tdi.split())  # 标准化空格

        char_class = CLASS_ID_MAP.get(c["class"], None)
        char_level = c["level"]

        if not char_class:
            print(f"  跳过 {c['name']}: 未知职业ID {c['class']}")
            continue

        # 匹配数据库记录
        matched_row = None

        # 方式1: 直接用 tdInspect 的 name 匹配
        if c["name"] in name_index:
            matched_row = name_index[c["name"]]
        else:
            # 方式2: 用 (角色名, 服务器) 匹配
            key = (char_name_tdi, realm_tdi_norm)
            if key in db_index:
                matched_row = db_index[key]

        if matched_row:
            # 检查是否需要更新
            needs_update = False
            updates = []
            if matched_row["wow_class"] != char_class:
                updates.append(f"职业: {matched_row['wow_class']} → {char_class}")
                needs_update = True
            if matched_row["level"] != char_level:
                updates.append(f"等级: {matched_row['level']} → {char_level}")
                needs_update = True

            if needs_update:
                cursor.execute(
                    """UPDATE characters SET wow_class=?, level=?, updated_at=? WHERE id=?""",
                    (char_class, char_level, now, matched_row["id"])
                )
                print(f"  ✓ 更新 [{matched_row['name']}]: {', '.join(updates)}")
                updated += 1
            else:
                print(f"  - 跳过 [{matched_row['name']}]: 数据已是最新")
        else:
            not_found.append(c["name"])

    conn.commit()
    conn.close()

    print(f"\n同步完成！更新了 {updated} 条记录")
    if not_found:
        print(f"\n未能匹配到数据库的角色 ({len(not_found)} 个):")
        for n in not_found:
            print(f"  - {n}")


if __name__ == "__main__":
    main()
