from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from src.models.item_model import Item
from src.logic.wardrobe_logic import (
    convert_result_to_item,
    add_item_to_category,
    create_category,
    rename_category,
    delete_category,
    remove_wardrobe,
    remove_item_from_category
)

router = APIRouter()

class SerpApiResult(BaseModel):
    title: str
    link: Optional[str]
    price: str
    store_name: Optional[str]
    thumbnail: Optional[str]
    country: Optional[str]
    category_name: str

class CreateCategoryRequest(BaseModel):
    category_name: str

class RenameCategoryRequest(BaseModel):
    former_name: str
    new_name: str


class DeleteCategoryRequest(BaseModel):
    category_name: str

class DeleteItemFromCategoryRequest(BaseModel):
    item_id: str
    category_name: str
    
@router.post("/add-to-wardrobe")
def add_to_closet(
    result: SerpApiResult,
    user_id: str = Header(..., alias="user-id")
):
    try:
        item = convert_result_to_item(result.model_dump())
        category = result.category_name
        add_item_to_category(user_id, item, category)
        return {"message": f"Item added to category '{category}'", "id": str(item.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/remove-from-wardrobe")
def remove_from_closet(
    result: DeleteItemFromCategoryRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        item = Item.objects.get(id=result.item_id)
        category = result.category_name
        remove_item_from_category(user_id, item, category)
        return {"message": f"Item removed from category '{category}'", "id": str(item.id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/create-category")
def create_category_endpoint(
    req: CreateCategoryRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        create_category(user_id, req.category_name)
        return {"message": f"Category '{req.category_name}' created"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/rename-category")
def rename_category_endpoint(
    req: RenameCategoryRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        rename_category(user_id, req.former_name, req.new_name)
        return {"message": f"Category renamed from '{req.former_name}' to '{req.new_name}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class DeleteCategoryRequest(BaseModel):
    category_name: str

@router.delete("/delete-category")
def delete_category_endpoint(
    req: DeleteCategoryRequest,
    user_id: str = Header(..., alias="user-id")
):
    try:
        delete_category(user_id, req.category_name)
        return {"message": f"Category '{req.category_name}' deleted"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/remove-wardrobe")
def remove_wardrobe_endpoint(
    user_id: str = Header(..., alias="user-id")
):
    try:
        result = remove_wardrobe(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))