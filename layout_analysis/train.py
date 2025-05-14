import pickle

import numpy as np
from datasets import load_from_disk, load_metric
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
)

# Загрузка токенизированного датасета
tokenized = load_from_disk("docbank_tokenized")

# Загрузка label encoder
with open("label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

# Токенизатор и модель
checkpoint = "cointegrated/rubert-tiny2"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)

model = AutoModelForSequenceClassification.from_pretrained(
    checkpoint, num_labels=len(label_encoder.classes_)
)

# Метрика
accuracy = load_metric("accuracy")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return accuracy.compute(predictions=preds, references=labels)


# Аргументы обучения
training_args = TrainingArguments(
    output_dir="./rubert-docbank",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=5,
    weight_decay=0.01,
    logging_dir="./logs",
    report_to="none",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# Обучение
trainer.train()

# Сохранение модели и токенизатора
trainer.save_model("./rubert-docbank")
tokenizer.save_pretrained("./rubert-docbank")
