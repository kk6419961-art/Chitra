# Chitra Platform v0.2 — expanded development scaffold

This release expands the initial starter with:
- local video upload endpoint (development only)
- FFmpeg HLS transcoding service wrapper
- public video feed and creator video listing
- likes, comments, subscriptions
- moderation review endpoints for admins
- ad campaign and ad-impression event models/endpoints
- eligibility-based creator monetization review
- Android Compose screens for feed, upload placeholder, Shorts and creator area
- Docker Compose for PostgreSQL and Redis

## Important
This is a development scaffold, not a production YouTube-scale service. It has not been
security-audited or load-tested. The local upload endpoint is for development only.
For production, replace local files with private object storage and signed upload URLs,
run FFmpeg in isolated workers, use a real ad server, implement robust invalid-traffic
controls, and integrate a compliant KYC/payment provider. Do not collect bank details
or identity documents directly in this starter.

## Run backend
```bash
cd backend
python -m venv .venv
# activate the environment
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

## Optional PostgreSQL + Redis
From the project root:
```bash
docker compose up -d
```
Then set `DATABASE_URL=postgresql+psycopg://chitra:change-me@localhost:5432/chitra`
and `REDIS_URL=redis://localhost:6379/0` in `backend/.env`.

## FFmpeg
Install FFmpeg on the worker machine and ensure `ffmpeg` is on PATH.
The API queues a local development transcode task synchronously; production must use
a background queue such as Celery/RQ/Arq and isolated worker containers.

## Android
Open `android/` in Android Studio. The app is a UI scaffold; connect API calls and
secure token storage before release.

## Still not included
A complete public production service also needs website/iOS clients, real OTP/email
verification, account recovery, production object storage/CDN, adaptive player,
notifications, recommendations, search indexing, reporting/appeals, privacy tools,
store billing where applicable, tax/compliance workflows, and operational monitoring.
