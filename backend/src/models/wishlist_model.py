import mongoengine as me
from src.models.item_model import EmbeddedItem

class Wishlist(me.Document):
    user_id = me.ObjectIdField(required=True)
    wishlistCount = me.IntField(default=0)
    items = me.EmbeddedDocumentListField(EmbeddedItem, default=list)

    meta = {
        'collection': 'wishlist'
    }
