# Setup

Manual, one-time steps needed to bring the platform online. Everything else is code, tracked in this repo.

## 1. Supabase (Phase 1)

- [ ] Create a new Supabase project (you already have an account) — free tier
- [ ] Copy the Postgres connection details (host, port, db name, user, password) into a local `.env` (see `env.example`)
- [ ] Add the same values as GitHub Actions repo secrets (Settings → Secrets and variables → Actions) so `.github/workflows/daily-ingestion.yml` can run

## 2. FRED API (Phase 2)

- [ ] Request a free API key at https://fred.stlouisfed.org/docs/api/api_key.html
- [ ] Add `FRED_API_KEY` to `.env` and to GitHub Actions secrets

## 3. Tableau Public (Phase 6)

- [ ] Create a free account at https://public.tableau.com
- [ ] Publish the anomaly-detection dashboard once the gold-layer marts exist

## 4. Streamlit Community Cloud (Phase 6)

- [ ] Create a free account at https://streamlit.io/cloud (sign in with GitHub)
- [ ] Deploy `streamlit_app/` once it has content, pointing at this repo

## 5. Local Python environment

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy env.example .env
```
