# Architecture — Shree Balaji Wood

## Approved Architecture

The system architecture was defined and approved in **Phase 1 — Project Architecture**.

### System Overview

```text
┌─────────────────┐     HTTP REST API     ┌─────────────────┐     SQLAlchemy ORM     ┌─────────────────┐
│   React + TS    │ ──────────────────►   │    FastAPI       │ ──────────────────►   │   PostgreSQL    │
│   Vite          │ ◄──────────────────   │    (Python)      │ ◄──────────────────   │   Database      │
│   Tailwind v4   │      JSON             │                  │                       │                 │
└─────────────────┘                       └─────────────────┘                       └─────────────────┘
     Frontend                                  Backend                                  Data Layer
```

### Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite |
| Styling | Tailwind CSS v4 |
| Backend | Python + FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0+ |
| Migrations | Alembic |
| API Docs | OpenAPI / Swagger (built into FastAPI) |
| Version Control | Git |
| Configuration | `.env` files |

### Authentication

- Single admin user
- Admin Authentication (HttpOnly Secure Cookie)
- Credentials never stored in localStorage or sessionStorage
- Password hashing with bcrypt

### API Design

- Base URL: `/api/v1/`
- Public endpoints: Products, Gallery, Enquiries, Content
- Admin endpoints: Protected via HttpOnly cookie authentication
- Response format: JSON

### Image Storage

- Local filesystem storage (`backend/uploads/`) for V1
- Clean service abstraction for future cloud migration

---

**Phase 1 Status:** ✅ Approved (28 September 2026)
