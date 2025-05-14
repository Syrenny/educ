![CI](https://github.com/Syrenny/educ/actions/workflows/test.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/USERNAME/REPO_NAME/badge.svg?branch=main)](https://coveralls.io/github/USERNAME/REPO_NAME?branch=main)

# Educ Chat

**Educ Chat** — это прототип интерактивного учебного пособия на базе Retrieval Augmented Generation. Пользователь может загружать PDF-документы, задавать вопросы и получать ответы с указанием релевантных фрагментов текста.

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

