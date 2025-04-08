from fastapi import APIRouter
from src.logic.web_scraping_logic.vogue_scraping_logic import scrape_vogue_articles
from src.logic.web_scraping_logic.harpersbazaar_scraping_logic import scrape_harpersbazaar_articles

router = APIRouter()

@router.get("/scrape/harpersbazaar")
def get_harpersbazaar():
    result = scrape_harpersbazaar_articles()
    return result

@router.get("/scrape/vogue")
def get_vogue():
    result = scrape_vogue_articles()
    return result