# AI Telegram Finance

`p_choa` — это финансовый ассистент, построенный как мультиагентная AI-система. Несколько интеллектуальных агентов работают совместно как единый механизм, анализируя запросы, обрабатывая финансовый контекст и формируя структурированные ответы.

Проект ориентирован на модульность, прозрачную архитектуру и готовность к production.

---

## Возможности

* Мультиагентная архитектура
* Финансовый анализ и структурированное рассуждение
* Координация взаимодействия агентов
* Готовый Docker-образ
* Быстрая установка через `uv`
* Конфигурация через переменные окружения

---

## Архитектура

Система построена вокруг нескольких AI-агентов, объединённых общим уровнем оркестрации.
Каждый агент выполняет свою роль, а логика координации объединяет их выводы в финальный ответ.

Общий поток работы:

Пользователь → Telegram-бот → Оркестратор → Специализированные AI-агенты → Итоговый ответ

---

## Установка

### Вариант 1 — Локально (для разработки)

Требуется:

* Python 3.13+
* `uv`

#### Клонируем репозиторий

```bash
git clone https://github.com/lambda19-auto/p_choa.git
```

#### Создание и активация виртуального окружения

```bash
uv venv
source .venv/bin/activate.fish
```

#### Установка зависимостей

```bash
uv sync
```

#### Переменные окружения

Создайте файл `.env` на основе:

```
.env.example
```

Обязательные ключи:

```
OPENROUTER_API_KEY=
BOT_TOKEN=
HEYGEN_API_KEY=
WEBHOOK_BASE_URL=
WEBHOOK_PATH=/telegram/webhook
WEBHOOK_SECRET_TOKEN=
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8080
```

Дополнительно для синхронизации журнала операций и ОДДС с Google Sheets:

```
GOOGLE_CREDENTIALS_JSON=google_credentials.json
GOOGLE_JOURNAL_SHEET_URL=https://docs.google.com/spreadsheets/d/.../edit#gid=...
GOOGLE_CFS_SHEET_URL=https://docs.google.com/spreadsheets/d/.../edit#gid=...
```

> `GOOGLE_CREDENTIALS_JSON` — имя или путь к JSON-файлу сервисного аккаунта Google.
> По вашему сценарию файл можно разместить прямо в корне проекта `p_choa/`.

Используемые сервисы:

* OpenRouter
* HeyGen
* Google Sheets API (опционально, для хранения журнала и отчета ОДДС)

#### Запуск

Бот запускается в режиме **webhook** (без long polling). Укажите публичный HTTPS URL в `WEBHOOK_BASE_URL` (например, через Nginx/Cloudflare tunnel), после чего запустите:

```bash
python3 -m service.telegram.bot
```

---

### Вариант 2 — Docker (рекомендуемый способ)

Docker-образ доступен на Docker Hub.

Загрузка образа:

```bash
docker pull lambda19main/p_choa:latest
```
Пример запуска:

```bash
docker run -d \
  --name choa-bot \
  --restart unless-stopped \
  -p 8080:8080 \
  -e OPENROUTER_API_KEY=your_key \
  -e BOT_TOKEN=your_token \
  -e HEYGEN_API_KEY=your_token \
  -e WEBHOOK_BASE_URL=https://your-domain.example \
  -e WEBHOOK_PATH=/telegram/webhook \
  -e WEBHOOK_SECRET_TOKEN=your_secret \
  -e WEB_SERVER_HOST=0.0.0.0 \
  -e WEB_SERVER_PORT=8080 \
  lambda19main/p_choa:latest
```

---

## Демонстрация

Видео с демонстрацией работы бота доступно по ссылке: 
https://youtu.be/ibiy3S2DCNc

---

## Конфигурация

Настройка осуществляется через переменные окружения.

Для локальной разработки:

* переименуйте `.env.example` → `.env`

Для production:

* передавайте переменные через флаг `-e` в Docker
* либо используйте менеджер секретов вашей инфраструктуры

---

## Требования

* Python 3.13+
* Токен Telegram-бота
* OpenRouter API Key
* HeyGen API Key

---

## Разработка

Проект построен с акцентом на:

* Чёткое разделение ролей агентов
* Расширяемую логику оркестрации
* Возможность дальнейшей интеграции финансовых инструментов

---

AI-консультант компании Atomy от lambda19.
