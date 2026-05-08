import sqlite3
from smart_translator import translate_item_name

def batch_translate():
    conn = sqlite3.connect('wow_character_manager.db')
    cursor = conn.cursor()
    
    # 获取所有英文装备名称
    cursor.execute('''
        SELECT DISTINCT item_name 
        FROM boss_loot 
        WHERE item_name NOT LIKE '%[\\u4e00-\\u9fff]%' 
        AND item_name != ''
    ''')
    english_items = [row[0] for row in cursor.fetchall()]
    
    print(f'Total English items to translate: {len(english_items)}')
    
    # 创建翻译映射
    translations = {}
    for item in english_items:
        chinese = translate_item_name(item)
        if chinese != item:
            translations[item] = chinese
    
    print(f'Successfully translated: {len(translations)} items')
    
    # 更新数据库
    updated_count = 0
    for english, chinese in translations.items():
        cursor.execute('''
            UPDATE boss_loot 
            SET item_name = ? 
            WHERE item_name = ?
        ''', (chinese, english))
        updated_count += cursor.rowcount
    
    conn.commit()
    print(f'Updated {updated_count} loot entries')
    
    # 更新items表
    cursor.execute('''
        SELECT DISTINCT name 
        FROM items 
        WHERE name NOT LIKE '%[\\u4e00-\\u9fff]%' 
        AND name != ''
    ''')
    english_item_names = [row[0] for row in cursor.fetchall()]
    
    item_updates = 0
    for name in english_item_names:
        chinese = translate_item_name(name)
        if chinese != name:
            cursor.execute('''
                UPDATE items 
                SET name = ? 
                WHERE name = ?
            ''', (chinese, name))
            item_updates += cursor.rowcount
    
    conn.commit()
    print(f'Updated {item_updates} items in items table')
    
    conn.close()

if __name__ == '__main__':
    batch_translate()
