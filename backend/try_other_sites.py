import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 尝试其他游戏网站
sites = [
    {"name": "多玩游戏", "url": "https://wow.duowan.com/", "search_url": "https://wow.duowan.com/search.html?keyword="},
    {"name": "游民星空", "url": "https://www.gamersky.com/z/wow/", "search_url": "https://so.gamersky.com/?s="},
    {"name": "太平洋游戏网", "url": "https://wow.pcgames.com.cn/", "search_url": "https://wow.pcgames.com.cn/search/?keyword="},
    {"name": "新浪游戏", "url": "https://games.sina.com.cn/wow/", "search_url": "https://search.sina.com.cn/?q="},
]

print("=== 尝试访问其他游戏网站 ===")

for site in sites:
    print(f"\n--- {site['name']} ---")
    try:
        response = requests.get(site['url'], headers=headers, timeout=10)
        print(f"首页: {site['url']} - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "无标题"
            print(f"页面标题: {title}")
            
            # 查找数据库/装备相关链接
            links = soup.find_all('a', href=True)
            db_links = []
            for link in links:
                href = link['href']
                text = link.get_text(strip=True)
                if any(keyword in href.lower() or keyword in text for keyword in ['item', '装备', '数据库', 'db', '物品']):
                    db_links.append((text, href))
            
            if db_links:
                print(f"找到 {len(db_links)} 个数据库相关链接:")
                for text, href in db_links[:3]:
                    print(f"  {text} -> {href}")
    except Exception as e:
        print(f"{site['name']} 访问失败: {e}")

# 尝试搜索装备
print("\n=== 尝试搜索装备 ===")
search_keyword = "安卡哈护手"

for site in sites:
    search_url = site['search_url'] + search_keyword
    print(f"\n{site['name']} 搜索: {search_url}")
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找搜索结果
            results = soup.find_all('a', href=True)
            found_items = []
            for link in results[:10]:
                href = link['href']
                text = link.get_text(strip=True)
                if text and ('护手' in text or '装备' in text or '/item/' in href):
                    found_items.append((text, href))
            
            if found_items:
                print(f"找到 {len(found_items)} 个结果:")
                for text, href in found_items[:3]:
                    print(f"  {text} -> {href}")
    except Exception as e:
        print(f"搜索失败: {e}")
