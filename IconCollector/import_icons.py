"""
从 WoW 插件的 SavedVariables 文件导入图标映射到数据库
"""
import sqlite3
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "wow_character_manager.db")
WTF_BASE = r"C:\WOW\World of Warcraft\_classic_titan_\WTF\Account"

def find_icon_collector_file():
    """在 WTF 目录下查找 IconCollector.lua 文件"""
    for root, dirs, files in os.walk(WTF_BASE):
        for f in files:
            if f == "IconCollector.lua":
                return os.path.join(root, f)
    return None

def parse_icon_mapping(filepath):
    """解析 SavedVariables Lua 文件中的 IconCollectorDB 数据"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    mapping = {}
    # 匹配所有 ["itemId"] = "icon_name" 或 [itemId] = "icon_name"
    for match in re.finditer(r'\["?(\d+)"?\]\s*=\s*"([^"]+)"', content):
        item_id = int(match.group(1))
        icon_name = match.group(2)
        if item_id <= 0:
            continue
        icon_url = f"https://render.worldofwarcraft.com/icons/56/{icon_name}.jpg"
        mapping[item_id] = icon_url

    return mapping

def update_database(mapping):
    """更新数据库 items 表的 icon_url 字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updated = 0
    not_found = 0

    for item_id, icon_url in sorted(mapping.items()):
        cursor.execute("UPDATE items SET icon_url = ? WHERE item_id = ?", (icon_url, item_id))
        if cursor.rowcount > 0:
            updated += 1
        else:
            not_found += 1

    conn.commit()
    conn.close()

    print(f"数据库更新完成:")
    print(f"  - 总处理 {len(mapping)} 个物品")
    print(f"  - 成功更新 {updated} 条")
    print(f"  - 未匹配 {not_found} 条（数据库中不存在该 item_id）")

def main():
    print("正在查找 IconCollector.lua...")
    filepath = find_icon_collector_file()

    if not filepath:
        print(f"未在 {WTF_BASE} 下找到 IconCollector.lua 文件")
        print("请确认以下路径是否存在:")
        print(r"  C:\WOW\World of Warcraft\_classic_titan_\Interface\AddOns\IconCollector\")
        print("以及已在游戏中执行过 /ic scan 和 /ic export")
        return

    print(f"找到文件: {filepath}")
    print("正在解析图标映射...")

    mapping = parse_icon_mapping(filepath)
    print(f"解析到 {len(mapping)} 个物品图标")

    if not mapping:
        print("未解析到任何图标数据，请确认已在游戏中执行了 /ic scan")
        return

    update_database(mapping)

if __name__ == "__main__":
    main()