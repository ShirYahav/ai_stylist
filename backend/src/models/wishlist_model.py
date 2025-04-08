import mongoengine as me
from src.models.item_model import EmbeddedItem

class Wishlist(me.Document):
    user_id = me.ObjectIdField(required=True)
    items = me.EmbeddedDocumentListField(EmbeddedItem, default=list)

    meta = {
        'collection': 'wishlist'
    }
