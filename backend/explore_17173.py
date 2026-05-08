import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 先访问17173魔兽世界首页，看看装备数据库入口
url = "https://wow.17173.com/"
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

print("=== 17173 WoW首页内容 ===")
soup = BeautifulSoup(response.text, 'html.parser')

# 查找数据库入口链接
links = soup.find_all('a', href=True)
for link in links[:30]:
    href = link['href']
    text = link.get_text(strip=True)
    if '数据库' in text or 'item' in href.lower() or '装备' in text:
        print(f"Found link: {text} -> {href}")

# 尝试搜索一个已知装备
print("\n=== 搜索装备 ===")
search_url = "https://wow.17173.com/search.html?keyword=安卡哈护手"
response = requests.get(search_url, headers=headers)
print(f"Search status: {response.status_code}")
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    results = soup.find_all('a', href=True)
    for result in results[:10]:
        href = result['href']
        text = result.get_text(strip=True)
        if 'item' in href.lower() or '装备' in text:
            print(f"Result: {text} -> {href}")
