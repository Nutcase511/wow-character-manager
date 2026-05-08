import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://bbs.nga.cn/',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# 尝试NGA搜索
search_keyword = "安卡哈护手"
search_url = f"https://bbs.nga.cn/search.php?keyword={search_keyword}&fid=182"

try:
    response = requests.get(search_url, headers=headers, timeout=15)
    print(f"NGA搜索: {search_url}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        # 尝试不同编码
        encodings = ['utf-8', 'gbk', 'gb2312']
        content = None
        
        for encoding in encodings:
            try:
                response.encoding = encoding
                content = response.text
                # 检查是否包含有效内容
                if '安卡哈' in content or '护手' in content:
                    print(f"成功解码，编码: {encoding}")
                    break
            except:
                continue
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            
            # 查找搜索结果
            results = soup.find_all('a', href=True)
            found_items = []
            for link in results[:30]:
                text = link.get_text(strip=True)
                href = link['href']
                if text and len(text) > 3:
                    found_items.append((text, href))
            
            if found_items:
                print(f"找到 {len(found_items)} 个结果:")
                for text, href in found_items[:10]:
                    print(f"  {text}")
                
                # 查找包含"装备"或"护手"的结果
                print("\n包含装备名称的结果:")
                for text, href in found_items:
                    if '护手' in text or '装备' in text or '物品' in text:
                        print(f"  {text} -> {href[:60]}")

except Exception as e:
    print(f"NGA搜索失败: {e}")
    import traceback
    traceback.print_exc()
