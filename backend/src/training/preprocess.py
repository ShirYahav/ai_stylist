from transformers import BlipProcessor

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

def preprocess_sample(example):

    inputs = processor(
        images=example["image"],
        text=example["text"], 
        return_tensors="pt",
        padding="max_length",
        max_length=20, 
        truncation=True,
    )
    
    example["pixel_values"] = inputs["pixel_values"].squeeze(0)
    example["input_ids"] = inputs["input_ids"].squeeze(0)
    example["labels"] = inputs["input_ids"].squeeze(0)
    
    return example

