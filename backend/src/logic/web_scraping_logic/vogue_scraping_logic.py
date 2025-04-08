import time
from bs4 import BeautifulSoup
from src.utils.web_scraping_utils import get_page_content, build_absolute_url

def scrape_vogue_main():
    url = "https://www.vogue.com/fashion"
    page_content = get_page_content(url)
    if page_content is None:
        return {"error": "Failed to retrieve Vogue Fashion page."}
    
    soup = BeautifulSoup(page_content, 'html.parser')
    articles = []

    anchors = soup.select('a.SummaryItemHedLink-civMjp')
    
    for anchor in anchors:
        h3 = anchor.find("h3", attrs={"data-testid": "SummaryItemHed"})
        title = h3.get_text(strip=True) if h3 else anchor.get_text(strip=True)
        
        href = anchor.get("href")
        full_link = build_absolute_url(url, href) if href else "No Link Found"
        
        if full_link and full_link != "No Link Found":
            articles.append({
                "title": title,
                "link": full_link
            })
    return articles

def scrape_vogue_article(article_url: str):
    content = get_page_content(article_url)
    if content is None:
        return {
            "url": article_url,
            "paragraphs": [],
            "main_image": None,
            "error": "Failed to retrieve article."
        }
    
    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find("div", class_="article__content-body")
    if not main_content:
        main_content = soup.find("main") or soup

    paragraphs = []
    for p in main_content.find_all("p"):
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)

    main_image = None
    for img in main_content.find_all("img"):
        img_src = img.get("src") or img.get("data-src")
        if not img_src:
            continue
        
        lower_src = img_src.lower()
        if any(keyword in lower_src for keyword in ["svg", "icon", "logo"]):
            continue
        main_image = build_absolute_url(article_url, img_src)
        break  

    return {
        "url": article_url,
        "paragraphs": paragraphs,
        "main_image": main_image
    }

def scrape_vogue_articles():
    articles_list = scrape_vogue_main()
    results = []
    
    max_articles = 5
    count = 0

    for article in articles_list:
        if count >= max_articles:
            break
        link = article.get("link")
        title = article.get("title")
        if not link:
            continue
        
        time.sleep(1)
        
        content_data = scrape_vogue_article(link)
        combined_data = {
            "title": title,
            "link": link,
            "content_paragraphs": content_data.get("paragraphs", []),
            "main_image": content_data.get("main_image")
        }
        results.append(combined_data)
        count += 1

    return results
