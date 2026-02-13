# Oman WPS SIF Generator (Web)

This repository now contains:
- `backend/` FastAPI service for SIF validation/generation
- `frontend/` SvelteKit UI for employer/payer + employees flow

## Local Development

### Backend (FastAPI)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (SvelteKit)
```bash
cd frontend
npm install
cp .env.example .env
# set VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

Open `http://localhost:5173`.

## API
- `GET /health`
- `GET /api/banks`
- `POST /api/sif/preview`
- `POST /api/sif/generate`

## Bank Data Source
- Runtime bank data: `backend/data/omani_banks.json`
- Original source spreadsheet: `backend/data/source/Omani Banks List.xlsx`
- Regeneration script: `backend/scripts/xlsx_to_json.py`

## Deployment
See `DEPLOYMENT.md`.

## Skill (Global)
A new global Codex skill is installed at:
`/Users/varyable/.codex/skills/chatgpt-share-extractor`

It summarizes shared-chat links first and always asks whether to return full transcript.
