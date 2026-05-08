import sqlite3

def fix_dungeon_data():
    conn = sqlite3.connect('wow_character_manager.db')
    cursor = conn.cursor()
    
    # 删除重复数据
    cursor.execute('''
        DELETE FROM dungeons 
        WHERE id NOT IN (
            SELECT MIN(id) FROM dungeons GROUP BY name, expansion
        )
    ''')
    conn.commit()
    print('Deleted duplicates')
    
    # 更新WotLK团本分类
    wl_raids = ['纳克萨玛斯', '永恒之眼', '黑曜石圣殿', '奥杜尔', '十字军试炼', '阿尔卡冯的宝库', '冰冠堡垒', '红玉圣殿']
    for raid in wl_raids:
        cursor.execute('UPDATE dungeons SET category = "raid" WHERE name = ? AND expansion = "wotlk"', (raid,))
    
    # 更新WotLK五人本分类
    wl_dungeons = ['灵魂洪炉', '岩石大厅', '古达克', '映像大厅', '闪电大厅', '紫罗兰堡', '魔枢', '达克萨隆要塞', '乌特加德城堡', '乌特加德之巅', '萨隆矿坑', '魔导师平台']
    for dungeon in wl_dungeons:
        cursor.execute('UPDATE dungeons SET category = "dungeon" WHERE name = ? AND expansion = "wotlk"', (dungeon,))
    
    # 更新TBC团本分类
    tbc_raids = ['玛瑟里顿的巢穴', '卡拉赞', '祖阿曼', '毒蛇神殿', '风暴要塞', '格鲁尔的巢穴', '黑暗神殿', '太阳井高地']
    for raid in tbc_raids:
        cursor.execute('UPDATE dungeons SET category = "raid" WHERE name = ? AND expansion = "tbc"', (raid,))
    
    # 更新TBC五人本分类
    tbc_dungeons = ['鲜血熔炉', '地狱火壁垒', '破碎大厅', '黑色沼泽', '幽暗沼泽', '塞泰克大厅', '暗影迷宫', '法力墓地', '旧希尔斯布莱德', '禁魔监狱']
    for dungeon in tbc_dungeons:
        cursor.execute('UPDATE dungeons SET category = "dungeon" WHERE name = ? AND expansion = "tbc"', (dungeon,))
    
    # 更新Classic团本分类
    classic_raids = ['纳克萨玛斯', '熔火之心', '奥妮克希亚的巢穴', '黑翼之巢', '安其拉废墟', '安其拉']
    for raid in classic_raids:
        cursor.execute('UPDATE dungeons SET category = "raid" WHERE name = ? AND expansion = "classic"', (raid,))
    
    # 更新Classic五人本分类
    classic_dungeons = ['沉没的神庙', '奥达曼', '影牙城堡', '哀嚎洞穴', '死亡矿井', '黑暗深渊', '怒焰裂谷', '剃刀沼泽', '暴风城监狱', '血色修道院', '剃刀高地', '诺莫瑞根', '厄运之槌', '祖尔法拉克', '黑石塔', '通灵学院', '斯坦索姆']
    for dungeon in classic_dungeons:
        cursor.execute('UPDATE dungeons SET category = "dungeon" WHERE name = ? AND expansion = "classic"', (dungeon,))
    
    conn.commit()
    
    # 统计
    cursor.execute('SELECT COUNT(*) FROM dungeons')
    print(f'Total dungeons after cleanup: {cursor.fetchone()[0]}')
    
    cursor.execute('SELECT expansion, category, COUNT(*) FROM dungeons GROUP BY expansion, category ORDER BY expansion, category')
    print('\nSummary:')
    for row in cursor.fetchall():
        print(f'{row[0]} - {row[1]}: {row[2]}')
    
    conn.close()

if __name__ == '__main__':
    fix_dungeon_data()
