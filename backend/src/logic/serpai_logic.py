import requests
import os
from dotenv import load_dotenv
from difflib import SequenceMatcher
from src.models.user_model import User
import re

load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

STOPWORDS = {
    "a","an","the","in","on","and","of","with","to","for",
    "solid","cotton","weave","down", "-"
}

TRUSTED_STORES = [
    "nike.com", "amazon.com", "zara.com", "adidas.com", "hm.com",
    "asos.com", "shein.com", "castro.com", "terminalx.com", "ksp.co.il",
    "next.co.uk", "ebay.com", "bestbuy.com", "walmart.com", "aliexpress.com",
    "ebags.com", "sneakersnstuff.com", "footlocker.com", "jd.com", "renuar.com",
    "gap.com", "oldnavy.com", "target.com", "uniqlo.com", "mango.com", "ralphlauren.com"
]

country_to_currency = {
    "United States": ("USD", "$"),
    "Israel": ("ILS", "₪"),
    "United Kingdom": ("GBP", "£"),
    "Canada": ("CAD", "C$"),
    "China": ("CNY", "¥"),
    "Australia": ("AUD", "A$"),
    "Germany": ("EUR", "€"),
    "France": ("EUR", "€"),
    "Italy": ("EUR", "€"),
    "Spain": ("EUR", "€"),
    "Netherlands": ("EUR", "€"),
    "Japan": ("JPY", "¥"),
    "India": ("INR", "₹"),
}

def clean_query(query: str) -> str:
    tokens = re.findall(r"\w+", query)
    tokens = [t for t in tokens if t.lower() not in STOPWORDS]
    return " ".join(tokens)

def get_currency_info_by_country(country_name):
    return country_to_currency.get(country_name, ("USD", "$"))

def convert_price(amount: float, from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return round(amount, 2)
    try:
        url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
        response = requests.get(url)
        response.raise_for_status()
        return round(response.json().get("result", amount), 2)
    except:
        return round(amount, 2)

def detect_currency_code(price_str: str) -> str:
    if "₪" in price_str:
        return "ILS"
    elif "£" in price_str:
        return "GBP"
    elif "€" in price_str:
        return "EUR"
    elif "¥" in price_str:
        return "CNY"
    elif "₹" in price_str:
        return "INR"
    elif "C$" in price_str:
        return "CAD"
    elif "A$" in price_str:
        return "AUD"
    else:
        return "USD"

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

    score = (similarity * 3) + (trusted_score * 1.5)
    return score

def search_google_shopping(query: str, user: User = None): 
    countries = ['uk']
    results_list = []

    if user and user.country:
        to_currency, currency_symbol = get_currency_info_by_country(user.country)
    else:
        to_currency, currency_symbol = "USD", "$"  

    for gl_code in countries:
        params = {
            "engine": "google_shopping",
            "q": clean_query(query),
            "hl": "en",
            "gl": gl_code,
            "api_key": SERPAPI_KEY
        }

        try:
            response = requests.get("https://serpapi.com/search.json", params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"error for country {gl_code}: {e}")
            continue

        shopping_results = data.get("shopping_results", [])

        for item in shopping_results:
            title = item.get("title")
            link = item.get("link") or item.get("product_link")
            price_str = item.get("price", "")
            extracted_price = item.get("extracted_price")
            source = item.get("source")
            product_id = item.get("product_id")
            thumbnail = item.get("thumbnail")

            if extracted_price:
                from_currency = detect_currency_code(price_str)
                converted_price = convert_price(extracted_price, from_currency, to_currency)
                formatted_price = f"{converted_price}{currency_symbol}"
            else:
                formatted_price = "N/A"

            result_info = {
                "title": title,
                "link": link,
                "price": formatted_price,
                "store_name": source,
                "product_id": product_id,
                "thumbnail": thumbnail,
                "country": gl_code
            }

            result_info["score"] = calculate_score(result_info, query)
            results_list.append(result_info)

    sorted_results = sorted(results_list, key=lambda x: x["score"], reverse=True)[:5]
    return sorted_results