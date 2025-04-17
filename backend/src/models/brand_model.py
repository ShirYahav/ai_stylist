import mongoengine as me

class Brand(me.Document):
    name = me.StringField(required=True, unique=True)

    meta = {
        'collection': 'brands'
    }
