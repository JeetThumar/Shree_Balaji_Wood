# API Documentation — Shree Balaji Wood

API implementation will begin in **Phase 4 — Backend Foundation**.

## Foundation Endpoint (Phase 2)

The following endpoint exists as part of the Phase 2 project foundation:

### Health Check

```
GET /health
```

**Response:**

```json
{
  "status": "ok"
}
```

This endpoint verifies that the backend is running. It has no business logic.

## Planned API Structure

The following API structure was approved in Phase 1:

### Public Endpoints (Phase 4+)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `GET` | `/api/v1/products` | List all products |
| `GET` | `/api/v1/products/{id}` | Get product details |
| `GET` | `/api/v1/gallery` | Get gallery images |
| `POST` | `/api/v1/enquiries` | Submit a door requirement / RFQ |
| `GET` | `/api/v1/content/{section}` | Get website content |

### Admin Endpoints (Phase 7)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/api/v1/admin/auth/login` | Admin login → secure auth cookie |
| `GET` | `/api/v1/admin/dashboard` | Dashboard stats |
| `GET/POST/PUT/DELETE` | `/api/v1/admin/products` | Product CRUD |
| `POST/DELETE` | `/api/v1/admin/products/{id}/images` | Product image management |
| `GET/POST/DELETE` | `/api/v1/admin/gallery` | Gallery CRUD |
| `GET/PUT` | `/api/v1/admin/enquiries` | View and update enquiry status |
| `GET/PUT` | `/api/v1/admin/content` | Website content management |

These endpoints will be documented in detail as they are implemented.

## Interactive API Documentation

FastAPI provides interactive documentation automatically:

| Tool | URL |
|------|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |

---

**Phase 4 Status:** ⬜ Not Started
