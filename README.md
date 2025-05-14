![CI](https://github.com/Syrenny/educ/actions/workflows/test.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/USERNAME/REPO_NAME/badge.svg?branch=main)](https://coveralls.io/github/USERNAME/REPO_NAME?branch=main)

# Educ Chat

**[Educ Chat](https://github.com/Syrenny/educ)** — это прототип интерактивного учебного пособия на базе Retrieval Augmented Generation. Пользователь может загружать PDF-документы, задавать вопросы и получать ответы с указанием релевантных фрагментов текста.

---

### 🚀 Запуск

#### Разработка

1. Клиент:

```bash
cd client
npm install
npm start
```

2. Сервер:

```bash
cd server/docker
docker compose -f compose.dev.yml up
```

#### Продакшн

```bash
cd server/docker
docker compose -f compose.prod.yml up -d
```

---

### 🧪 Тестирование

1. Установить `env='TEST'` в `server/config.yaml`
2. Запустить:

```bash
. .venv/bin/activate
pytest
```

### Бенчмарк

Стоит отметить, что для запуска бенчмарка и конфигурации AgenticRAG понадобится подключиться большую языковую модель, поддерживающую инструменты.

0. Подготовка окружения:

```bash
sudo apt install pipx
pipx install uv
uv sync
```

1. Запуск подготовки датасета:

```bash
uv run -m benchmark.dataset
```

После успешного выполнения в терминале будет оставлено сообщение вида:

Dataset checkpoint created at: benchmark/data/transformed/datasets/FRAMES_2025-05-14_12-05-09_Lzi3Ny

На следующем этапе необходимо подставить путь из этого сообщения

2. Запуск бенчмарка:

```bash
uv run -m benchmark.evaluate --config < system / agentic / llm > --checkpoint <путь до директории с датасетом>
```
