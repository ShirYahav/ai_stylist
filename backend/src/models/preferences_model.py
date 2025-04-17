import mongoengine as me

from src.enums.aesthetics_enum import AestheticsEnum
from src.enums.celebrities_enum import CelebritiesEnum
from src.enums.colors_enum import ColorsEnum

class Preferences(me.Document):
    user = me.ReferenceField("User", required=True)
    brands = me.ListField(me.StringField(), default=list)
    aesthetics = me.ListField(me.StringField(choices=[e.value for e in AestheticsEnum]), default=list)
    celebrities = me.ListField(me.StringField(choices=[e.value for e in CelebritiesEnum]), default=list)
    colors = me.ListField(me.StringField(choices=[e.value for e in ColorsEnum]), default=list)

    meta = {
        'collection': 'preferences'
    }
