# serpai_controller.py
from fastapi import APIRouter, Query, Depends
from src.logic.serpai_logic import search_google_shopping
from src.utils.auth_utils import get_current_user
from src.models.user_model import User

router = APIRouter()

@router.get("/shopping")
def shopping_search(
    q: str = Query(..., description="Search query, e.g. 'white midi skirt'"),
    user: User = Depends(get_current_user)
):
    results = search_google_shopping(q, user)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }
