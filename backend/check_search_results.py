import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 测试游民星空搜索
url = "https://so.gamersky.com/?s=安卡哈护手"
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

print("=== 游民星空搜索结果页面 ===")
print(f"状态码: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 打印页面结构
    print("\n页面标题:", soup.title.string if soup.title else "无标题")
    
    # 查找所有可能的结果容器
    print("\n=== 查找结果容器 ===")
    
    # 尝试不同的标签
    containers = ['div', 'article', 'ul', 'li']
    for container in containers:
        elements = soup.find_all(container)
        print(f"找到 {len(container)} 个 {container} 标签")
    
    # 查找所有链接
    links = soup.find_all('a', href=True)
    print(f"\n找到 {len(links)} 个链接")
    
    # 打印前20个链接
    print("\n前20个链接:")
    for link in links[:20]:
        text = link.get_text(strip=True)
        href = link['href']
        if text:
            print(f"  {text[:50]} -> {href[:50]}")

# 测试新浪搜索
print("\n\n=== 新浪搜索结果页面 ===")
url = "https://search.sina.com.cn/?q=安卡哈护手"
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    print("\n页面标题:", soup.title.string if soup.title else "无标题")
    
    # 查找所有链接
    links = soup.find_all('a', href=True)
    print(f"\n找到 {len(links)} 个链接")
    
    # 打印前20个链接
    print("\n前20个链接:")
    for link in links[:20]:
        text = link.get_text(strip=True)
        href = link['href']
        if text and len(text) > 5:
            print(f"  {text[:50]} -> {href[:50]}")
