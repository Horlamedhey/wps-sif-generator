# Deployment Guide

## Architecture
- Frontend: SvelteKit on Vercel (`/frontend`)
- Backend: FastAPI on Render (`/backend`)

## 1) Deploy FastAPI to Render
1. Push this repo to GitHub.
2. In Render, create a new Web Service from the repo.
3. Set root directory to `backend`.
4. Use:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Configure env vars:
   - `PYTHON_VERSION=3.12.9` (important: avoid Render default Python 3.14 for now)
   - `CORS_ALLOW_ORIGINS=https://<your-vercel-production-domain>`
   - `CORS_ALLOW_ORIGIN_REGEX=https://.*\\.vercel\\.app`
6. Confirm `GET /health` returns `{"status":"ok"}`.

## 2) Deploy SvelteKit to Vercel
1. Create a Vercel project with root directory `frontend`.
2. Add env var:
   - `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`
3. Build/deploy using Vercel defaults for SvelteKit.

## 3) Validate Production E2E
1. Open frontend URL.
2. Confirm banks list loads.
3. Fill fields and generate `.xlsx`.
4. Confirm download works and filename matches `SIF_<employer>_<bank>_<yyyymmdd>_<seq>.xlsx`.

## Notes
- Backend exposes `Content-Disposition` and `X-Generated-Filename` so browser clients can preserve download filename.
- CORS is configured for exact production domain and preview domains via regex.
