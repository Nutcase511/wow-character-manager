import requests

def test_connection():
    urls = [
        "https://www.baidu.com",
        "https://wow.17173.com",
        "https://db.nga.cn"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"{url}: OK (status code: {response.status_code})")
        except Exception as e:
            print(f"{url}: FAILED - {e}")

if __name__ == '__main__':
    test_connection()
