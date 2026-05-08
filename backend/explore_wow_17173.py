import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 访问17173魔兽世界首页
url = "https://wow.17173.com/"
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

print("=== 17173 WoW首页 ===")
soup = BeautifulSoup(response.text, 'html.parser')

# 查找所有链接
all_links = soup.find_all('a', href=True)

print("\n=== 找到的链接 (包含item或数据库的) ===")
found_links = []
for link in all_links:
    href = link['href']
    text = link.get_text(strip=True)
    # 过滤包含关键词的链接
    if any(keyword in href.lower() or keyword in text for keyword in ['item', '装备', '数据库', 'db']):
        found_links.append((text, href))
        print(f"{text} -> {href}")

# 尝试访问可能的数据库页面
print("\n=== 尝试访问找到的链接 ===")
for text, href in found_links[:5]:
    try:
        # 处理相对路径
        if href.startswith('/'):
            full_url = "https://wow.17173.com" + href
        else:
            full_url = href
            
        response = requests.get(full_url, headers=headers, timeout=10)
        print(f"{text}: {full_url} - 状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查页面是否包含装备相关内容
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "无标题"
            print(f"  页面标题: {title[:50]}...")
    except Exception as e:
        print(f"{text}: {href} - 访问失败: {e}")
