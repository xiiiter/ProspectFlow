# LeadPilot

LeadPilot is a web dashboard for finding local business leads, enriching commercial data, generating outreach messages, and tracking follow-ups through email, WhatsApp, and a lightweight CRM.

## Features

- Search businesses by niche, city, and country.
- Review digital presence, phone numbers, WhatsApp availability, websites, social profiles, and Brazilian CNPJ data.
- Export lead results to Excel spreadsheets.
- Generate outreach emails with local templates or the Anthropic API.
- Send emails through Gmail OAuth.
- Support WhatsApp Web follow-ups and local conversation handling with Ollama.
- Track each lead through a simple CRM board.

## Getting Started

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python server.py
```

Then open `http://localhost:5000`.

## Configuration

1. Copy `.env.example` to `.env` and fill in your sender details.
2. For Gmail sending, create OAuth credentials in Google Cloud and save them as `credentials.json`.
3. The `token.json` file is created automatically after the first authorization.
4. WhatsApp session data is stored in `wa_profile/` and should never be committed.

## Before Committing

Credentials, sessions, generated spreadsheets, and local logs are already protected by `.gitignore`. Before publishing the project, review these paths carefully:

- `.env`
- `credentials.json`
- `token.json`
- `wa_session.json`
- `wa_profile/`
- `data/leads/`
- `data/logs/`
