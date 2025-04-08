import mongoengine as me

class Outfit(me.Document):
    
    user_id = me.ObjectIdField(required=True)
    items = me.ListField(me.ReferenceField('Item'), default=list)
    occasions = me.ListField (me.StringField(), default=list)

    meta = {
        'collection': 'outfits'
    }