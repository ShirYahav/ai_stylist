from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType, prepare_model_for_kbit_training
import torch

def build_prompt(example):
    parts = ["<|begin_of_text|>"]
    for m in example["messages"]:
        parts.append(f"<|start_header_id|>{m['role']}<|end_header_id|>\n{m['content']}<|eot_id|>")
    parts.append("<|start_header_id|>assistant<|end_header_id|>\n")
    return "".join(parts)

# טוען מודל בסיס של LLaMA 3 (8B) — צריך הרשאה מ-Meta
model_id = "meta-llama/Meta-Llama-3-8B"
tokenizer = AutoTokenizer.from_pretrained(model_id, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto",
    torch_dtype=torch.float16,
    use_auth_token=True
)

# הכנת המודל לאימון LoRA
model = prepare_model_for_kbit_training(model)
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8,
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    target_modules=["q_proj", "v_proj"]
)
model = get_peft_model(model, peft_config)

# טוען את הדאטה
dataset = load_dataset("json", data_files="dataset.jsonl", split="train")

# בונה פרומפטים
def tokenize(example):
    prompt = build_prompt(example)
    tokens = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

tokenized = dataset.map(tokenize)

# הגדרות אימון
args = TrainingArguments(
    output_dir="./finetuned-llama3",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=4,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=100,
    learning_rate=2e-4,
    fp16=True,
    report_to="none"
)

# מריץ אימון
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()

# שומר את המודל
trainer.save_model("./finetuned-llama3")
