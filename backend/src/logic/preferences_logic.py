from enum import Enum
from src.enums.aesthetics_enum import AestheticsEnum
from src.enums.celebrities_enum import CelebritiesEnum
from src.enums.colors_enum import ColorsEnum
from src.models.preferences_model import Preferences
from src.models.user_model import User

def validate_enum_values(field_name: str, values: list[str], enum_cls: Enum):
    enum_values = {e.value for e in enum_cls}
    invalid = [v for v in values if v not in enum_values]
    if invalid:
        raise ValueError(f"Invalid {field_name} values: {invalid}")

def create_preferences_for_user(user_id: str, data: dict) -> Preferences:

    user = User.objects(id=user_id).first()
    if not user:
        raise ValueError("User not found")
    
    validate_enum_values("aesthetics", data.get("aesthetics", []), AestheticsEnum)
    validate_enum_values("celebrities", data.get("celebrities", []), CelebritiesEnum)
    validate_enum_values("colors", data.get("colors", []), ColorsEnum)


    prefs = Preferences(
        user=user,
        brands=data.get("brands", []),
        aesthetics=data.get("aesthetics", []),
        celebrities=data.get("celebrities", []),
        colors=data.get("colors", []),
    )
    prefs.save()
    
    user.preferences = prefs.id
    user.save()
    
    return prefs


def get_preferences(user_id: str):
    prefs = Preferences.objects(user=user_id).first()
    if not prefs:
        raise ValueError("Preferences not found for this user.")
    return prefs


def update_preferences(user_id: str, data: dict) -> Preferences:
    
    prefs = Preferences.objects(user=user_id).first()
    if not prefs:
        raise ValueError("Preferences not found for this user.")
    
    if "aesthetics" in data:
        validate_enum_values("aesthetics", data["aesthetics"], AestheticsEnum)
    if "celebrities" in data:
        validate_enum_values("celebrities", data["celebrities"], CelebritiesEnum)
    if "colors" in data:
        validate_enum_values("colors", data["colors"], ColorsEnum)

    for field in ["brands", "aesthetics", "celebrities", "colors"]:
        if field in data:
            setattr(prefs, field, data[field])
    
    prefs.save()
    return prefs
