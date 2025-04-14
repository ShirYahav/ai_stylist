from transformers import BlipProcessor

base_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")

base_processor.save_pretrained("./blip-finetuned-fashion")
