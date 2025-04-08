import mongoengine as me
from src.models.item_model import EmbeddedItem

class Wardrobe(me.Document):
    user_id = me.StringField(required=True, unique=True)
    categories = me.MapField(
        field=me.EmbeddedDocumentListField(EmbeddedItem),
        default=dict
    )

    meta = {
        'collection': 'wardrobes'
    }
