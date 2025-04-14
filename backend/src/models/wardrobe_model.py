import mongoengine as me
from src.models.item_model import EmbeddedItem

class CategoryData(me.EmbeddedDocument):
    count = me.IntField(default=0)
    items = me.EmbeddedDocumentListField(EmbeddedItem, default=list)

class Wardrobe(me.Document):
    user_id = me.ObjectIdField(required=True)
    wardrobeCount = me.IntField(default=0)

    categories = me.MapField(
        field=me.EmbeddedDocumentField(CategoryData),
        default=dict
    )

    meta = {
        'collection': 'wardrobes'
    }
