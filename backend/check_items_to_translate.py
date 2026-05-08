import sqlite3

def contains_chinese(text):
    if not text:
        return False
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

conn = sqlite3.connect('wow_character_manager.db')
cursor = conn.cursor()

# 获取所有装备
cursor.execute('SELECT item_id, item_name FROM boss_loot WHERE item_id IS NOT NULL AND item_id > 0')
items = cursor.fetchall()

print(f"总共有 {len(items)} 条掉落记录")

# 统计需要翻译的装备
need_translate = []
already_chinese = []

for item_id, item_name in items:
    if item_name:
        if contains_chinese(item_name):
            already_chinese.append((item_id, item_name))
        else:
            need_translate.append((item_id, item_name))

print(f"已翻译: {len(already_chinese)}")
print(f"需要翻译: {len(need_translate)}")

# 显示需要翻译的前20个装备（按出现次数排序）
print("\n需要翻译的装备（出现次数最多的前20个）:")
cursor.execute('''
    SELECT item_id, item_name, COUNT(*) as count 
    FROM boss_loot 
    WHERE item_id IS NOT NULL AND item_id > 0 AND item_name NOT LIKE '%[\\u4e00-\\u9fff]%'
    GROUP BY item_id, item_name 
    ORDER BY count DESC 
    LIMIT 20
''')
top_items = cursor.fetchall()

for item_id, item_name, count in top_items:
    print(f"  {item_id}: {item_name} ({count}次)")

# 保存需要翻译的装备列表
with open('items_need_translate.txt', 'w', encoding='utf-8') as f:
    for item_id, item_name in need_translate:
        f.write(f"{item_id}|{item_name}\n")

print(f"\n已保存需要翻译的装备列表到 items_need_translate.txt")

conn.close()
