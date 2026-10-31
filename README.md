# SAHAYAK — सहायक

**BenefitBridge – Intelligent Government Scheme Matching System**

SAHAYAK (meaning "helper" in Sanskrit) is a hackathon project that helps citizens discover which government schemes they may be eligible for. It combines a **Python FastAPI backend** with a **vanilla JavaScript / HTML / CSS frontend**.

> ⚠️ **Illustrative prototype.** Scheme details, eligibility rules, benefits and limits here are simplified for a hackathon demo. Always confirm the latest criteria and the official application process with the concerned ministry or department before applying.

## Project structure

```
saha/
├── index.html              # Landing page
├── dashboard.html          # Citizen dashboard
├── profile.html            # Profile form
├── schemes.html            # Scheme discovery (search / filter)
├── matches.html            # Eligibility matching results
├── gap-analyzer.html       # Gap analysis
├── simulator.html          # What-if simulator
├── documents.html          # Document checklist
├── compare.html            # Scheme comparison
├── README.md
├── .gitignore
├── backend/                # FastAPI backend (copied from BenefitBridge)
│   ├── main.py             # App entry point + CORS
│   ├── models/schemas.py   # Pydantic models
│   ├── routes/             # HTTP route handlers
│   ├── services/           # Eligibility engine, gap analyzer, simulator, documents
│   ├── data/schemes.json   # Verified government schemes
│   └── tests/              # 114 passing tests
└── js/
    ├── data.js             # Illustrative data, field definitions, schemes
    ├── engine.js           # Local eligibility engine + localStorage store
    ├── api.js              # API client (talks to the FastAPI backend)
    ├── ui.js               # Shared UI: icons, toasts, modal, shell
    └── pages.js            # Page controllers
```

## Running the project

### 1. Backend (FastAPI, port 8000)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

API docs are available at `http://localhost:8000/docs`.

### 2. Frontend (static site, port 5500)

```bash
python -m http.server 5500
```

Open `http://localhost:5500/`.

### 3. Run the tests

```bash
cd backend
python -m pytest tests/ -v
```

## API endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health |
| GET | `/health` | Health check |
| GET | `/schemes` | List schemes (filters: `category`, `government_level`, `state`, `search`) |
| GET | `/schemes/{scheme_id}` | Scheme details |
| POST | `/profile` | Validate and store a user profile |
| GET | `/profile` | Get stored profile |
| DELETE | `/profile` | Clear stored profile |
| POST | `/match` | Evaluate profile against all schemes |
| POST | `/analyze` | Gap analysis |
| POST | `/simulate` | What-if simulation |
| GET | `/documents/{scheme_id}` | Required documents for a scheme |
| POST | `/documents/check` | Check document readiness |
| POST | `/compare` | Compare 2–5 schemes |

## Field mapping (frontend → backend)

The frontend uses different field names than the backend. `js/api.js` maps them:

| Frontend field | Backend field | Notes |
|---------------|---------------|-------|
| `age` | `age` | |
| `gender` | `gender` | |
| `state` | `state` | |
| `area` | `residential_status` | `rural`→`Rural`, `urban`→`Urban` |
| `income` | `annual_income` | |
| `category` | `category` | `general`→`OPEN`, `obc`→`OBC`, `sc`→`SC`, `st`→`ST`, `ews`→`EWS` |
| `occupation` | `occupation` | keys → display values |
| `education` | `education_level` | keys → display values |
| `landOwner` | `landholding_required` | `yes`/`no` → `true`/`false` |
| `ownsPuccaHouse` | `pucca_house_owned` | `yes`/`no` → `true`/`false` |

## Data source

The backend serves 12 verified government schemes (mostly Maharashtra state and central schemes) from `backend/data/schemes.json`. The frontend's local `js/data.js` contains an illustrative set of 15 schemes with simplified rules — it is used as a fallback when the backend is unavailable.

## Contributing

This is a hackathon prototype. Do not push to GitHub or merge into main without explicit authorization.