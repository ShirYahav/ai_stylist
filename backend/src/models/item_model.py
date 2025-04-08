import mongoengine as me

class EmbeddedItem(me.EmbeddedDocument):
    item_id = me.ObjectIdField(required=True)
    type = me.StringField(required=True)
    gender = me.StringField()
    brand = me.StringField(required=True)
    color = me.ListField(me.StringField(), default=list)
    material = me.StringField()
    image_url = me.StringField()

    @staticmethod
    def from_item(item):
        return EmbeddedItem(
            item_id=item.id,
            type=item.type,
            gender=item.gender,
            brand=item.brand,
            color=item.color,
            material=item.material,
            image_url=item.image_url
        )

class Item(me.Document):
    type = me.StringField(required=True)
    gender = me.StringField()
    brand = me.StringField(required=True)
    color = me.ListField(me.StringField(), default=list)
    material = me.StringField()
    image_url = me.StringField()
    usage_count = me.IntField(default=0)  

    meta = {
        'collection': 'items'
    }
