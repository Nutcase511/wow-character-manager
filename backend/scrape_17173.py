import sqlite3
import requests
import re
import time
import random

def fetch_item_name_17173(item_id):
    """从17173获取装备的中文名称"""
    url = f"https://wow.17173.com/item/{item_id}.shtml"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://wow.17173.com/'
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            content = response.text
            # 提取装备名称 - 尝试多种模式
            # 模式1: <h1 class="item-name">装备名称</h1>
            match = re.search(r'<h1[^>]*class="item-name"[^>]*>([^<]+)</h1>', content)
            if match:
                return match.group(1).strip()
            # 模式2: <title>装备名称 | 魔兽世界数据库...</title>
            match = re.search(r'<title>([^|]+)\s*\|\s*魔兽世界', content)
            if match:
                return match.group(1).strip()
            # 模式3: <div class="item-detail-header"><h2>装备名称</h2>
            match = re.search(r'<div class="item-detail-header"><h2>([^<]+)</h2>', content)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}")
    
    return None

def batch_fetch():
    conn = sqlite3.connect('wow_character_manager.db')
    cursor = conn.cursor()
    
    # 获取需要翻译的装备（有item_id且名称是英文）
    cursor.execute('''
        SELECT DISTINCT item_id, item_name 
        FROM boss_loot 
        WHERE item_id IS NOT NULL 
        AND item_id > 0 
        AND item_name NOT LIKE '%[\\u4e00-\\u9fff]%' 
        AND item_name != ''
        ORDER BY item_id
        LIMIT 20
    ''')
    items = cursor.fetchall()
    
    print(f'Found {len(items)} items to fetch')
    
    success_count = 0
    fail_count = 0
    
    for item_id, english_name in items:
        print(f'Fetching item {item_id}: {english_name}')
        
        chinese_name = fetch_item_name_17173(item_id)
        
        if chinese_name and chinese_name != english_name:
            print(f'  -> {chinese_name}')
            # 更新boss_loot表
            cursor.execute('UPDATE boss_loot SET item_name = ? WHERE item_id = ?', (chinese_name, item_id))
            # 更新items表
            cursor.execute('UPDATE items SET name = ? WHERE item_id = ?', (chinese_name, item_id))
            success_count += 1
        else:
            print(f'  -> Failed to fetch')
            fail_count += 1
        
        # 随机延迟
        time.sleep(random.uniform(0.5, 1.5))
        
        # 每5个提交一次
        if success_count % 5 == 0 and success_count > 0:
            conn.commit()
            print(f'Committed {success_count} translations')
    
    conn.commit()
    print(f'\nTotal: {len(items)} items')
    print(f'Success: {success_count}')
    print(f'Failed: {fail_count}')
    
    conn.close()

if __name__ == '__main__':
    batch_fetch()
