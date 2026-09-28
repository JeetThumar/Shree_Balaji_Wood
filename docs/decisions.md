# Architectural Decisions — Shree Balaji Wood

This document records important architectural and implementation decisions made during the project.

---

## Decision 001 — Technology Stack

**Date:** 28 September 2026  
**Phase:** Phase 0 / Phase 1  
**Decision:** Use React + TypeScript + Vite for frontend, FastAPI + Python for backend, PostgreSQL for database.  
**Rationale:** Modern, well-supported stack. Simple enough to understand and maintain while providing a solid foundation for production use.

---

## Decision 002 — Tailwind CSS v4

**Date:** 28 September 2026  
**Phase:** Phase 1 / Phase 2  
**Decision:** Use Tailwind CSS v4 with the `@tailwindcss/vite` plugin.  
**Rationale:** Tailwind v4 uses a modern Vite plugin approach. No `tailwind.config.js` required. CSS import via `@import "tailwindcss"` is the standard v4 method.

---

## Decision 003 — Admin Authentication (HttpOnly Secure Cookie)

**Date:** 28 September 2026  
**Phase:** Phase 1  
**Decision:** Use secure HttpOnly cookies for admin authentication instead of storing JWT tokens in localStorage.  
**Rationale:** HttpOnly cookies are not accessible to JavaScript, reducing XSS attack surface. The browser automatically includes the cookie with requests.

---

## Decision 004 — Minimal Phase 2 Foundation

**Date:** 28 September 2026  
**Phase:** Phase 2  
**Decision:** Install only FastAPI and Uvicorn as backend dependencies. Do not pre-install SQLAlchemy, Alembic, auth libraries, or other future dependencies.  
**Rationale:** Keep the dependency tree minimal. Each dependency is added when its phase requires it, avoiding unused packages and version conflicts.

---

## Decision 005 — Alembic Deferred to Phase 3

**Date:** 28 September 2026  
**Phase:** Phase 2  
**Decision:** Do not create Alembic directory or configuration in Phase 2.  
**Rationale:** Alembic requires a database connection and models to be meaningful. Creating it now would result in non-functional placeholder configuration. It will be properly configured alongside the database in Phase 3.

---

## Decision 006 — No Business Logic in Phase 2

**Date:** 28 September 2026  
**Phase:** Phase 2  
**Decision:** Phase 2 contains only project structure, minimal placeholder content, and a health check endpoint. No product APIs, enquiry forms, admin features, or database operations.  
**Rationale:** Strict phase separation ensures each phase is independently verifiable and avoids premature implementation of unreviewed features.

---

## Decision 007 — Frontend Dependencies Minimal

**Date:** 28 September 2026  
**Phase:** Phase 2  
**Decision:** Do not install React Router, Axios, or other libraries in Phase 2. Only React, TypeScript, Vite, and Tailwind CSS v4 are installed.  
**Rationale:** These libraries will be added when routing and API integration are actually implemented in later phases. Installing them now provides no benefit and adds unused code.
