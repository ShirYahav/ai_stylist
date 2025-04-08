import requests
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY") 

TRUSTED_STORES = [
    "nike.com", "amazon.com", "zara.com", "adidas.com", "hm.com",
    "asos.com", "shein.com", "castro.com", "terminalx.com", "ksp.co.il",
    "next.co.uk", "ebay.com", "bestbuy.com", "walmart.com", "aliexpress.com",
    "ebags.com", "sneakersnstuff.com", "footlocker.com", "jd.com","renuar.com",
    "gap.com", "oldnavy.com", "target.com", "uniqlo.com", "mango.com",
]

def calculate_score(item, query):
    title = item.get("title", "") or ""
    link = item.get("link", "") or ""
    store = item.get("store_name", "") or ""

    similarity = SequenceMatcher(None, query.lower(), title.lower()).ratio()
    trusted_score = 0
    for store_url in TRUSTED_STORES:
        if store_url.lower() in (store or "").lower() or store_url.lower() in (link or "").lower():
            trusted_score = 1
            break

    score = (similarity * 2.0) + (trusted_score * 2.0)
    return score

def search_google_shopping(query: str):
    """
    Calls SerpAPI to perform Google Shopping search in multiple countries for the given query.
    Returns a sorted list of up to 50 relevant items.
    """

    countries = ['us', 'il', 'uk','ca','cn','au']
    results_list = []

    for gl_code in countries:
        params = {
            "engine": "google_shopping",
            "q": query,
            "hl": "en",
            "gl": gl_code,
            "api_key": SERPAPI_KEY
        }

        try:
            response = requests.get("https://serpapi.com/search.json", params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"שגיאה עבור המדינה {gl_code}: {e}")
            continue

        shopping_results = data.get("shopping_results", [])

        for item in shopping_results:
            title = item.get("title")
            link = item.get("link") or item.get("product_link")
            extracted_price = item.get("extracted_price")
            source = item.get("source")
            product_id = item.get("product_id")
            thumbnail = item.get("thumbnail")

            result_info = {
                "title": title,
                "link": link,
                "price": extracted_price,
                "store_name": source,
                "product_id": product_id,
                "thumbnail": thumbnail,
                "country": gl_code
            }

            result_info["score"] = calculate_score(result_info, query)
            results_list.append(result_info)

    sorted_results = sorted(results_list, key=lambda x: x["score"], reverse=True)[:50]

    return sorted_results