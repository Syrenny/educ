# Educ Chat

**[Educ Chat](https://github.com/Syrenny/educ)** — это прототип интерактивного учебного пособия на основе технологии _Retrieval-Augmented Generation_ (RAG).
Система позволяет загружать PDF-документы, задавать вопросы на естественном языке и получать точные ответы с указанием соответствующих фрагментов из текста.

---

### Запуск

#### Режим разработки

**1. Клиентская часть:**

```bash
cd client
npm install
npm start
```

**2. Серверная часть:**

```bash
cd server/docker
docker compose -f compose.dev.yml up
```

#### Режим продакшена

```bash
cd server/docker
docker compose -f compose.prod.yml up -d
```

---

### 🧪 Тестирование

1. Установите переменную окружения `env='TEST'` в файле `server/config.yaml`
2. Запустите тесты:

```bash
. .venv/bin/activate
pytest
```

---

### 📊 Бенчмаркинг

Для оценки качества системы и использования расширенной конфигурации (например, AgenticRAG) необходимо подключение к языковой модели, поддерживающей работу с инструментами (например, `GPT-4o mini`).

#### Подготовка окружения:

```bash
sudo apt install pipx
pipx install uv
uv sync
```

#### 1. Подготовка датасета:

```bash
uv run -m benchmark.dataset
```

После выполнения в терминале появится сообщение с путём к сохранённому датасету, например:

```
Dataset checkpoint created at: benchmark/data/transformed/datasets/FRAMES_2025-05-14_12-05-09_Lzi3Ny
```

Скопируйте этот путь и используйте его на следующем этапе.

#### 2. Запуск бенчмарка:

```bash
uv run -m benchmark.evaluate --config <system | agentic | llm> --checkpoint <путь к датасету>
```

---

### 📄 Преобразование PDF → Markdown с помощью GROBID

Для выполнения пробной конвертации PDF-файла в формат Markdown:

1. Разверните контейнер с GROBID:

```bash
docker compose -f docker/compose.dev.yml up -d
```

2. Запустите скрипт:

```bash
uv run benchmark.test_grobid
```

---
