import mongoengine as me

class User(me.Document):
    
    email = me.StringField(required=True)
    password_hash = me.StringField(required=True)
    full_name = me.StringField()
    country = me.StringField(required=True)
    city = me.StringField(required=True)
    gender = me.StringField()    
    preferences = me.ReferenceField("Preferences",default=None)
    wardrobe = me.ReferenceField("Wardrobe",default=None)
    wishlist = me.ReferenceField("Wishlist",default=None)
    outfits = me.ListField(me.ReferenceField('Outfit'), default=list)

    meta = {
        'collection': 'users'
    }
