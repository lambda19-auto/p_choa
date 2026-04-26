# AI Telegram Finance

`p_choa` is a financial assistant built as a multi-agent AI system. Multiple intelligent agents work together as a single mechanism, analyzing requests, processing financial context, and producing structured responses.

The project is focused on modularity, transparent architecture, and production readiness.

---

## Features

* Multi-agent architecture
* Financial analysis and structured reasoning
* Agent interaction orchestration
* Ready-to-use Docker image
* Fast installation via `uv`
* Configuration through environment variables

---

## Architecture

The system is built around several AI agents connected through a shared orchestration layer.
Each agent performs its own role, while coordination logic combines their outputs into the final response.

General workflow:

User → Telegram bot → Orchestrator → Specialized AI agents → Final response

---

## Installation

### Option 1 — Local setup (for development)

Requirements:

* Python 3.13+
* `uv`

#### Clone the repository

```bash
git clone https://github.com/lambda19-auto/p_choa.git
```

#### Create and activate a virtual environment

```bash
uv venv
source .venv/bin/activate.fish
```

#### Install dependencies

```bash
uv sync
```

#### Environment variables

Create a `.env` file based on:

```
.env.example
```

Required keys:

```
# OpenRouter
OPENROUTER_API_KEY=your_api_key

# Telegram Bot
BOT_TOKEN=your_token
WEBHOOK_BASE_URL=your_domain
WEBHOOK_PATH=/telegram/webhook
WEBHOOK_SECRET_TOKEN=your_strong_password
WEB_SERVER_HOST=0.0.0.0
WEB_SERVER_PORT=8080

# HeyGen
HEYGEN_API_KEY=your_api_key

# Google Sheets API
# JSON key file should be placed in repository root (p_choa/)
GOOGLE_CREDENTIALS_JSON=google_credentials.json
GOOGLE_JOURNAL_SHEET_URL=your_table
GOOGLE_CFS_SHEET_URL=your_table
```

Additionally, for synchronizing the operations journal and CFS report with Google Sheets:

```
GOOGLE_CREDENTIALS_JSON=google_credentials.json
GOOGLE_JOURNAL_SHEET_URL=https://docs.google.com/spreadsheets/d/.../edit#gid=...
GOOGLE_CFS_SHEET_URL=https://docs.google.com/spreadsheets/d/.../edit#gid=...
```

> `GOOGLE_CREDENTIALS_JSON` is the name or path to a Google service account JSON file.
> Depending on your setup, you can place the file directly in the project root `p_choa/`.

Services used:

* OpenRouter
* HeyGen
* Google Sheets API (optional, for storing the operations journal and CFS report)

#### Run

The bot runs in **webhook** mode (without long polling). Set a public HTTPS URL in `WEBHOOK_BASE_URL` (for example, via Nginx/Cloudflare Tunnel), then run:

```bash
python3 -m service.telegram.bot
```

---

### Option 2 — Docker (recommended)

The Docker image is available on Docker Hub.

Pull the image:

```bash
docker pull lambda19main/p_choa:1.0.0
```
Prepare a local `data` directory (on the host), which should contain:

* `google_credentials.json` for Google Sheets
* a `logs/` subdirectory for container logs

```bash
mkdir -p data/logs
# Copy your service account file:
# cp /path/to/google_credentials.json data/google_credentials.json
```

Run example:

```bash
docker run -d \
  --name choa-bot \
  --restart unless-stopped \
  -p 8080:8080 \
  -v "$(pwd)/data/credentials.json:/p_choa/credentials.json" \
  -v "$(pwd)/data/logs:/p_choa/logs" \
  -e OPENROUTER_API_KEY=your_key \
  -e BOT_TOKEN=your_token \
  -e HEYGEN_API_KEY=your_key \
  -e WEBHOOK_BASE_URL=https://your-domain.example \
  -e WEBHOOK_PATH=/telegram/webhook \
  -e WEBHOOK_SECRET_TOKEN=your_secret \
  -e WEB_SERVER_HOST=0.0.0.0 \
  -e WEB_SERVER_PORT=8080 \
  -e GOOGLE_CREDENTIALS_JSON=/p_choa/credentials.json \
  -e GOOGLE_JOURNAL_SHEET_URL="https://docs.google.com/spreadsheets/d/.../edit#gid=..." \
  -e GOOGLE_CFS_SHEET_URL="https://docs.google.com/spreadsheets/d/.../edit#gid=..." \
  p_choa:1.0.0
```

---

## Configuration

Configuration is done via environment variables.

For local development:

* rename `.env.example` → `.env`

For production:

* pass variables using `-e` flags in Docker
* or use your infrastructure's secret manager

---

## Requirements

* Python 3.13+
* Telegram bot token
* OpenRouter API key
* HeyGen API key

---

## Development

The project is built with an emphasis on:

* Clear separation of agent roles
* Extensible orchestration logic
* Future integration of financial tools

---

