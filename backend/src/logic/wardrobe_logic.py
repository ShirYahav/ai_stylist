from bson import ObjectId
from mongoengine.errors import DoesNotExist
from src.models.item_model import EmbeddedItem, Item
from src.models.wardrobe_model import Wardrobe
from typing import Optional
from src.models.wardrobe_model import CategoryData

from mongoengine import DoesNotExist

def detect_gender(title: str):
    title = title.lower()
    if "men" in title or "man" in title:
        return "male"
    elif "women" in title or "woman" in title:
        return "female"
    return None


def extract_colors(title: str):
    colors = ["white", "black", "blue", "red", "green", "yellow", "gray", "brown", "pink", "purple", "orange"]
    return [color for color in colors if color in title.lower()]



def detect_type(title: str) -> Optional[str]:
    types = [
        "t-shirt", "shirt", "button-up", "tank top", "hoodie", "sweater",
        "dress", "blouse", "jacket", "coat", "jeans", "shorts", "skirt"
    ]
    for t in types:
        if t in title:
            return t
    return "Unknown"

    
def detect_material(title: str) -> Optional[str]:
    materials = ["cotton", "polyester", "linen", "silk", "denim", "leather", "wool", "nylon", "viscose"]
    for material in materials:
        if material in title:
            return material
    return None


def convert_result_to_item(result: dict) -> Item:
    title = result.get("title", "").lower()
    existing_item = Item.objects(image_url=result.get("thumbnail")).first()
    if existing_item:
        return existing_item

    item = Item(
        type=detect_type(title),
        gender=detect_gender(title),
        price=result.get("price"),
        brand=result.get("store_name", "Unknown"),
        color=extract_colors(title),
        material=detect_material(title), 
        image_url=result.get("thumbnail")
    )
    item.save()
    return item


def create_category(user_id: str, category_name: str):
    try:
        wardrobe = Wardrobe.objects.get(user_id=user_id)
    except DoesNotExist:
        wardrobe = Wardrobe(user_id=user_id, categories={})

    # בדיקה אם קיימת כבר קטגוריה (case insensitive)
    if category_name.lower() in (name.lower() for name in wardrobe.categories.keys()):
        raise ValueError(f"Category '{category_name}' already exists.")

    # יצירת קטגוריה חדשה עם אובייקט מסוג CategoryData
    wardrobe.categories[category_name] = CategoryData(items=[], count=0)
    wardrobe.save()
    return wardrobe



def rename_category(user_id: str, former_name: str, new_name: str):
    wardrobe = Wardrobe.objects.get(user_id=user_id)

    lower_categories = {k.lower(): k for k in wardrobe.categories.keys()}

    if former_name.lower() not in lower_categories:
        raise ValueError(f"Category '{former_name}' does not exist.")
    if new_name.lower() in lower_categories:
        raise ValueError(f"Category '{new_name}' already exists.")

    real_former_name = lower_categories[former_name.lower()]
    wardrobe.categories[new_name] = wardrobe.categories.pop(real_former_name)
    wardrobe.save()
    return wardrobe


def delete_category(user_id: str, category_name: str):
    wardrobe = Wardrobe.objects.get(user_id=user_id)

    lower_categories = {k.lower(): k for k in wardrobe.categories.keys()}

    if category_name.lower() not in lower_categories:
        raise ValueError(f"Category '{category_name}' does not exist.")
    
    for embedded in wardrobe.categories[category_name]:
        item = Item.objects(id=embedded.item_id).first()
        if item:
            item.update(dec__usage_count=1)
            wardrobe.wardrobeCount -=1
            wardrobe.save()
            item.reload()
            if item.usage_count <= 0:
                item.delete()

    real_name = lower_categories[category_name.lower()]
    del wardrobe.categories[real_name]
    wardrobe.save()
    return wardrobe

def add_item_to_category(user_id: str, item: Item, category: str):
    try:
        wardrobe = Wardrobe.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError(f"Wardrobe for user_id '{user_id}' does not exist.")

    if category not in wardrobe.categories:
        raise ValueError(f"Category '{category}' does not exist in user's wardrobe.")

    category_data = wardrobe.categories[category]

    # בדיקה אם הפריט כבר קיים בקטגוריה
    for embedded in category_data.items:
        if embedded.image_url == item.image_url:
            raise ValueError("Item is already in the wardrobe category.")

    # בדיקה אם הפריט קיים ב-wishlist
    from src.models.wishlist_model import Wishlist
    wishlist = Wishlist.objects(user_id=user_id).first()
    if wishlist:
        for embedded in wishlist.items:
            if embedded.image_url == item.image_url:
                raise ValueError("Item exists in wishlist and cannot be added to wardrobe.")

    # שמירת הפריט למסד
    if not item.id:
        item.usage_count = 1
        item.save()
    else:
        item.update(inc__usage_count=1)

    # הוספת הפריט לקטגוריה
    embedded = EmbeddedItem.from_item(item)
    category_data.items.append(embedded)
    category_data.count += 1

    wardrobe.wardrobeCount += 1
    wardrobe.save()

    return wardrobe



def remove_item_from_category(user_id: str, item: Item, category: str):
    from src.models.wishlist_model import Wishlist  # אם צריך

    try:
        wardrobe = Wardrobe.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError("Wardrobe not found.")

    if category not in wardrobe.categories:
        raise ValueError("Category does not exist.")

    category_data = wardrobe.categories[category]
    original_count = len(category_data.items)

    # מסנן החוצה את הפריט לפי image_url
    category_data.items = [
        emb for emb in category_data.items
        if emb.image_url != item.image_url
    ]

    # אם שום דבר לא השתנה – הפריט לא היה שם בכלל
    if len(category_data.items) == original_count:
        raise ValueError("Item not found in category.")

    # עדכון המונים
    category_data.count -= 1
    wardrobe.wardrobeCount -= 1
    wardrobe.save()

    # עדכון מונה שימוש של הפריט
    item.update(dec__usage_count=1)
    item.reload()
    if item.usage_count <= 0:
        item.delete()

    return {"message": f"Item removed from category '{category}'"}

def remove_wardrobe(user_id: str):
    try:
        wardrobe = Wardrobe.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError(f"Wardrobe for user_id '{user_id}' does not exist.")

    item_ids_to_check = set()
    for items in wardrobe.categories.values():
        for embedded in items:
            if hasattr(embedded, "item_id"):
                item_ids_to_check.add(embedded.item_id)
    wardrobe.wardrobeCount = 0
    wardrobe.delete()

    for item_id in item_ids_to_check:
        item = Item.objects(id=item_id).first()
        if item:
            item.update(dec__usage_count=1)
            item.reload()
            if item.usage_count <= 0:
                item.delete()

    return {"message": f"Wardrobe and all related items removed for user '{user_id}'"}


def get_wardrobe(user_id: str):
    try:
        wardrobe = Wardrobe.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError(f"Wardrobe for user_id '{user_id}' does not exist.")

    wardrobe_data = {
        "user_id": str(wardrobe.user_id),
        "wardrobeCount": wardrobe.wardrobeCount,
        "categories": {}
    }

    for category_name, category_data in wardrobe.categories.items():
        wardrobe_data["categories"][category_name] = {
            "count": category_data.count,
            "items": [
                {
                    "item_id": str(item.item_id),
                    "type": item.type,
                    "gender": item.gender,
                    "price": item.price,
                    "color": item.color,
                    "image_url": item.image_url,
                }
                for item in category_data.items
            ]
        }

    return wardrobe_data


def get_specific_item_from_wardrobe(user_id: str, item_id: str):
    try:
        wardrobe = Wardrobe.objects.get(user_id=ObjectId(user_id))
    except DoesNotExist:
        raise ValueError(f"Wardrobe for user_id '{user_id}' does not exist.")

    target_id = ObjectId(item_id)

    for category_name, category_data in wardrobe.categories.items():
        for item in category_data.items:
            if hasattr(item, "item_id") and item.item_id == target_id:
                return {
                    "item_id": str(item.item_id),
                    "type": item.type,
                    "gender": item.gender,
                    "price": item.price,
                    "color": item.color,
                    "image_url": item.image_url,
                    "category": category_name
                }

    raise ValueError(f"Item with ID '{item_id}' not found in wardrobe.")
