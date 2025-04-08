import requests
from urllib.parse import urljoin

def get_page_content(url: str):
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; MyScraper/1.0)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Error fetching {url}: Status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception while requesting {url}: {e}")
        return None

def build_absolute_url(base_url: str, link: str) -> str:
    return urljoin(base_url, link)
