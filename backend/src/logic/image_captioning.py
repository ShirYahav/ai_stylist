from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io

processor = BlipProcessor.from_pretrained("./blip-finetuned-fashion")
model = BlipForConditionalGeneration.from_pretrained("./blip-finetuned-fashion")

def extract_query_from_image(image_bytes):
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    inputs = processor(image, return_tensors="pt")
    
    outputs = model.generate(**inputs, max_length=50, num_beams=4, early_stopping=True)
    
    raw_caption = processor.decode(outputs[0], skip_special_tokens=True).strip().lower()
    return raw_caption
