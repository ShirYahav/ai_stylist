from fastapi import APIRouter, Query, Depends, UploadFile, File
from src.logic.image_captioning import extract_query_from_image
from src.logic.serpai_logic import search_google_shopping
from src.utils.auth_utils import get_current_user_optional  
from src.models.user_model import User
from typing import Optional

router = APIRouter()

@router.get("/shopping")
def shopping_search(
    q: str = Query(..., description="Search query, e.g. 'white midi skirt'"),
    user: Optional[User] = Depends(get_current_user_optional)  
):
    results = search_google_shopping(q, user)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }

@router.post("/shopping/image")
async def shopping_image_search(
    image: UploadFile = File(...),
    user: Optional[User] = Depends(get_current_user_optional)  
):
    image_bytes = await image.read()
    
    query = extract_query_from_image(image_bytes)
    
    results = search_google_shopping(query, user)
    
    return {
        "query": query,
        "count": len(results),
        "results": results
    }