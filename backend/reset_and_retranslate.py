import sqlite3

def contains_chinese(text):
    """检查字符串是否包含中文"""
    if not text:
        return False
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def reset_and_retranslate():
    conn = sqlite3.connect('wow_character_manager.db')
    cursor = conn.cursor()
    
    # 获取原始的英文装备名称（从之前保存的文件）
    try:
        with open('english_items.txt', 'r', encoding='utf-8') as f:
            original_names = set(f.read().splitlines())
    except:
        original_names = set()
        print("Could not read original names file")
    
    # 恢复所有装备名称为英文（如果在原始列表中）
    cursor.execute('SELECT DISTINCT item_name FROM boss_loot')
    all_names = [row[0] for row in cursor.fetchall()]
    
    print(f'Total distinct names: {len(all_names)}')
    
    # 统计当前状态
    chinese_count = 0
    mixed_count = 0
    english_count = 0
    
    for name in all_names:
        if contains_chinese(name):
            # 检查是否是混合的
            has_english = any(c.isascii() and c.isalpha() for c in name)
            if has_english:
                mixed_count += 1
            else:
                chinese_count += 1
        else:
            english_count += 1
    
    print(f'Current state:')
    print(f'  Pure Chinese: {chinese_count}')
    print(f'  Mixed (Chinese + English): {mixed_count}')
    print(f'  Pure English: {english_count}')
    
    # 恢复混合名称为原始英文
    if mixed_count > 0:
        print(f'\nRestoring {mixed_count} mixed names...')
        for name in all_names:
            if contains_chinese(name):
                has_english = any(c.isascii() and c.isalpha() for c in name)
                if has_english:
                    # 尝试从original_names中找到匹配的
                    found = False
                    for orig in original_names:
                        if orig.lower() in name.lower() or name.lower() in orig.lower():
                            cursor.execute('UPDATE boss_loot SET item_name = ? WHERE item_name = ?', (orig, name))
                            found = True
                            break
                    if not found:
                        # 尝试清理名称
                        cleaned = ''.join([c for c in name if not ('\u4e00' <= c <= '\u9fff')])
                        cleaned = cleaned.strip()
                        if cleaned:
                            cursor.execute('UPDATE boss_loot SET item_name = ? WHERE item_name = ?', (cleaned, name))
    
    conn.commit()
    print('Done!')
    
    conn.close()

if __name__ == '__main__':
    reset_and_retranslate()
