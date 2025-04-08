from fastapi import APIRouter, Query
from src.logic.serpai_logic import search_google_shopping

router = APIRouter()

@router.get("/shopping")
def shopping_search(q: str = Query(..., description="Search query, e.g. 'white midi skirt'")):
    """
    GET /shopping?q=white+midi+skirt

    Performs a Google Shopping query via SerpAPI and returns a JSON response
    with product information.
    """
    results = search_google_shopping(q)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }
