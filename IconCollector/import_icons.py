"""
从WoW SavedVariables文件导入图标扫描结果到数据库
用法: python IconCollector/import_icons.py
"""
import re
import sys
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

# 尝试多个可能的SavedVariables路径
import os
possible_paths = [
    os.path.expandvars(r'%USERPROFILE%\Documents\WTF\Account\*\SavedVariables\IconCollector.lua'),
    r'C:\WOW\World of Warcraft\_classic_titan_\WTF\Account\*\SavedVariables\IconCollector.lua',
]

import glob
found_file = None
for pattern in possible_paths:
    files = glob.glob(pattern)
    if files:
        found_file = files[0]
        break

if not found_file:
    print("未找到IconCollector.lua SavedVariables文件!")
    print("请确认路径: WTF/Account/<你的账号>/SavedVariables/IconCollector.lua")
    print("或者手动输入文件路径:")
    manual_path = input("文件路径: ").strip()
    if manual_path:
        found_file = manual_path
    else:
        sys.exit(1)

with open(found_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 解析Lua格式: ["itemId"] = { ["name"] = "xxx", ["icon"] = "xxx" }
items = {}
pattern = r'\[\s*(\d+)\s*\]\s*=\s*\{\s*\[\s*"name"\s*\]\s*=\s*"([^"]*)"\s*,\s*\[\s*"icon"\s*\]\s*=\s*"([^"]*)"\s*\}'
for match in re.finditer(pattern, content):
    item_id = int(match.group(1))
    name = match.group(2)
    icon_name = match.group(3)
    items[item_id] = (name, icon_name)

if not items:
    print("未找到扫描数据！请确认已在游戏中执行 /ic raid 扫描 和 /reloadui")
    sys.exit(1)

print(f"从 {found_file} 读取到 {len(items)} 个物品")

# 更新数据库
db = sqlite3.connect(DB_PATH)
c = db.cursor()

updated_items = 0
for item_id, (name, icon_name) in items.items():
    icon_url = f"https://render.worldofwarcraft.com/icons/56/{icon_name}.jpg"
    
    # 更新items表
    c.execute("SELECT name, icon_url FROM items WHERE item_id = ?", (item_id,))
    row = c.fetchone()
    if row:
        old_name = row[0] or ''
        if '未知' in old_name or old_name == '':
            c.execute("UPDATE items SET name = ?, icon_url = ? WHERE item_id = ?",
                     (name, icon_url, item_id))
            updated_items += 1
        elif row[1] != icon_url:
            c.execute("UPDATE items SET icon_url = ? WHERE item_id = ?",
                     (icon_url, item_id))
            updated_items += 1
    else:
        # items表没有记录则插入
        c.execute("INSERT INTO items (item_id, name, quality, item_level, icon_url, stats, slot) VALUES (?, ?, 'common', 0, ?, '{}', '')",
                 (item_id, name, icon_url))
        updated_items += 1

db.commit()

print(f"\n更新完成:")
print(f"  items表更新: {updated_items} 条")
print(f"  boss_loot影响: {len(items)} 个物品")
db.close()