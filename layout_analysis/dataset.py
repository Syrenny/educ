import os
import pickle
import zipfile

import pandas as pd
from datasets import Dataset
from huggingface_hub import hf_hub_download
from sklearn.preprocessing import LabelEncoder
from transformers import AutoTokenizer

docbank_zip = hf_hub_download(
    repo_id="liminghao1630/DocBank",
    filename="DocBank_500K_txt.zip",
    local_dir="./layout_analysis/raw",
    repo_type="dataset",
)
extract_dir = "./layout_analysis/raw/DocBank_500K_txt"

if not os.path.exists(extract_dir):
    with zipfile.ZipFile(docbank_zip, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

# Загрузка предобработанных данных
data = pd.read_json("docbank_blocks.json")  # Пример: [{"text": ..., "label": ...}]

# Кодировка меток
label_encoder = LabelEncoder()
data["label_id"] = label_encoder.fit_transform(data["label"])

# Сохраняем label encoder

with open("label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)

# Создание датасета HuggingFace
dataset = Dataset.from_pandas(data[["text", "label_id"]])
dataset = dataset.train_test_split(test_size=0.1)

# Токенизатор
checkpoint = "cointegrated/rubert-tiny2"
tokenizer = AutoTokenizer.from_pretrained(checkpoint)


def tokenize(example):
    return tokenizer(
        example["text"], truncation=True, padding="max_length", max_length=128
    )


tokenized = dataset.map(tokenize, batched=True)

# Сохраняем токенизированный датасет
tokenized.save_to_disk("docbank_tokenized")
