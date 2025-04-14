from src.models.wishlist_model import Wishlist
from src.models.wardrobe_model import Wardrobe
from src.models.item_model import EmbeddedItem, Item
from bson import ObjectId
from mongoengine.errors import DoesNotExist
from src.logic.wardrobe_logic import convert_result_to_item


def add_item_to_wishlist(user_id: str, result: dict):
    item = convert_result_to_item(result)
    try:
        wardrobe = Wardrobe.objects.get(user_id=user_id)
        for category_items in wardrobe.categories.values():
            for embedded in category_items:
                if embedded.image_url == item.image_url:
                    raise ValueError("Item already exists in user's wardrobe.")
    except Wardrobe.DoesNotExist:
        pass 

    wishlist = Wishlist.objects(user_id=user_id).first()
    if not wishlist:
        wishlist = Wishlist(user_id=user_id, items=[])
        

    for embedded in wishlist.items:
        if embedded.image_url == item.image_url:
            raise ValueError("Item already exists in wishlist.")

    if not item.id:
        item.usage_count = 1
        item.save()
    else:
        item.update(inc__usage_count=1)
        wishlist.wishlistCount +=1
        wishlist.save()  
    embedded = EmbeddedItem.from_item(item)
    wishlist.items.append(embedded)
    wishlist.save()
    return {"message": "Item added to wishlist", "id": str(item.id)}


def remove_item_from_wishlist(user_id: str, item_id: str):
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError(f"Wishlist for user_id '{user_id}' does not exist.")

    item_object_id = ObjectId(item_id)
    found = False

    new_items = []
    for embedded in wishlist.items:
        if hasattr(embedded, "item_id") and embedded.item_id == item_object_id:
            found = True
            wishlist.wishlistCount -=1
            wishlist.save()  
        else:
            new_items.append(embedded)

    if not found:
        raise ValueError("Item not found in wishlist.")

    wishlist.items = new_items
    wishlist.save()

    item = Item.objects(id=item_object_id).first()
    if item:
        item.update(dec__usage_count=1)
        item.reload()
        if item.usage_count <= 0:
            item.delete()

    return {"message": f"Item {item_id} removed from wishlist."}

def remove_wishlist(user_id: str):
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError(f"Wishlist for user_id '{user_id}' does not exist.")

    item_ids_to_check = set()
    for embedded in wishlist.items:
        if hasattr(embedded, "item_id"):
            item_ids_to_check.add(embedded.item_id)
    wishlist.wishlistCount = 0
    wishlist.delete()

    for item_id in item_ids_to_check:
        item = Item.objects(id=item_id).first()
        if item:
            item.update(dec__usage_count=1)
            item.reload()
            if item.usage_count <= 0:
                item.delete()

    return {"message": f"Wishlist for user_id '{user_id}' has been removed."}





def move_item_from_wishlist_to_wardrobe(user_id: str, item_id: str, category: str):
    item_object_id = ObjectId(item_id)

    # שליפת הפריט מה-Item
    item = Item.objects(id=item_object_id).first()
    if not item:
        raise ValueError("Item does not exist.")

    # שליפת ה-Wishlist
    wishlist = Wishlist.objects(user_id=user_id).first()
    if not wishlist:
        raise ValueError("Wishlist does not exist.")

    # בדיקה אם הפריט קיים ב-wishlist
    found = False
    for emb in wishlist.items:
        if hasattr(emb, "item_id") and emb.item_id == item_object_id:
            found = True
            wishlist.wishlistCount -= 1
            break

    if not found:
        raise ValueError("Item not found in wishlist.")

    # הסרה מה-wishlist
    wishlist.items = [
        emb for emb in wishlist.items
        if not (hasattr(emb, "item_id") and emb.item_id == item_object_id)
    ]
    wishlist.save()

    # שליפת הארון
    wardrobe = Wardrobe.objects(user_id=user_id).first()
    if not wardrobe:
        raise ValueError("Wardrobe does not exist.")

    if category not in wardrobe.categories:
        raise ValueError(f"Category '{category}' does not exist in wardrobe.")

    category_data = wardrobe.categories[category]

    for emb in category_data.items:
        if emb.image_url == item.image_url:
            raise ValueError("Item already exists in wardrobe category.")

    # הוספה לארון
    embedded = EmbeddedItem.from_item(item)
    category_data.items.append(embedded)
    category_data.count += 1
    wardrobe.wardrobeCount += 1
    wardrobe.save()

    # עדכון usage count של הפריט
    item.update(inc__usage_count=1)

    return {
        "message": f"Item moved from wishlist to category '{category}' in wardrobe.",
        "item_id": str(item.id)
    }

def get_specific_item_from_wishlist(user_id: str, item_id: str):
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
    except DoesNotExist:
        raise ValueError(f"Wishlist for user_id '{user_id}' does not exist.")

    item_object_id = ObjectId(item_id)

    for item in wishlist.items:
        if hasattr(item, "item_id") and item.item_id == item_object_id:
                    return {
                    "item_id": str(item.item_id),
                    "type": item.type,
                    "gender": item.gender,
                    "price": item.price,
                    "color": item.color,
                    "image_url": item.image_url,
                }

    raise ValueError("Item not found in wishlist.")

def get_wishlist(user_id: str):
    try:
        wishlist = Wishlist.objects.get(user_id=ObjectId(user_id))
    except DoesNotExist:
        raise ValueError(f"Wishlist for user_id '{user_id}' does not exist.")

    wishlist_data = {
        "user_id": str(wishlist.user_id),
        "wishlistCount": wishlist.wishlistCount,
        "items": []
    }

    for embedded_item in wishlist.items:
        try:
            item = Item.objects.get(id=embedded_item.item_id)
            wishlist_data["items"].append({
                "item_id": str(item.id),
                "type": item.type,
                "gender": item.gender,
                "price": item.price,
                "color": item.color,
                "image_url": item.image_url
            })
        except Item.DoesNotExist:
            continue  # אם פריט לא קיים במסד, פשוט מדלגים עליו

    return wishlist_data