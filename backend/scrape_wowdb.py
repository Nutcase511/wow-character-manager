import sqlite3
import requests
import json
import time
import random

def fetch_item_name_wowdb(item_id):
    """从WoWDB获取装备的中文名称"""
    # WoWDB提供API接口
    url = f"https://www.wowdb.com/api/item/{item_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            try:
                data = response.json()
                if 'name' in data and data['name']:
                    return data['name']
            except:
                # 如果不是JSON，尝试解析HTML
                content = response.text
                import re
                match = re.search(r'<title>([^|]+)\|', content)
                if match:
                    return match.group(1).strip()
    except Exception as e:
        print(f"Error fetching item {item_id} from WoWDB: {e}")
    
    return None

def fetch_item_name_wowhead_api(item_id):
    """使用WoWHead的API获取中文名称"""
    # WoWHead API格式
    url = f"https://api.wowhead.com/item={item_id}&json"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.wowhead.com/'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            # WoWHead返回的是JSONP格式
            if content.startswith('WH.ItemJson'):
                json_str = content[13:-1]  # 去掉WH.ItemJson( 和 )
                try:
                    data = json.loads(json_str)
                    if 'name' in data:
                        return data['name']
                except:
                    pass
    except Exception as e:
        print(f"Error fetching item {item_id} from WoWHead API: {e}")
    
    return None

def fetch_item_name_icy_veins(item_id):
    """从Icy Veins获取装备名称"""
    url = f"https://www.icy-veins.com/wow/item/{item_id}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text
            import re
            # 尝试多种模式
            match = re.search(r'<h1 class="heading-1">(.*?)</h1>', content)
            if match:
                return match.group(1).strip()
            match = re.search(r'<title>([^|]+)\|', content)
            if match:
                return match.group(1).strip()
    except Exception as e:
        print(f"Error fetching item {item_id} from Icy Veins: {e}")
    
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
        LIMIT 30
    ''')
    items = cursor.fetchall()
    
    print(f'Found {len(items)} items to fetch')
    
    success_count = 0
    fail_count = 0
    
    for item_id, english_name in items:
        print(f'Fetching item {item_id}: {english_name}')
        
        # 尝试多个数据源
        chinese_name = None
        
        # 先尝试WoWHead API
        if not chinese_name:
            chinese_name = fetch_item_name_wowhead_api(item_id)
        
        # 尝试WoWDB
        if not chinese_name:
            chinese_name = fetch_item_name_wowdb(item_id)
        
        # 尝试Icy Veins
        if not chinese_name:
            chinese_name = fetch_item_name_icy_veins(item_id)
        
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
        time.sleep(random.uniform(1, 2))
        
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
