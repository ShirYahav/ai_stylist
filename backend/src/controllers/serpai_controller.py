# serpai_controller.py
from fastapi import APIRouter, Query, Depends
from src.logic.serpai_logic import search_google_shopping
from src.utils.auth_utils import get_current_user_optional  
from src.models.user_model import User
from typing import Optional

router = APIRouter()

@router.get("/shopping")
def shopping_search(
    q: str = Query(..., description="Search query, e.g. 'white midi skirt'"),
    user: Optional[User] = Depends(get_current_user_optional)  # 👈 Optional
):
    results = search_google_shopping(q, user)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }