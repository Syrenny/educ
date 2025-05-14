![CI](https://github.com/Syrenny/educ/actions/workflows/test.yml/badge.svg)

[![Coverage Status](https://coveralls.io/repos/github/USERNAME/REPO_NAME/badge.svg?branch=main)](https://coveralls.io/github/USERNAME/REPO_NAME?branch=main)

# Educ Chat

Проект представляет собой прототип, который использует возможности Retrieval Augmented Generation для реализации интерактивного учебного пособия - файла в формате PDF, с которым можно вести диалог, задавать вопросы и получать не только ответы, но и ссылки на фрагменты в тексте.

### Запуск проекта

#### Разработка

1. Запуск клиента

В `./client`:

```bash
npm install
npm start
```

2. Запуск сервера

В `./server/docker`:

```bash
docker compose -f compose.dev.yml up
```

Код автоматически обновляется в контейнере

#### Развертывание

В `./server/docker`:

```bash
docker compose -f compose.prod.yml up -d
```

Сервис будет развернут на порту 3000

### Запуск тестов

0. Поменять конфигурацию в `./server/config.yaml`, где нужно выставить `env='TEST'`

1. В корне проекта:

```bash
. .venv/bin/activate
pytest
```
