import sqlite3
import requests
import json
import time
import random

def fetch_item_name(item_id):
    """从WoWHead获取装备的中文名称"""
    url = f"https://www.wowhead.com/item={item_id}&xml"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            # 提取中文名称
            if '<name lang="zhCN">' in content:
                start = content.find('<name lang="zhCN">') + len('<name lang="zhCN">')
                end = content.find('</name>', start)
                return content[start:end].strip()
            elif '<name>' in content:
                start = content.find('<name>') + len('<name>')
                end = content.find('</name>', start)
                return content[start:end].strip()
    except Exception as e:
        print(f"Error fetching item {item_id}: {e}")
    
    return None

def batch_fetch_and_update():
    conn = sqlite3.connect('wow_character_manager.db')
    cursor = conn.cursor()
    
    # 获取所有有item_id但名称是英文的装备
    cursor.execute('''
        SELECT DISTINCT item_id, item_name 
        FROM boss_loot 
        WHERE item_id IS NOT NULL 
        AND item_id > 0 
        AND item_name NOT LIKE '%[\\u4e00-\\u9fff]%' 
        AND item_name != ''
        LIMIT 100
    ''')
    items = cursor.fetchall()
    
    print(f'Found {len(items)} items to fetch')
    
    success_count = 0
    fail_count = 0
    
    for item_id, english_name in items:
        print(f'Fetching item {item_id}: {english_name}')
        
        chinese_name = fetch_item_name(item_id)
        
        if chinese_name and chinese_name != english_name:
            print(f'  -> {chinese_name}')
            # 更新boss_loot表
            cursor.execute('''
                UPDATE boss_loot 
                SET item_name = ? 
                WHERE item_id = ?
            ''', (chinese_name, item_id))
            # 更新items表
            cursor.execute('''
                UPDATE items 
                SET name = ? 
                WHERE item_id = ?
            ''', (chinese_name, item_id))
            success_count += 1
        else:
            print(f'  -> Failed to fetch')
            fail_count += 1
        
        # 随机延迟，避免被封禁
        time.sleep(random.uniform(0.5, 2.0))
        
        # 每10个提交一次
        if success_count % 10 == 0:
            conn.commit()
            print(f'Committed {success_count} translations')
    
    conn.commit()
    print(f'\nTotal: {len(items)} items')
    print(f'Success: {success_count}')
    print(f'Failed: {fail_count}')
    
    conn.close()

if __name__ == '__main__':
    batch_fetch_and_update()
