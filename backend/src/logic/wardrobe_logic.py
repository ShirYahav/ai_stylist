from bson import ObjectId
from mongoengine.errors import DoesNotExist
from src.models.item_model import EmbeddedItem, Item
from src.models.wardrobe_model import Wardrobe
from typing import Optional

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

    if category_name.lower() in (name.lower() for name in wardrobe.categories.keys()):
        raise ValueError(f"Category '{category_name}' already exists.")

    wardrobe.categories[category_name] = []
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

    # בדיקה אם הפריט כבר קיים בקטגוריה
    for embedded in wardrobe.categories[category]:
        if embedded.image_url == item.image_url:
            raise ValueError("Item is already in the wardrobe category.")

    # בדיקה אם הפריט קיים ב-wishlist
    from src.models.wishlist_model import Wishlist
    wishlist = Wishlist.objects(user_id=user_id).first()
    if wishlist:
        for embedded in wishlist.items:
            if embedded.image_url == item.image_url:
                raise ValueError("Item exists in wishlist and cannot be added to wardrobe.")

    if not item.id:
        item.usage_count = 1
        item.save()
    else:
         item.update(inc__usage_count=1)  # מעלה את המונה

    embedded = EmbeddedItem.from_item(item)
    wardrobe.categories[category].append(embedded)
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

    original_count = len(wardrobe.categories[category])
    wardrobe.categories[category] = [
        emb for emb in wardrobe.categories[category]
        if emb.image_url != item.image_url
    ]

    if len(wardrobe.categories[category]) == original_count:
        raise ValueError("Item not found in category.")

    wardrobe.save()

    # עדכון מונה שימוש
    item.update(dec__usage_count=1)
    item.reload()  # נטען את הערך החדש
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

    wardrobe.delete()

    for item_id in item_ids_to_check:
        item = Item.objects(id=item_id).first()
        if item:
            item.update(dec__usage_count=1)
            item.reload()
            if item.usage_count <= 0:
                item.delete()

    return {"message": f"Wardrobe and all related items removed for user '{user_id}'"}
