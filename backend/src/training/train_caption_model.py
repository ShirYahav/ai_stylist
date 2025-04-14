from datasets import load_dataset
from transformers import BlipForConditionalGeneration, BlipProcessor, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from preprocess import preprocess_sample 

def load_and_preprocess_dataset():
   
    dataset = load_dataset("tomytjandra/h-and-m-fashion-caption", split="train")
    
    dataset = dataset.shuffle(seed=42)
    
    small_dataset = dataset.select(range(1000))
    
    processed_dataset = small_dataset.map(
        preprocess_sample,
        remove_columns=dataset.column_names,
        load_from_cache_file=False
    )
    
    return processed_dataset


def main():
    
    processed_dataset = load_and_preprocess_dataset()

    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    
    training_args = TrainingArguments(
        output_dir="./blip-finetuned-fashion", 
        num_train_epochs=3, 
        per_device_train_batch_size=8,
        save_steps=500,
        logging_steps=100,
        learning_rate=5e-5, 
        weight_decay=0.01,
        fp16=True,
    )
    
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    tokenizer = processor.tokenizer  
    data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=processed_dataset,
        data_collator=data_collator,
    )
    
    trainer.train()
    
    trainer.save_model("./blip-finetuned-fashion")

if __name__ == "__main__":
    main()
