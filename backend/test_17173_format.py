import requests

# 测试不同的URL格式
test_urls = [
    "https://wow.17173.com/item/35607.shtml",  # 安卡哈护手
    "https://wow.17173.com/item/39417.shtml",  # 死亡之咬
    "https://wow.17173.com/item-35607.html",
    "https://db.17173.com/wow/item/35607",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

for url in test_urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"{url}: status={response.status_code}")
        # 打印前500个字符看看页面结构
        if response.status_code == 200:
            content = response.text[:500]
            print(f"  Content preview: {content[:100]}...")
    except Exception as e:
        print(f"{url}: FAILED - {e}")
