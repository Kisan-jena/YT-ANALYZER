from transformers import T5ForConditionalGeneration, T5Tokenizer, Trainer, TrainingArguments, DataCollatorForSeq2Seq
from datasets import load_dataset

# Load the T5 model and tokenizer
model_name = "t5-base"  # Use "t5-base" or "t5-large" for potentially better results
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Load your fine-tuning dataset
dataset = load_dataset("AdamLucek/youtube-titles")  # Ensure the dataset is formatted correctly.

# Preprocessing function for tokenizing the inputs and outputs
def preprocess_function(examples):
    inputs = [f"generate youtube title: {desc}" for desc in examples['prompt']]
    targets = examples['video_title']  # Make sure you use the correct column for the title
    model_inputs = tokenizer(inputs, max_length=128, truncation=True)
    labels = tokenizer(targets, max_length=30, truncation=True).input_ids

    # Replace -100 with a value that can be ignored by the loss function
    # to handle padding in the labels
    labels = [l if l != tokenizer.pad_token_id else -100 for l in labels]

    model_inputs["labels"] = labels
    return model_inputs

# Preprocess the dataset
tokenized_datasets = dataset.map(preprocess_function, batched=True)

# Training configuration
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=3,
    weight_decay=0.01,
    save_steps=500,
    logging_steps=500,
)

# Data collator that handles padding
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],  # Optional validation dataset
    data_collator=data_collator,
    tokenizer=tokenizer,
)

# Train the model
trainer.train()

# Save the fine-tuned model
model.save_pretrained("./fine-tuned-t5")
tokenizer.save_pretrained("./fine-tuned-t5")
