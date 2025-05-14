import zipfile
from pathlib import Path

from datasets import Dataset
from huggingface_hub import hf_hub_download
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm
from transformers import AutoTokenizer

# 📁 Пути
raw_dir = Path("layout_analysis/raw")
docbank_zip_path = hf_hub_download(
    repo_id="liminghao1630/DocBank",
    filename="DocBank_500K_txt.zip",
    local_dir=str(raw_dir),
    repo_type="dataset",
)

extract_dir = raw_dir / "DocBank_500K_txt"

# 🗂️ Распаковка
if not extract_dir.exists():
    with zipfile.ZipFile(docbank_zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)


# 📄 Загрузка данных
def parse_docbank_folder(folder_path: Path, label_encoder: LabelEncoder = None):
    data = []

    txt_files = list(folder_path.glob("**/*.txt"))
    for txt_path in tqdm(txt_files, desc="Parsing DocBank"):
        tokens = []
        labels = []
        with txt_path.open(encoding="utf-8") as f:
            prev_label = None
            for line in f:
                parts = line.strip().split()
                if len(parts) < 6:
                    continue
                token = parts[0]
                tag = parts[-1].strip("<>").upper()

                # BIO-тегирование
                if prev_label != tag:
                    bio_tag = f"B-{tag}"
                else:
                    bio_tag = f"I-{tag}"
                prev_label = tag

                tokens.append(token)
                labels.append(bio_tag)

        if tokens:
            data.append({"tokens": tokens, "labels": labels})

    # Обучение LabelEncoder (если не передан)
    if label_encoder is None:
        label_encoder = LabelEncoder()
        all_labels = [label for ex in data for label in ex["labels"]]
        label_encoder.fit(all_labels)

    # Преобразование меток в числа
    for example in data:
        example["labels"] = label_encoder.transform(example["labels"]).tolist()

    return data, label_encoder


# 🧩 Подготовка токенизатора и датасета
def tokenize_dataset(data, tokenizer, max_length=512):
    def tokenize_batch(batch):
        tokenized = tokenizer(
            batch["tokens"],
            is_split_into_words=True,
            truncation=True,
            padding="max_length",
            max_length=max_length,
        )
        labels = []
        for i, word_ids in enumerate(
            tokenized.word_ids(batch_index=i) for i in range(len(batch["tokens"]))
        ):
            word_labels = batch["labels"][i]
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)
                else:
                    label_ids.append(word_labels[word_idx])
            labels.append(label_ids)
        tokenized["labels"] = labels
        return tokenized

    dataset = Dataset.from_list(data)
    return dataset.map(tokenize_batch, batched=True)


# 🚀 Загрузка и токенизация
tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")

parsed_data, label_encoder = parse_docbank_folder(extract_dir)
tokenized_dataset = tokenize_dataset(parsed_data, tokenizer)

# 🔖 Сохранение, если нужно
tokenized_dataset.save_to_disk("layout_analysis/tokenized_docbank")
