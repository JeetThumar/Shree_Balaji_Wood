# Shree Balaji Wood

Product showcase and enquiry website for Shree Balaji Wood — a wood manufacturing business specializing in flush door production.

## About

This website allows customers to browse flush door products (Pine, Hardwood, FRD), view product details with images, and submit enquiries (Request for Quote) with door specifications. It is **not an e-commerce platform** — pricing and orders are handled directly with the business.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite |
| Styling | Tailwind CSS v4 |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0+ |
| Migrations | Alembic |

## Project Structure

```text
Balaji Wood/
├── frontend/          # React + Vite + TypeScript application
├── backend/           # FastAPI Python application
├── docs/              # Project documentation
├── tests/             # Test files
├── .gitignore
└── README.md
```

## Local Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL (required from Phase 3 onwards)

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs at `http://localhost:5173`.

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The backend server runs at `http://localhost:8000`.

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Environment Configuration

Copy the `.env.example` files and update values as needed:

```bash
# Frontend
cp frontend/.env.example frontend/.env

# Backend
cp backend/.env.example backend/.env
```

## Current Phase

**Phase 2 — Folder Structure & Project Foundation** (In Progress)

See `docs/development-progress.md` for detailed phase tracking.
