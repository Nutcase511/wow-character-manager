import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_from_gamersky(search_keyword):
    """从游民星空搜索结果中提取装备名称"""
    url = f"https://so.gamersky.com/?s={search_keyword}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找搜索结果
            results = soup.find_all('h3', class_='news-title')
            for result in results[:5]:
                link = result.find('a')
                if link:
                    text = link.get_text(strip=True)
                    href = link['href']
                    print(f"游民星空: {text} -> {href}")
                    return text
    except Exception as e:
        print(f"游民星空提取失败: {e}")
    return None

def extract_from_sina(search_keyword):
    """从新浪游戏搜索结果中提取装备名称"""
    url = f"https://search.sina.com.cn/?q={search_keyword}"
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 查找搜索结果
            results = soup.find_all('h2')
            for result in results[:5]:
                link = result.find('a')
                if link:
                    text = link.get_text(strip=True)
                    href = link['href']
                    print(f"新浪游戏: {text} -> {href}")
                    return text
    except Exception as e:
        print(f"新浪游戏提取失败: {e}")
    return None

# 测试提取
test_items = ["安卡哈护手", "死亡之咬", "瓦兰奈尔", "影之哀伤"]

print("=== 测试装备名称提取 ===")
for item in test_items:
    print(f"\n搜索: {item}")
    result = extract_from_gamersky(item)
    if not result:
        result = extract_from_sina(item)
    print(f"提取结果: {result}")
