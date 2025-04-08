from bs4 import BeautifulSoup
from src.utils.web_scraping_utils import build_absolute_url, get_page_content
import time

def scrape_harpersbazaar():
    url = "https://www.harpersbazaar.com/fashion/"
    page_content = get_page_content(url)
    
    if page_content is None:
        return {"error": "Failed to retrieve page."}
    
    soup = BeautifulSoup(page_content, "html.parser")
    anchors = soup.find_all("a", attrs={"data-theme-key": "custom-item"})

    articles = []
    for anchor in anchors:
        title = anchor.get("data-vars-ga-call-to-action", "").strip()
        if not title:
            title = anchor.get_text(strip=True)
        
        outbound_link = anchor.get("data-vars-ga-outbound-link")
        href_link = anchor.get("href")
        final_link = outbound_link if outbound_link else href_link
        full_link = build_absolute_url(url, final_link) if final_link else "No Link Found"
        
        articles.append({
            "title": title,
            "link": full_link,
        })

    return articles

def scrape_article_page(article_url: str):

    page_content = get_page_content(article_url)
    if page_content is None:
        return {"error": f"Could not retrieve article: {article_url}"}
    
    soup = BeautifulSoup(page_content, "html.parser")
    
    paragraphs = []
    
    main_content = soup.find("div", class_="body-content")
    if main_content:
        p_tags = main_content.find_all("p")
    else:
        p_tags = soup.find_all("p")
    
    for p in p_tags:
        text = p.get_text(strip=True)
        if text:
            paragraphs.append(text)
    

    main_image = None
    if main_content:
        img_tags = main_content.find_all("img")
    else:
        img_tags = soup.find_all("img")
    
    for img in img_tags:
        src_attr = img.get("src") or img.get("data-src")
        if not src_attr:
            continue
        
        lower_src = src_attr.lower()
        if any(substr in lower_src for substr in ["svg", "icon", "logo"]):
            continue

        main_image = build_absolute_url(article_url, src_attr)
        break  

    return {
        "url": article_url,
        "paragraphs": paragraphs,
        "main_image": main_image  
    }

def scrape_harpersbazaar_articles():

    articles_list = scrape_harpersbazaar()
    
    max_articles = 5
    combined_results = []
    count = 0

    for article in articles_list:
        if count >= max_articles:
            break
        link = article.get("link")
        if not link or link == "No Link Found":
            continue
        
        time.sleep(1) 
        
        content_data = scrape_article_page(link)
        combined_data = {
            "title": article.get("title"),
            "link": link,
            "content_paragraphs": content_data.get("paragraphs", []),
            "main_image": content_data.get("main_image")
        }
        combined_results.append(combined_data)
        count += 1

    return combined_results