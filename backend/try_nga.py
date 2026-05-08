import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://bbs.nga.cn/'
}

# NGA的不同域名
nga_urls = [
    "https://bbs.nga.cn/",
    "https://wow.nga.cn/",
    "https://bbs.nga.cn/thread.php?fid=182",  # 魔兽世界综合讨论区
    "https://bbs.nga.cn/thread.php?fid=589",  # WLK怀旧服讨论区
]

print("=== 尝试访问NGA ===")

for url in nga_urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"{url}: 状态码 {response.status_code}")
        
        if response.status_code == 200:
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "无标题"
            print(f"  标题: {title[:50]}")
            
            # 查找搜索框
            search_box = soup.find('input', {'name': 'q', 'type': 'text'})
            if search_box:
                print(f"  找到搜索框")
            
            # 查找数据库相关链接
            links = soup.find_all('a', href=True)
            db_links = []
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                if any(keyword in href.lower() or keyword in text for keyword in ['db', '数据库', '装备', '物品', 'item']):
                    db_links.append((text, href))
            
            if db_links:
                print(f"  找到 {len(db_links)} 个数据库链接:")
                for text, href in db_links[:3]:
                    print(f"    {text} -> {href}")
                    
    except Exception as e:
        print(f"{url}: 访问失败 - {e}")

# 尝试搜索装备
print("\n=== 尝试在NGA搜索装备 ===")
search_keyword = "安卡哈护手"
search_url = f"https://bbs.nga.cn/search.php?keyword={search_keyword}&fid=182"

try:
    response = requests.get(search_url, headers=headers, timeout=15)
    print(f"NGA搜索: {search_url}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找搜索结果
        results = soup.find_all('a', href=True)
        found_items = []
        for link in results[:20]:
            text = link.get_text(strip=True)
            href = link['href']
            if text and len(text) > 3:
                found_items.append((text, href))
        
        if found_items:
            print(f"找到 {len(found_items)} 个结果:")
            for text, href in found_items[:5]:
                print(f"  {text} -> {href[:60]}")
                
except Exception as e:
    print(f"NGA搜索失败: {e}")
