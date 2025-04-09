from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.logic.wishlist_logic import (
    add_item_to_wishlist,
    remove_item_from_wishlist,
    remove_wishlist,
    move_item_from_wishlist_to_wardrobe,
    get_specific_item_from_wishlist,
    get_wishlist
)

router = APIRouter()

class WishlistItemRequest(BaseModel):
    title: str
    link: Optional[str]
    price: str
    store_name: Optional[str]
    thumbnail: Optional[str]
    country: Optional[str]
    

class WishlistItemDeleteRequest(BaseModel):
    item_id: str

class WishlistMoveRequest(BaseModel):
    item_id: str
    category: str


class getItemRequest(BaseModel):
    item_id: str
    
# ✅ הוספה ל־Wishlist
@router.post("/add-item")
def add_to_wishlist(
    result: WishlistItemRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        return add_item_to_wishlist(user_id, result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ❌ הסרה מ־Wishlist
@router.delete("/remove-item")
def remove_from_wishlist(
    data: WishlistItemDeleteRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        return remove_item_from_wishlist(user_id, data.item_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 🔁 העברה ל־Wardrobe
@router.post("/move-to-wardrobe")
def move_to_wardrobe(
    data: WishlistMoveRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        return move_item_from_wishlist_to_wardrobe(user_id, data.item_id, data.category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 🗑️ מחיקת Wishlist שלם
@router.delete("/delete-wishlist")
def delete_wishlist(
    user_id: str = Header(..., alias="user-id")
):
    try:
        return remove_wishlist(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/get-item-from-wishlist")
def get_specific_wishlist_item(
    req: getItemRequest,
    user: str = Header(..., alias="user-id")
):
    try:
        result = get_specific_item_from_wishlist(user, req.item_id)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.get("/get-wishlist")
def get_wishlist_endpoint(
    user_id: str = Header(..., alias="user-id")
):
    try:
        return get_wishlist(user_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))