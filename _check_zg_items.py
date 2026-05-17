"""检查经典ZG物品ID在items表中的状态"""
import sqlite3

DB_PATH = r'c:\wow后台管理\wow-character-manager\backend\wow_character_manager.db'

# 从Icy-Veins抓到的ZG物品ID（部分）
zg_item_ids = [
    # 小怪掉落
    20263, 19908, 20261, 20259, 20258, 19921,
    # 主手武器
    19968, 19964, 19965, 19867, 19864, 19865, 19903, 19896, 19890,
    # 单手武器
    19961, 19901, 19852, 19859,
    # 双手武器
    19962, 19963, 19946, 19900, 19874, 19918, 19884, 19944, 19909, 19854,
    # 远程
    19993, 19967, 19853, 20038, 19927, 19861,
    # 副手/盾牌
    19922, 19915, 19862, 19910, 19891, 19866,
    # 项链/披风
    19923, 19871, 19885, 19876, 19856, 22711,
]

db = sqlite3.connect(DB_PATH)
c = db.cursor()

exist = []
missing = []
for item_id in zg_item_ids:
    c.execute('SELECT item_id, name, icon_url FROM items WHERE item_id = ?', (item_id,))
    row = c.fetchone()
    if row:
        exist.append((row[0], row[1], row[2]))
    else:
        missing.append(item_id)

print(f'总ZG物品: {len(zg_item_ids)}')
print(f'items表已存在: {len(exist)}')
print(f'items表缺失: {len(missing)}')

if exist:
    print(f'\n=== 已存在的物品({len(exist)}个) ===')
    for e in exist:
        icon_short = e[2][:50] if e[2] and len(e[2]) > 50 else e[2]
        print(f'  ID={e[0]}, {e[1]}, icon={icon_short}')

if missing:
    print(f'\n=== 缺失的物品({len(missing)}个) ===')
    print(f'  ID列表: {missing}')

db.close()