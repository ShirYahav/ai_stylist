from src.logic.wardrobe_logic import get_wardrobe
from src.logic.wishlist_logic import get_wishlist
from src.logic.weather_logic import get_weather_and_time
from src.logic.preferences_logic import get_preferences
from src.models.user_model import User
from bson import ObjectId
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_id = "finetuned-llama3"

model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=torch.float16, device_map="auto")
tokenizer = AutoTokenizer.from_pret

def fetch_user_context(user_id: str) -> str:
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return "No user context available."

    try:
        wardrobe = get_wardrobe(user.id)
    except:
        wardrobe = {"categories": {}}

    try:
        wishlist = get_wishlist(user.id)
    except:
        wishlist = {"items": []}

    try:
        prefs = get_preferences(user.id)
    except:
        prefs = {}

    try:
        weather = get_weather_and_time(str(user.id))
    except:
        weather = {}

    wardrobe_items = []
    for cat, data in wardrobe["categories"].items():
        for item in data["items"]:
            wardrobe_items.append(f"{item['type']} ({', '.join(item['color'])})")

    wishlist_items = [f"{item['type']} ({', '.join(item['color'])})" for item in wishlist["items"]]

    context_parts = [
        f"User is from {user.city}, {user.country}.",
        f"Current weather: {weather.get('weather_description', 'unknown')} and {weather.get('temperature', '?')}°C.",
        f"User's wardrobe: {', '.join(wardrobe_items) if wardrobe_items else 'empty.'}",
        f"User's wishlist: {', '.join(wishlist_items) if wishlist_items else 'empty.'}",
        f"User prefers colors: {', '.join(prefs.colors) if prefs else 'unknown' }.",
        f"User's preferred aesthetics: {', '.join(prefs.aesthetics) if prefs else 'unknown'}."
    ]

    return " ".join(context_parts)

class ChatSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.messages = []

    def _build_prompt(self):
        parts = ["<|begin_of_text|>"]
        for msg in self.messages:
            parts.append(f"<|start_header_id|>{msg['role']}<|end_header_id|>\n{msg['content']}<|eot_id|>")
        parts.append("<|start_header_id|>assistant<|end_header_id|>\n")
        return "".join(parts)

    def ask(self, user_input):
        context = fetch_user_context(self.user_id)
        self.messages.insert(0, {"role": "system", "content": context})
        self.messages.append({"role": "user", "content": user_input})

        prompt = self._build_prompt()
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )

        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        reply = decoded.split("<|start_header_id|>assistant<|end_header_id|>\n")[-1].strip()
        self.messages.append({"role": "assistant", "content": reply})
        return reply