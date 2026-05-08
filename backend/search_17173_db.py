import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 访问17173数据库搜索页面
search_url = "https://tools.17173.com/wowdb/db/cata/search"
response = requests.get(search_url, headers=headers)
response.encoding = 'utf-8'

print("=== 17173数据库搜索页面 ===")
soup = BeautifulSoup(response.text, 'html.parser')

# 查找搜索表单
form = soup.find('form')
if form:
    print("找到搜索表单")
    inputs = form.find_all('input')
    for input_tag in inputs:
        print(f"Input: {input_tag.get('name', '')} - {input_tag.get('placeholder', '')}")

# 尝试搜索装备
print("\n=== 尝试搜索装备 ===")
search_data = {
    'q': '安卡哈护手',
    'search_type': 'item'
}
response = requests.post(search_url, data=search_data, headers=headers)
print(f"搜索状态: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    # 查找搜索结果
    results = soup.find_all('div', class_='list-item')
    if results:
        print(f"找到 {len(results)} 个结果")
        for result in results[:5]:
            link = result.find('a')
            if link:
                print(f"结果: {link.get_text(strip=True)} -> {link['href']}")
    else:
        # 尝试其他选择器
        links = soup.find_all('a', href=True)
        for link in links[:20]:
            href = link['href']
            text = link.get_text(strip=True)
            if '/item/' in href and text:
                print(f"找到装备链接: {text} -> {href}")
