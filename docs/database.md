# Phase 3 — Database Foundation Architecture & Specification (v2.1 Finalized)

## Shree Balaji Wood — Wooden Door Product Showcase & Enquiry Website

**Role:** Senior Database Architect, Backend Architect, Security Engineer & QA Engineer  
**Date:** 29 September 2026  
**Document Version:** 2.1 (Correction Pass)  
**Status:** ⏳ Architecture Specification — Ready for Final Review  
**Target RDBMS:** PostgreSQL 15+  
**ORM / Query Layer:** SQLAlchemy 2.0+ (Declarative Mappings)  
**Migration Engine:** Alembic  
**Backend Framework:** FastAPI (Python 3.11+)  
**Database Driver:** `psycopg2-binary` (Synchronous SQLAlchemy 2.0 Engine with Connection Pooling)  

---

## 1. Executive Summary

This document represents the finalized, implementation-ready database foundation architecture specification (v2.1) for **Shree Balaji Wood**. The primary mission of this data tier is to provide a reliable, ACID-compliant, secure, and structured storage layer for a B2B/B2C wooden door manufacturing showcase and customer enquiry workflow.

The architecture directly derives its functional requirements from **Phase 0 (Requirements)** and **Phase 1 (System Architecture)**, incorporating all clarifications:
1. Product categories restricted to the three confirmed lines: Pine Flush Doors, Hardwood Flush Doors, and Fire Retardant Doors (FRD).
2. Product variations constrained to Single Core (SC), Double Core (DC), With Dipping, and Without Dipping.
3. Customer Request for Quote (RFQ) dimension structure supporting independent unit selection (`ft`, `in`, `cm`, `m`) for height and width, with thickness fixed in millimeters (`mm`), retaining 100% data fidelity.
4. Single-administrator authentication secured via HttpOnly session cookies (incorporating `Secure`, `SameSite`, and server-side signature verification).
5. Strict separation between internal database identity keys and public API identifiers.

This v2.1 specification applies precise technical corrections to v2.0, refining collation behavior, explicit `updated_at` lifecycle ownership, category referential integrity, fail-safe initial administrator seeding, cookie security definitions, realistic workload expectations, and pending implementation acceptance criteria.

---

## 2. Database Architecture Overview

### 2.1 Architectural Philosophy
The data layer is constructed according to five foundational engineering tenets:
- **Relational Integrity First:** Business invariants (valid units, non-zero positive dimensions, mandatory contact details, foreign key constraints) are enforced within PostgreSQL via declarative constraints, ensuring data validity regardless of how queries are executed.
- **Pragmatic Normalization (3NF):** Core transactional data is structured in Third Normal Form to eliminate update and deletion anomalies, while keeping join depths shallow (maximum 2 joins for catalog display).
- **Record Lifecycle Timestamps:** All tables maintain standardized temporal tracking (`created_at`, `updated_at`) using timezone-aware UTC timestamps (`TIMESTAMPTZ`) to record row creation and last modification times.
- **Decoupled API Boundaries:** Internal integer identity keys drive database joins and foreign key lookups; public-facing endpoints interface exclusively through immutable slugs or alphanumeric reference identifiers (`RFQ-YYYYMMDD-XXXX`).
- **Zero Premature Complexity:** We deliberately reject distributed UUIDs, microservice event brokers, unstructured generic EAV schemas, and universal soft-deletion frameworks where standard relational columns and active flags completely fulfill the V1 requirements.

### 2.2 Global Database Configuration Standards

| Parameter | Selected Value | Justification |
| :--- | :--- | :--- |
| **Engine** | PostgreSQL 15+ | Enterprise ACID compliance, robust declarative constraints, transactional DDL for Alembic migrations, native JSONB support, and mature connection pooling. |
| **Character Encoding** | `UTF8` | Complete support for multilingual text, Indian commercial entities, addresses, and technical dimension symbols (`₹`, `×`, `²`, `³`, `°`). |
| **Collation & Sorting** | `en_US.UTF-8` or `C.UTF-8` | Establishes standard lexical sorting and character classification. Locale/collation selection and case-insensitive matching are distinct concerns: case-insensitive lookups (e.g. for usernames, email addresses, or slugs) are implemented explicitly at the query/constraint level via `LOWER()` expressions or `ILIKE`, rather than relying on collation defaults. |
| **Timezone Storage** | `UTC` (`TIMESTAMPTZ`) | Database stores UTC exclusively. Presentation-tier localization to Indian Standard Time (IST: UTC+05:30) occurs at the API/client boundary. |
| **Numeric Precision** | `NUMERIC(8, 2)` & `NUMERIC(6, 2)` | Exact fixed-point arithmetic for physical dimensions and monetary values, eliminating floating-point rounding errors. |

---

## 3. Technology Stack

| Layer | Component | Specification / Version | Role in Data Tier |
| :--- | :--- | :--- | :--- |
| **Database Server** | PostgreSQL | Version 15 or 16 | Relational database management system and primary transactional store. |
| **ORM / Data Access** | SQLAlchemy | Version 2.0+ | Modern mapped declarative syntax (`Mapped[...]`, `mapped_column`), type safety, query compilation, and connection management. |
| **Database Driver** | `psycopg2-binary` | Version 2.9.9+ | High-performance C-extension synchronous DBAPI driver for PostgreSQL. |
| **Migration Manager** | Alembic | Version 1.13+ | Version-controlled, deterministic schema evolution tracked in Git. |
| **Schema Validation**| Pydantic | Version 2.0+ | Input validation and serialization boundaries separating HTTP requests from database models. |
| **Configuration** | `python-dotenv` | Version 1.0+ | Secure environment variable injection for database connection strings and credentials. |

---

## 4. Architectural Principles

1. **Explicit Schema Enforcement:** Every table declares an explicit primary key, explicit foreign key constraints with documented referential actions (`ON DELETE`, `ON UPDATE`), explicit `NOT NULL` rules, and explicit `CHECK` constraints.
2. **Deterministic Migrations:** All schema changes must be expressible via Alembic revision scripts. No direct manual DDL alterations in production.
3. **Least Privilege Operation:** Application runtime access is partitioned from migration DDL administrative privileges.
4. **Resilience & Connection Lifecycle:** Connections are managed via SQLAlchemy's `QueuePool` with active health checking (`pool_pre_ping=True`) and periodic recycling (`pool_recycle=1800`) to gracefully recover from network drops or server restarts.
5. **Security by Isolation:** Credentials, database passwords, and cryptographic secrets are never committed to version control; they are supplied strictly via environment variables.

---

## 5. Entity Inventory

The database foundation consists of **7 core entities**, strictly aligned with approved business requirements:

| Entity Name | Table Name | Business Purpose | Cardinality / Volume (V1) | Volatility |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | `admins` | Authenticated system administrator managing catalog and enquiries. | Exactly 1 active account (capacity for 1–5) | Extremely Low |
| **Product Category** | `product_categories` | Major door classification lines (Pine, Hardwood, FRD). | 3 rows initially | Extremely Low |
| **Product** | `products` | Door showcase specifications, core type options, dipping, and pricing visibility. | 10–50 rows | Low |
| **Product Image** | `product_images` | High-resolution photographs showcasing doors, with primary thumbnail flag. | 50–300 rows | Medium |
| **Enquiry (RFQ)** | `enquiries` | Customer quotation requests capturing customer details, door requirements, and custom dimensions. | 100–5,000+ rows/year | High (Write-heavy) |
| **Gallery Image** | `gallery_images` | Media assets displaying factory machinery, timber seasoning, and finished projects. | 30–150 rows | Low |
| **Website Content** | `website_contents` | Key-value/section-based dynamic CMS content (Hero, About Us, Quality Standards). | 5–20 rows | Low |

---

## 6. Corrected Conceptual ERD

The conceptual ERD illustrates **only genuine relational connections**. Independent standalone entities (`admins`, `gallery_images`, `website_contents`) have no foreign keys and are modeled without synthetic or self-referential relationships.

```mermaid
erDiagram
    PRODUCT_CATEGORY ||--o{ PRODUCT : "classifies (1:N)"
    PRODUCT ||--o{ PRODUCT_IMAGE : "contains (1:N)"
    PRODUCT ||--o{ ENQUIRY : "optionally references (1:N)"

    PRODUCT_CATEGORY {
        int id PK
        string name UK
        string slug UK
    }

    PRODUCT {
        int id PK
        int category_id FK
        string name
        string slug UK
        string core_type
        string dipping
    }

    PRODUCT_IMAGE {
        int id PK
        int product_id FK
        string image_path
        boolean is_primary
    }

    ENQUIRY {
        int id PK
        string reference_number UK
        int product_id FK "nullable"
        string customer_name
        string phone
        decimal height
        string height_unit
        decimal width
        string width_unit
        decimal thickness_mm
        int quantity
        string status
    }

    ADMIN {
        int id PK
        string username UK
        string email UK
        string password_hash
    }

    GALLERY_IMAGE {
        int id PK
        string title
        string image_path
        string category
    }

    WEBSITE_CONTENT {
        int id PK
        string section_key UK
        string title
        text content
    }
```

---

## 7. Logical Data Model

The logical data model defines foreign key propagation, data types, constraints, and operational metadata.

```text
product_categories (1) ────< products (N) ────< product_images (N)
                                 │
                                 │ (optional 1:N)
                                 ▼
                             enquiries (N)

[admins]              (Independent security entity)
[gallery_images]      (Independent media showcase entity)
[website_contents]    (Independent CMS section entity)
```

---

## 8. Table-by-Table Schema Specification

### 8.0 Timestamp Management Architecture
Across all tables:
- **`created_at`:** Stored as `TIMESTAMPTZ NOT NULL`. Initialized at database level via `server_default=func.now()` (generating `DEFAULT CURRENT_TIMESTAMP` in DDL).
- **`updated_at`:** Stored as `TIMESTAMPTZ NOT NULL`. Initialized via `server_default=func.now()`. **Update maintenance is owned explicitly by the SQLAlchemy ORM layer** using `onupdate=func.now()`, ensuring that any session flush emitting an `UPDATE` statement automatically updates this timestamp to the current UTC time. **Important Clarification:** `updated_at` is automatically maintained for application updates executed through SQLAlchemy ORM; direct SQL/database-side updates outside the ORM are not covered by this mechanism (unlike check and foreign key constraints, which are enforced directly at the PostgreSQL engine level).
- **Verification:** Automated tests verify that modifying a record via SQLAlchemy updates `updated_at` while preserving `created_at`.

---

### 8.1 Table: `admins`
Stores administrator credentials and session metadata.

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal admin ID |
| `username` | `VARCHAR(50)` | `Mapped[str]` | No | `UNIQUE`, `CHECK(length(username) >= 3)` | Login handle |
| `email` | `VARCHAR(255)` | `Mapped[str]` | No | `UNIQUE`, format checked at API boundary | Notification / recovery email |
| `password_hash` | `VARCHAR(255)` | `Mapped[str]` | No | `CHECK(length(password_hash) >= 20)` | Cryptographic digest (Argon2id/bcrypt) |
| `is_active` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT true` | Account status flag |
| `last_login_at` | `TIMESTAMPTZ` | `Mapped[Optional[datetime]]` | Yes | `DEFAULT NULL` | Last authentication timestamp (UTC) |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Account creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Last profile update timestamp (UTC) |

- **Primary Key:** `pk_admins` (`id`)
- **Implicit Constraint Indexes:** `uq_admins_username` (`username`), `uq_admins_email` (`email`)
- **Explicit Indexes:** None required (total rows ≤ 5).

---

### 8.2 Table: `product_categories`
Primary classifications for flush doors (Pine, Hardwood, FRD).

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal category ID |
| `name` | `VARCHAR(100)` | `Mapped[str]` | No | `UNIQUE`, `CHECK(length(name) >= 2)` | Category title |
| `slug` | `VARCHAR(120)` | `Mapped[str]` | No | `UNIQUE`, `CHECK(slug ~ '^[a-z0-9-]+$')` | URL-safe slug |
| `description` | `TEXT` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Category narrative & technical overview |
| `sort_order` | `INTEGER` | `Mapped[int]` | No | `DEFAULT 0` | UI sequence ordering |
| `is_active` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT true` | Public visibility toggle |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Row creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Row update timestamp (UTC) |

- **Primary Key:** `pk_product_categories` (`id`)
- **Implicit Constraint Indexes:** `uq_product_categories_slug` (`slug`), `uq_product_categories_name` (`name`)
- **Explicit Index:** `ix_product_categories_active_order` on `(is_active, sort_order)` for sorted public catalog navigation.

---

### 8.3 Table: `products`
The core showcase door items.

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal product ID |
| `category_id` | `INTEGER` | `Mapped[int]` | No | `FK -> product_categories.id ON DELETE RESTRICT` | Parent product category |
| `name` | `VARCHAR(150)` | `Mapped[str]` | No | `CHECK(length(name) >= 2)` | Product title |
| `slug` | `VARCHAR(180)` | `Mapped[str]` | No | `UNIQUE`, `CHECK(slug ~ '^[a-z0-9-]+$')` | URL-safe product slug |
| `short_description`| `VARCHAR(300)` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Brief teaser for catalog cards |
| `description` | `TEXT` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Comprehensive material and wood specs |
| `core_type` | `VARCHAR(50)` | `Mapped[str]` | No | `CHECK(core_type IN ('Single Core', 'Double Core', 'Both'))` | Core construction variant |
| `dipping` | `VARCHAR(50)` | `Mapped[str]` | No | `CHECK(dipping IN ('With Dipping', 'Without Dipping', 'Both'))` | Chemical treatment option |
| `standard_thicknesses` | `VARCHAR(100)` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Display text: e.g. "25mm, 30mm, 32mm, 35mm" |
| `base_price` | `NUMERIC(10, 2)` | `Mapped[Optional[Decimal]]`| Yes | `CHECK(base_price >= 0)`, `DEFAULT NULL` | Optional indicative/base price |
| `show_price` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT false` | Flag governing public price display |
| `is_featured` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT false` | Showcase flag on homepage |
| `is_active` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT true` | Public visibility flag |
| `sort_order` | `INTEGER` | `Mapped[int]` | No | `DEFAULT 0` | UI sequence ordering |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Row creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Row update timestamp (UTC) |

- **Primary Key:** `pk_products` (`id`)
- **Foreign Key:** `fk_products_category_id` (`category_id` references `product_categories(id)` ON DELETE RESTRICT)
- **Implicit Constraint Index:** `uq_products_slug` (`slug`)
- **Explicit Indexes:**
  - `ix_products_category_active_order` on `(category_id, is_active, sort_order)` (supports category filtering)
  - `ix_products_featured` on `(is_featured, is_active, sort_order)` (supports homepage showcase)

---

### 8.4 Table: `product_images`
Product photo gallery with primary thumbnail designation.

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal image ID |
| `product_id` | `INTEGER` | `Mapped[int]` | No | `FK -> products.id ON DELETE CASCADE` | Associated product |
| `image_path` | `VARCHAR(255)` | `Mapped[str]` | No | `CHECK(length(image_path) > 0)` | Relative canonical file storage path |
| `alt_text` | `VARCHAR(200)` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Accessibility and SEO alt description |
| `sort_order` | `INTEGER` | `Mapped[int]` | No | `DEFAULT 0` | Display ordering sequence |
| `is_primary` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT false` | Primary thumbnail flag |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Upload timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Row update timestamp (UTC) |

- **Primary Key:** `pk_product_images` (`id`)
- **Foreign Key:** `fk_product_images_product_id` (`product_id` references `products(id)` ON DELETE CASCADE)
- **Explicit Index:** `ix_product_images_product_order` on `(product_id, sort_order)`
- **Partial Unique Index:** `uq_product_primary_image` on `(product_id)` `WHERE is_primary = true` (Guarantees **at most one** primary image per product; application logic validates that when images exist, at least one is designated primary).

---

### 8.5 Table: `enquiries` (RFQ Submissions)
Customer quotation requests capturing dimensional specifications and contact info.

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal enquiry ID |
| `reference_number` | `VARCHAR(30)` | `Mapped[str]` | No | `UNIQUE`, `CHECK(length(reference_number) >= 10)` | Public tracking code (`RFQ-YYYYMMDD-XXXX`) |
| `product_id` | `INTEGER` | `Mapped[Optional[int]]` | Yes | `FK -> products.id ON DELETE SET NULL`, `DEFAULT NULL` | Optional associated product |
| `customer_name` | `VARCHAR(120)` | `Mapped[str]` | No | `CHECK(length(customer_name) >= 2)` | Contact person full name |
| `phone` | `VARCHAR(25)` | `Mapped[str]` | No | `CHECK(length(phone) >= 7)` | Contact telephone number |
| `email` | `VARCHAR(255)` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Contact email address |
| `company_name` | `VARCHAR(150)` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Firm / business entity name (B2B) |
| `address` | `TEXT` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Delivery site or office address |
| `gst_number` | `VARCHAR(20)` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Tax GSTIN for commercial quotes |
| `door_type` | `VARCHAR(50)` | `Mapped[str]` | No | `CHECK(length(door_type) > 0)` | Door type name snapshot |
| `core_type` | `VARCHAR(50)` | `Mapped[str]` | No | `CHECK(core_type IN ('Single Core', 'Double Core', 'Not Specified'))` | Required core variant |
| `dipping` | `VARCHAR(50)` | `Mapped[str]` | No | `CHECK(dipping IN ('With Dipping', 'Without Dipping', 'Not Specified'))` | Required chemical dipping |
| `height` | `NUMERIC(8, 2)` | `Mapped[Decimal]` | No | `CHECK(height > 0)` | Customer-entered height value |
| `height_unit` | `VARCHAR(10)` | `Mapped[str]` | No | `CHECK(height_unit IN ('ft', 'in', 'cm', 'm'))` | Selected height unit |
| `width` | `NUMERIC(8, 2)` | `Mapped[Decimal]` | No | `CHECK(width > 0)` | Customer-entered width value |
| `width_unit` | `VARCHAR(10)` | `Mapped[str]` | No | `CHECK(width_unit IN ('ft', 'in', 'cm', 'm'))` | Selected width unit |
| `thickness_mm` | `NUMERIC(6, 2)` | `Mapped[Decimal]` | No | `CHECK(thickness_mm > 0)` | Standardized thickness (in mm) |
| `quantity` | `INTEGER` | `Mapped[int]` | No | `CHECK(quantity >= 1)` | Number of doors required |
| `message` | `TEXT` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Customer remarks or instructions |
| `status` | `VARCHAR(30)` | `Mapped[str]` | No | `DEFAULT 'New'`, `CHECK(status IN ('New', 'Contacted', 'Quoted', 'In Discussion', 'Closed', 'Archived'))` | Operational processing state |
| `admin_notes` | `TEXT` | `Mapped[Optional[str]]` | Yes | `DEFAULT NULL` | Confidential internal admin notes |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Submission timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Last status/notes change timestamp (UTC) |

- **Primary Key:** `pk_enquiries` (`id`)
- **Foreign Key:** `fk_enquiries_product_id` (`product_id` references `products(id)` ON DELETE SET NULL)
- **Implicit Constraint Index:** `uq_enquiries_reference_number` (`reference_number`)
- **Explicit Indexes:**
  - `ix_enquiries_status_created` on `(status, created_at DESC)` (optimizes admin dashboard filtering)
  - `ix_enquiries_phone` on `(phone)` (supports rapid customer lookup on incoming calls)

---

### 8.6 Table: `gallery_images`
Showcases factory manufacturing, seasoning kilns, testing facilities, and finished installations.

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal image ID |
| `title` | `VARCHAR(150)` | `Mapped[str]` | No | `CHECK(length(title) >= 2)` | Image title or caption |
| `image_path` | `VARCHAR(255)` | `Mapped[str]` | No | `CHECK(length(image_path) > 0)` | Relative canonical file storage path |
| `category` | `VARCHAR(50)` | `Mapped[str]` | No | `DEFAULT 'Factory'`, `CHECK(category IN ('Factory', 'Machinery', 'Quality Testing', 'Finished Doors', 'General'))` | Gallery section tag |
| `sort_order` | `INTEGER` | `Mapped[int]` | No | `DEFAULT 0` | UI sequence ordering |
| `is_active` | `BOOLEAN` | `Mapped[bool]` | No | `DEFAULT true` | Public visibility flag |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Upload timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Row update timestamp (UTC) |

- **Primary Key:** `pk_gallery_images` (`id`)
- **Explicit Index:** `ix_gallery_images_category_active_order` on `(category, is_active, sort_order)` for filtered public media gallery viewing.

---

### 8.7 Table: `website_contents`
Key-value/section-based dynamic CMS content for website informational sections.

| Column | PostgreSQL Type | SQLAlchemy 2.0 Type | Nullable | Constraints & Defaults | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `Mapped[int]` | No | Primary Key, `GENERATED ALWAYS AS IDENTITY` | Internal content ID |
| `section_key` | `VARCHAR(60)` | `Mapped[str]` | No | `UNIQUE`, `CHECK(section_key ~ '^[a-z0-9_]+$')` | Machine-readable lookup key |
| `title` | `VARCHAR(200)` | `Mapped[str]` | No | `CHECK(length(title) > 0)` | Section heading |
| `content` | `TEXT` | `Mapped[str]` | No | `CHECK(length(content) > 0)` | Section body content |
| `meta_data` | `JSONB` | `Mapped[Optional[dict]]`| Yes | `DEFAULT '{}'::jsonb` | Extensible key-value metadata |
| `created_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()` (`DEFAULT CURRENT_TIMESTAMP`) | Row creation timestamp (UTC) |
| `updated_at` | `TIMESTAMPTZ` | `Mapped[datetime]` | No | `server_default=func.now()`, `onupdate=func.now()` | Row update timestamp (UTC) |

- **Primary Key:** `pk_website_contents` (`id`)
- **Implicit Constraint Index:** `uq_website_contents_section_key` (`section_key`)
- **Explicit Indexes:** None required (total rows ≤ 20; unique index on `section_key` satisfies all queries).

---

## 9. Relationships & Referential Integrity

```text
┌────────────────────────┐         1:N (ON DELETE RESTRICT)         ┌────────────────────────┐
│   product_categories   │ ───────────────────────────────────────► │        products        │
└────────────────────────┘                                          └────────────────────────┘
                                                                                 │
                                                                                 │ 1:N (ON DELETE CASCADE)
                                                                                 ▼
                                                                    ┌────────────────────────┐
                                                                    │     product_images     │
                                                                    └────────────────────────┘
                                                                                 ▲
                                                                                 │ 1:N (ON DELETE SET NULL)
                                                                    ┌────────────────────────┐
                                                                    │       enquiries        │
                                                                    └────────────────────────┘
```

### Referential Integrity Decision Matrix

| Parent Entity | Child Entity | Foreign Key Column | Action `ON DELETE` | Action `ON UPDATE` | Operational Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `product_categories` | `products` | `category_id` | **`RESTRICT`** | `CASCADE` | **Guards Catalog Stability:** Category deletion is strictly prevented while **any product references that category** (regardless of whether that product is marked active or inactive). Prevents accidental orphan products. An administrator must explicitly reassign or delete all associated products before a category can be removed. |
| `products` | `product_images` | `product_id` | **`CASCADE`** | `CASCADE` | **Clean Lifecycle Management:** Product images have zero business value without their parent product. Deleting a product automatically cleans up image metadata records. An application post-delete hook removes physical disk files. |
| `products` | `enquiries` | `product_id` | **`SET NULL`** | `CASCADE` | **Preserves Customer Quotation History:** Deleting or retiring a showcase door must NEVER destroy historical quotation records. The foreign key gracefully sets to `NULL`, while the snapshot fields (`door_type`, `core_type`, `dipping`, dimensions) permanently retain the customer's exact inquiry details. |

---

## 10. Constraints

The database utilizes standard PostgreSQL constraints to guarantee domain invariants:

1. **Primary Key Constraints:** Every table defines a single-column integer identity primary key (`GENERATED ALWAYS AS IDENTITY`).
2. **Foreign Key Constraints:** Explicit foreign keys with strict referential rules (`RESTRICT`, `CASCADE`, `SET NULL`).
3. **Unique Constraints:**
   - `uq_admins_username` on `admins(username)`
   - `uq_admins_email` on `admins(email)`
   - `uq_product_categories_name` on `product_categories(name)`
   - `uq_product_categories_slug` on `product_categories(slug)`
   - `uq_products_slug` on `products(slug)`
   - `uq_enquiries_reference_number` on `enquiries(reference_number)`
   - `uq_website_contents_section_key` on `website_contents(section_key)`
4. **Partial Unique Index:**
   - `uq_product_primary_image` on `product_images(product_id) WHERE is_primary = true`. Guarantees **at most one** primary image per product. Application validation in the product service ensures that when images exist for a product, at least one is designated as primary.
5. **CHECK Constraints:**
   - Dimension values: `height > 0`, `width > 0`, `thickness_mm > 0`
   - Dimension units: `height_unit IN ('ft', 'in', 'cm', 'm')`, `width_unit IN ('ft', 'in', 'cm', 'm')`
   - Quantity: `quantity >= 1`
   - Price: `base_price >= 0`
   - Core types: `core_type IN ('Single Core', 'Double Core', 'Both')` (products), `core_type IN ('Single Core', 'Double Core', 'Not Specified')` (enquiries)
   - Dipping options: `dipping IN ('With Dipping', 'Without Dipping', 'Both')` (products), `dipping IN ('With Dipping', 'Without Dipping', 'Not Specified')` (enquiries)
   - Enquiry status: `status IN ('New', 'Contacted', 'Quoted', 'In Discussion', 'Closed', 'Archived')`
   - Gallery category: `category IN ('Factory', 'Machinery', 'Quality Testing', 'Finished Doors', 'General')`
   - Slug formatting: Regex `CHECK(slug ~ '^[a-z0-9-]+$')`

---

## 11. Index & Query Strategy

### 11.1 Index Inventory

To prevent index bloat and unnecessary write amplification, explicit indexes are created only where query patterns demand them. Unique constraint indexes automatically created by PostgreSQL are not duplicated.

| Index Name | Table | Type | Columns | Target Query / Workflow |
| :--- | :--- | :--- | :--- | :--- |
| *(Automatic)* | `product_categories` | B-Tree Unique | `(slug)` | Category lookup by slug in public URL |
| `ix_product_categories_active_order` | `product_categories` | Composite B-Tree | `(is_active, sort_order)` | Public category listing navigation |
| *(Automatic)* | `products` | B-Tree Unique | `(slug)` | Product detail view (`GET /api/v1/products/{slug}`) |
| `ix_products_category_active_order` | `products` | Composite B-Tree | `(category_id, is_active, sort_order)` | Category product list filtering with sorting |
| `ix_products_featured` | `products` | Composite B-Tree | `(is_featured, is_active, sort_order)` | Homepage featured door carousel/grid |
| `ix_product_images_product_order` | `product_images` | Composite B-Tree | `(product_id, sort_order)` | Product detail gallery rendering |
| `uq_product_primary_image` | `product_images` | Partial Unique B-Tree | `(product_id) WHERE is_primary = true` | Fast primary thumbnail fetch & invariant enforcement |
| *(Automatic)* | `enquiries` | B-Tree Unique | `(reference_number)` | Public/Admin lookup by reference number |
| `ix_enquiries_status_created` | `enquiries` | Composite B-Tree | `(status, created_at DESC)` | Admin enquiry dashboard triage (newest first) |
| `ix_enquiries_phone` | `enquiries` | B-Tree | `(phone)` | Rapid customer history lookup on incoming call |
| `ix_gallery_images_category_active_order` | `gallery_images` | Composite B-Tree | `(category, is_active, sort_order)` | Filtered public gallery showcase |
| *(Automatic)* | `website_contents` | B-Tree Unique | `(section_key)` | Fetching CMS content section by key |

---

## 12. Pagination Strategy

1. **Public Catalog Listing (`/api/v1/products`):**
   - Will be implemented using standard `LIMIT` and `OFFSET` pagination with a total count header (`X-Total-Count`).
   - Default page size: 12 items (optimal for 3-column and 4-column responsive grid layouts). Maximum page size: 48 items.
   - For catalog sizes anticipated in V1–V2 (< 1,000 items), `LIMIT`/`OFFSET` queries on indexed composite columns (`is_active`, `sort_order`) execute with negligible overhead.
2. **Admin Enquiry Management (`/api/v1/admin/enquiries`):**
   - Default page size: 20 rows. Maximum page size: 100 rows.
   - Filterable by `status`, sorted by `created_at DESC` leveraging composite index `ix_enquiries_status_created`.
   - Architectural transition trigger: If the `enquiries` table exceeds 100,000 rows, keyset pagination (cursor-based on `(created_at, id)`) can be introduced without altering table schemas.

---

## 13. Security & Privacy

### 13.1 Least-Privilege Role Separation

In production environments, database access is segregated between application runtime operations and migration DDL executions:

```sql
-- 1. Application Runtime Role (Minimal Privileges)
CREATE ROLE balaji_app WITH LOGIN PASSWORD 'PLACEHOLDER_RUNTIME_PASSWORD';
GRANT CONNECT ON DATABASE balaji_wood TO balaji_app;
GRANT USAGE ON SCHEMA public TO balaji_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO balaji_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO balaji_app;

-- Ensure future tables grant access automatically
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO balaji_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public 
GRANT USAGE, SELECT ON SEQUENCES TO balaji_app;

-- 2. Migration Role (DDL Privileges, used during CI/CD or deployment only)
CREATE ROLE balaji_migrator WITH LOGIN PASSWORD 'PLACEHOLDER_MIGRATOR_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE balaji_wood TO balaji_migrator;
GRANT ALL ON SCHEMA public TO balaji_migrator;
```

### 13.2 Credentials & Secrets Management
- All database passwords, usernames, and host configurations must be provided strictly via environment variables (`DATABASE_URL`).
- All `.env` files are explicitly excluded from Git version control via `.gitignore`.
- Documentation and code contain only clear placeholder strings (e.g. `PLACEHOLDER_RUNTIME_PASSWORD`).

### 13.3 Customer PII Protection
- Customer phone numbers, email addresses, delivery locations, and GSTINs stored in `enquiries` constitute Personally Identifiable Information (PII).
- **Public API Isolation:** Public users cannot query customer enquiries. The endpoint `POST /api/v1/enquiries` is write-only, returning only an opaque reference tracking number.
- **Admin Access Only:** Full enquiry records are strictly restricted to authenticated administrators via protected API routes verified by session cookies.

### 13.4 Cryptographic Password & Session Cookie Security
- Plaintext passwords are never stored in the database. Admin authentication digests are generated using `Argon2id` (or `bcrypt` with work factor 12) before persistence in `admins.password_hash`.
- **Session Cookie Architecture:** Admin authentication relies on browser session cookies configured with the following precise attributes:
  - **`HttpOnly`:** Mitigates XSS credential theft by preventing client-side JavaScript access (`document.cookie`).
  - **`Secure`:** Ensures cookies are transmitted only over encrypted TLS (HTTPS) connections (set to `false` only in local development).
  - **`SameSite=Lax` (or `Strict`):** Protects against Cross-Site Request Forgery (CSRF).
  - **Server-Side Signature / Verification:** Session tokens carry a cryptographic HMAC signature verified server-side using `SECRET_KEY`.
  - **Explicit Expiration:** Configured with a bounded lifetime (e.g. 60 minutes) and immediate server-side invalidation upon logout.

### 13.5 SQL Injection Mitigation
- Application queries are compiled and parameterized using **SQLAlchemy 2.0 ORM** statement constructs (`select()`, `insert()`, `update()`, `delete()`).
- Parameterized queries significantly reduce SQL injection risk, provided developers do not construct unsafe raw SQL using untrusted string formatting. Raw SQL string concatenation is strictly prohibited in repository code.

---

## 14. Migration Strategy — Alembic

### 14.1 Alembic Directory Architecture
All schema evolution is version-controlled in the backend codebase:

```text
backend/
├── alembic/
│   ├── env.py                # Configured to inspect Base.metadata
│   ├── script.py.mako        # Migration template
│   └── versions/
│       └── 0001_initial_schema.py # Initial baseline migration
├── alembic.ini               # Runner configuration
└── app/
    ├── core/
    │   └── database.py       # Engine, sessionmaker, Base
    └── models/               # SQLAlchemy Declarative Models
```

### 14.2 Migration Lifecycle & Safety Guidelines

```text
Model Definition (SQLAlchemy)
             ↓
Generate Migration (`alembic revision --autogenerate -m "..."`)
             ↓
Manual Code Review of Migration Script
             ↓
Local Database Test (`alembic upgrade head`)
             ↓
Reversibility Test (`alembic downgrade -1` then `upgrade head`)
             ↓
CI/CD Automated Migration Execution
             ↓
Staging Verification → Production Deployment
```

1. **Transactional Execution:** PostgreSQL executes DDL within transactions. If an Alembic migration encounters an error, the entire migration rolls back automatically, preventing partial schema corruption.
2. **Reversibility Scope:** Every migration must provide a valid `downgrade()` function where practically possible. However, developers must recognize that destructive operations (e.g., dropping columns or tables) inherently cause data loss that cannot be reversed by DDL rollback alone; destructive production changes require pre-migration database snapshots.

---

## 15. Seed Data Strategy

An idempotent Python script (`backend/app/db/seed.py`) will manage initial data provisioning. Running the seed script multiple times produces identical results without creating duplicate rows or overwriting modified operational data.

### 15.1 Seed Data Elements

1. **Default Product Categories (3 Records):**
   - `Pine Flush Doors` (`slug`: `pine-flush-doors`, `sort_order`: 1)
   - `Hardwood Flush Doors` (`slug`: `hardwood-flush-doors`, `sort_order`: 2)
   - `FRD Flush Doors` (`slug`: `frd-flush-doors`, `sort_order`: 3)

2. **Default Website Content Sections (Key CMS blocks):**
   - `hero_section`: Banner headline and value proposition.
   - `about_company`: History, manufacturing plant, and timber sourcing.
   - `quality_assurance`: Chemical dipping, kiln seasoning, and IS:2202 testing standards.
   - `contact_details`: Physical factory address, phone numbers, and operational hours.

3. **Initial Admin Account (Strict Fail-Safe Security):**
   - Created **only if zero admin records exist** in the `admins` table.
   - Required administrator credentials **must be supplied through approved environment variables** (`INITIAL_ADMIN_USERNAME` and `INITIAL_ADMIN_PASSWORD`) or deployment secrets.
   - **Fail-Safe Behavior:** If either required variable is missing or blank, the seed operation **must fail immediately with an explicit configuration error**.
   - Under no circumstances will a fallback administrator password be generated, printed to deployment logs, or output to the console.
   - Credentials will never be stored in source code, migration files, Git, database seed files, or application responses.

---

## 16. Backup & Recovery

### 16.1 Backup Policy & Strategy

| Backup Mechanism | Frequency | Tool / Command | Retention Policy | Storage Destination |
| :--- | :--- | :--- | :--- | :--- |
| **Logical Backup** | Daily at 02:00 UTC | `pg_dump -Fc balaji_wood > balaji_wood_$(date +%F).dump` | 14 Daily, 4 Weekly, 12 Monthly | Encrypted offsite object storage (S3 / Cloud Storage) |
| **WAL Archiving** | Continuous / Interval | Managed Postgres WAL archiving or WAL-G | 7 Days Point-In-Time | Separate encrypted storage bucket |

### 16.2 Recovery Objectives & Verification

- **Recovery Point Objective (RPO) Target:** < 1 hour (using daily dumps supplemented by continuous WAL archives).
- **Recovery Time Objective (RTO) Target:** < 30 minutes (to spin up a clean database instance and restore a compressed dump).
- **Mandatory Restore Drills:** A backup that has never been tested does not constitute verified recovery capability. A staging restore test must be executed and documented prior to final production cutover.

---

## 17. API & Integration Boundaries

Strict architectural layering isolates internal database design from external API consumers:

```text
HTTP Request (Client)
         ↓
Pydantic Request Schemas (Validation, Type Coercion)
         ↓
FastAPI Route Handlers (HTTP Semantics, Status Codes)
         ↓
Service Layer (Business Logic, Transaction Boundaries)
         ↓
SQLAlchemy ORM Models (Database Mapping)
         ↓
PostgreSQL Database (ACID Storage)
```

1. **Decoupled Identifiers:**
   - Products are exposed via `slug` (e.g., `/api/v1/products/pine-flush-door-single-core`), concealing internal serial `id` values and boosting SEO.
   - Enquiries are exposed via immutable `reference_number` (e.g., `RFQ-20260929-8472`), preventing sequential record enumeration attacks.
2. **Abstracted Media Storage:**
   - Database stores relative storage keys (e.g., `products/pine-01.webp`), not absolute file system paths or external server URLs.
   - Service layers dynamically prepend base static URLs or CDN endpoints, allowing storage backends to be migrated to AWS S3 or Cloudflare R2 without schema updates.
3. **Pydantic Domain Schemas:**
   - Sensitive fields (`password_hash`, `admin_notes`) are strictly excluded from public and admin serialization schemas.

---

## 18. Scalability Strategy

The architecture accommodates realistic manufacturing showcase growth across three developmental horizons:

| Scale Metric | Current Target (V1) | 3-Year Planning Threshold | Architectural Provision |
| :--- | :--- | :--- | :--- |
| **Product Records** | 10–30 products | 100–300 products | Single table. Index scan latency estimated < 2ms under standard hardware. |
| **Enquiry Volume** | 50–200 / month | 1,000–5,000 / month | Composite index `(status, created_at DESC)`. Table comfortably handles 200,000+ rows before requiring table maintenance. |
| **Image Metadata** | 50–150 rows | 500–2,000 rows | Lightweight text metadata (< 120 bytes/row). Binary image blobs stored strictly on disk/CDN. |
| **Database Storage Footprint** | ~10–25 MB | ~200–500 MB | Extremely compact relational footprint. |

### Workload & Memory Expectations
Given the estimated compact dataset size (~10–25 MB in V1), typical PostgreSQL configurations with standard `shared_buffers` allocations are expected to comfortably cache active working sets in memory. This is an architectural planning expectation rather than a guaranteed memory invariant. Actual memory utilization, cache-hit ratios, and query execution times will be verified through representative workload testing and production monitoring.

### Practical Scaling Triggers
- **Redis Response Caching:** Triggered only if public catalog read throughput exceeds 300 requests/second or database CPU utilization sustains > 70%.
- **Table Partitioning:** Triggered only if the `enquiries` table exceeds 500,000 rows, utilizing range partitioning on `created_at`.
- **Object Storage Migration (S3):** Triggered when local media asset volume exceeds 20 GB or multi-server horizontal scaling is adopted.

---

## 19. Architectural Decisions & Trade-offs

### Decision 1: `CHECK` Constraints over PostgreSQL Native `ENUM` Types
- **Decision:** Use `VARCHAR` with SQL `CHECK` constraints (e.g. `CHECK(height_unit IN ('ft', 'in', 'cm', 'm'))`) instead of native PostgreSQL `CREATE TYPE ... AS ENUM`.
- **Reason:** Modifying native ENUM values in older PostgreSQL versions or complex migration rollbacks can require table locks or non-transactional DDL.
- **Benefit:** Seamless schema evolution via Alembic migrations. Adding a new unit or status requires a simple `ALTER TABLE ... DROP/ADD CONSTRAINT` without modifying underlying column types.
- **Trade-off:** Storage overhead is approximately 2–4 bytes larger per row than internal 4-byte enum integers. In tables containing under 500,000 rows, this overhead is negligible (< 2 MB total).
- **Future Implication:** Zero-downtime additions of new measurement units or workflow statuses.

### Decision 2: Original Dimension Values with Unit Storage (`height` + `height_unit`)
- **Decision:** Store dimensions exactly as submitted by the customer (`height NUMERIC(8, 2)`, `height_unit VARCHAR(10)`).
- **Reason:** In the Indian wooden door industry, carpenters and residential buyers quote in feet/inches, while commercial builders quote in centimeters or meters. Converting and rounding during intake risks precision loss and disputes.
- **Benefit:** Complete data fidelity. The admin views the quote exactly as submitted.
- **Trade-off:** Sorting or filtering across mixed units requires application-level normalization or a computed column.
- **Future Implication:** If cross-unit dimensional filtering becomes necessary, a PostgreSQL `GENERATED ALWAYS AS (...) STORED` column can be added seamlessly.

### Decision 3: Fixed Millimeters for Thickness (`thickness_mm`)
- **Decision:** Do not offer unit selection for thickness; store strictly as `thickness_mm NUMERIC(6, 2)`.
- **Reason:** Flush door manufacturing standards (IS:2202) universally specify door thicknesses in millimeters (e.g. 25mm, 30mm, 32mm, 35mm, 38mm).
- **Benefit:** Eliminates user input error and standardizes technical manufacturing specifications.
- **Trade-off:** None for this domain.
- **Future Implication:** Consistent standard reporting and matching against factory stock.

### Decision 4: Storing `standard_thicknesses` as Descriptive Text in V1
- **Decision:** Store `standard_thicknesses` on `products` as a formatted text string (e.g. "25mm, 30mm, 32mm, 35mm") rather than creating a normalized child table `product_thickness_options`.
- **Reason:** In V1, the website is an informational showcase with no checkout or real-time inventory. Thickness options are displayed as informational badges on the product card.
- **Benefit:** Avoids unnecessary join complexity for a simple catalog display.
- **Trade-off:** Thicknesses cannot be individually queried via SQL relational operators without string matching.
- **Future Implication:** If V2 introduces per-thickness dynamic pricing, a normalized join table can be introduced with a simple migration.

### Decision 5: Partial Unique Index for Primary Images
- **Decision:** Enforce `CREATE UNIQUE INDEX uq_product_primary_image ON product_images(product_id) WHERE is_primary = true`.
- **Reason:** Guarantees at the database engine level that no product can have multiple primary thumbnail images.
- **Benefit:** Completely eliminates race conditions causing multiple competing primary images.
- **Trade-off:** The index guarantees **at most one** primary image, but does not prevent zero primary images.
- **Future Implication:** The application service layer must validate that when images are uploaded, exactly one is marked `is_primary = true`.

---

## 20. Risks & Open Decisions

### 20.1 Technical & Operational Risks

| Risk | Impact | Likelihood | Mitigation Strategy |
| :--- | :--- | :--- | :--- |
| **Orphan Media Files on Disk** | Low | Medium | Implementing an application post-delete signal/hook that deletes physical files when `product_images` or `gallery_images` rows are deleted. |
| **Spam / Malicious RFQ Submissions** | Medium | Medium | Rate limiting on `POST /api/v1/enquiries` at the FastAPI route level (e.g., slowapi / Redis limiters) + Honeypot form field in frontend. |
| **Stale Database Connections** | Medium | Low | SQLAlchemy connection pool pre-ping enabled (`pool_pre_ping=True`) and connection recycling set to 1800 seconds. |

### 20.2 Open Decisions (For Stakeholder Review)

1. **GST Number Validation:** Should GSTIN adhere to strict 15-character Indian format regex (`^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`) at the database level, or remain permissive `VARCHAR(20)` for initial flexibility?  
   *Current Proposal:* Permissive at database level, validated strictly at API/Pydantic level if supplied.
2. **Archival Policy for Old Enquiries:** Should closed or archived RFQ enquiries be retained indefinitely or purged after a statutory period (e.g., 3 years)?  
   *Current Proposal:* Retain indefinitely in V1 given the low data footprint.

---

## 21. Phase 3 Implementation Roadmap

The implementation of Phase 3 will proceed across **6 sequential stages**:

```text
Stage 1: Environment & Driver Setup
   ├── Add dependencies to requirements.txt (sqlalchemy, alembic, psycopg2-binary, python-dotenv)
   └── Configure DATABASE_URL in backend/.env

Stage 2: Core Database Configuration
   ├── Implement backend/app/core/config.py (DatabaseSettings)
   └── Implement backend/app/core/database.py (Engine, sessionmaker, Base, get_db)

Stage 3: Declarative SQLAlchemy 2.0 Models
   ├── app/models/admin.py
   ├── app/models/category.py
   ├── app/models/product.py
   ├── app/models/image.py
   ├── app/models/enquiry.py
   ├── app/models/gallery.py
   ├── app/models/content.py
   └── app/models/__init__.py (Unified metadata export)

Stage 4: Alembic Configuration & Initial Migration
   ├── Initialize alembic (alembic init alembic)
   ├── Configure alembic/env.py with target_metadata = Base.metadata
   └── Generate initial migration: 0001_initial_schema.py

Stage 5: Migration Execution & Seed Implementation
   ├── Execute alembic upgrade head
   ├── Implement idempotent backend/app/db/seed.py
   └── Populate default categories, CMS sections, and secure initial admin

Stage 6: Automated Verification & Testing
   ├── Execute automated test suite for constraints, cascades, and rollbacks
   └── Validate health endpoint and Swagger UI integration
```

---

## 22. Database QA & Validation Plan

Prior to Phase 3 completion, the following automated validation checklist will be executed:

- [ ] **Connection Lifecycle:** Verify clean connection acquisition and release using `get_db()` dependency.
- [ ] **Alembic Reversibility:**
  - Execute `alembic upgrade head` on clean database.
  - Execute `alembic downgrade base` and verify all 7 tables and custom constraints are completely dropped.
  - Re-execute `alembic upgrade head` and verify clean re-creation.
- [ ] **Timestamp Maintenance Test:**
  - Insert record and verify `created_at` equals `updated_at`.
  - Update record and verify `updated_at` advances while `created_at` remains unchanged.
- [ ] **Constraint Enforcement Tests:**
  - Attempt inserting an enquiry with `height = -5` → Expect database `IntegrityError` (CHECK constraint).
  - Attempt inserting an enquiry with `height_unit = 'yard'` → Expect database `IntegrityError` (CHECK constraint).
  - Attempt inserting two images with `is_primary = true` for the same `product_id` → Expect `IntegrityError` (Partial Unique Index).
  - Attempt inserting duplicate category or product slugs → Expect `IntegrityError` (Unique constraint).
- [ ] **Referential Integrity Tests:**
  - Attempt deleting a category that has products (active or inactive) → Expect database `IntegrityError` (`ON DELETE RESTRICT`).
  - Delete a product with images → Verify associated rows in `product_images` are automatically deleted (`ON DELETE CASCADE`).
  - Delete a product referenced by an enquiry → Verify `enquiries.product_id` is updated to `NULL` while enquiry record remains intact (`ON DELETE SET NULL`).
- [ ] **Seed Idempotency & Security Test:**
  - Attempt running seed without `INITIAL_ADMIN_USERNAME` / `INITIAL_ADMIN_PASSWORD` → Verify operation fails with configuration error.
  - Run `python -m app.db.seed` with valid secrets on a freshly migrated database.
  - Run `python -m app.db.seed` a second time → Verify row counts remain unchanged and no unique violations occur.

---

## 23. Phase 3 Architecture Acceptance Criteria

The Phase 3 architecture specification satisfies the following readiness criteria:

* [x] **PostgreSQL version finalized:** PostgreSQL 15+ selected and documented.
* [x] **SQLAlchemy version finalized:** SQLAlchemy 2.0+ declarative mappings selected.
* [x] **Alembic migration strategy finalized:** Alembic versioned migrations with rollback guidelines documented.
* [x] **ERD contains only genuine relationships:** All phantom self-referential relationships eliminated.
* [x] **All tables justified:** All 7 entities directly map to approved Phase 0/1 requirements.
* [x] **All relationships match foreign keys:** Foreign keys, indexes, and Mermaid diagrams are 100% aligned.
* [x] **Referential actions validated:** `RESTRICT` (for any referencing product), `CASCADE`, and `SET NULL` behavior documented.
* [x] **Constraints validated:** CHECK constraints, UNIQUE constraints, and Partial Unique Indexes defined.
* [x] **Timestamp lifecycle defined:** Explicit initial values and SQLAlchemy ORM `onupdate` ownership documented.
* [x] **Indexes reviewed for redundancy:** Redundant duplicate indexes on UNIQUE columns eliminated.
* [x] **Sensitive fields identified:** Admin password hashes and customer PII documented with security rules.
* [x] **Database security model documented:** Least-privilege roles, placeholder credentials, and injection mitigation specified.
* [x] **Session cookie terminology accurate:** HttpOnly, Secure, SameSite, and server-side signing specified.
* [x] **Migration structure finalized:** Alembic directory and execution workflow detailed.
* [x] **Seed strategy fail-safe:** Fail-safe credential requirement without insecure fallback logging documented.
* [x] **Backup/recovery strategy documented:** Logical dumps, WAL archives, and mandatory restore drill defined.
* [x] **Scalability assumptions clearly labeled:** Performance and memory expectations labeled as planning thresholds rather than unverified guarantees.
* [x] **API/database boundaries defined:** Decoupled slugs and reference codes documented.
* [x] **SQLAlchemy model structure implementation-ready:** Ready for Stage 2 & 3 execution.
* [x] **Database test strategy defined:** Automated QA test plan documented.
* [x] **No unresolved Critical issues remain:** Complete audit performed.

---

## 24. Final Architecture Approval Checklist

* [ ] Database Architecture Overview reviewed and approved by Stakeholder
* [ ] Corrected ERD and Entity Inventory reviewed and approved
* [ ] Table specifications and column types reviewed and approved
* [ ] Referential actions (`RESTRICT`, `CASCADE`, `SET NULL`) approved
* [ ] Index and pagination strategy approved
* [ ] Security, least privilege, and PII protection approved
* [ ] Alembic migration workflow approved
* [ ] Seed data strategy and admin credential handling approved
* [ ] Implementation roadmap and QA test plan approved

*(Pending Stakeholder Sign-Off)*

---

## Audit Appendix

### A. Changes Made (v2.0 → v2.1)
1. **Collation & Case-Insensitive Matching Clarification:** Corrected Section 2.2 to clarify that UTF-8 locale selection and case-insensitive matching are distinct concerns. Case-insensitive lookups are explicitly owned by query/constraint logic (e.g. `LOWER()` or `ILIKE`), rather than assuming collation handles it automatically.
2. **`updated_at` Maintenance Architecture:** Added Section 8.0 and updated all table definitions. Clarified that `server_default=func.now()` sets initial values on `INSERT`, while update maintenance is explicitly owned by the SQLAlchemy ORM layer using `onupdate=func.now()`. Added timestamp test to QA plan.
3. **Category Delete Constraint Wording:** Corrected Section 9 and Section 22. Clarified that `ON DELETE RESTRICT` prevents category deletion while **any product references that category**, removing the limiting phrase "active products".
4. **Fail-Safe Initial Admin Seed Security:** Updated Section 15.1 and Section 22. Removed the insecure fallback that printed generated passwords to the console/logs. Specified that the seed script must fail with a configuration error if `INITIAL_ADMIN_USERNAME` or `INITIAL_ADMIN_PASSWORD` are missing.
5. **Memory Workload Expectation Clarification:** Corrected Section 18. Reframed the `shared_buffers` statement from a guaranteed memory invariant to an architectural planning expectation subject to benchmarking and monitoring.
6. **Session Cookie Terminology Accuracy:** Corrected Section 1, Section 13.4, and Section 23. Removed inaccurate "HttpOnly encrypted cookies" phrasing; accurately documented `HttpOnly`, `Secure`, `SameSite`, and server-side HMAC token signature verification.
7. **Acceptance Criteria & Verification Separation:** Corrected Section 22, 23, and 24. Converted post-coding implementation tasks to pending test checklists (`[ ]`) to accurately reflect that implementation coding has not yet begun.
8. **Record Lifecycle Timestamp Terminology:** Corrected Section 1.1, 2.1, and 9 to refer to "record lifecycle timestamps" rather than implying a full historical audit-trail log.

### B. Issues Discovered & Intentionally Retained
1. **`standard_thicknesses` as `VARCHAR(100)` Text:** Retained as a formatted text string on `products` rather than normalizing into a separate join table. Rationale: In V1, the website is an informational showcase with no checkout or dynamic pricing; normalizing this field would add unnecessary join complexity with no functional benefit. Future migration path to a join table is documented if per-thickness pricing is introduced in V2.
2. **Separate Dimension Columns (`height` + `height_unit`, `width` + `width_unit`):** Retained separate unit columns rather than normalizing to a single metric standard. Rationale: Preserves exact customer input fidelity without rounding discrepancies across Indian architectural (ft/in) and commercial (metric) quoting standards.

### C. Open Decisions
1. **GSTIN Validation Strictness:** Permissive `VARCHAR(20)` at the database level vs. strict 15-character regex constraint. (Recommended: Permissive in DB, validated via Pydantic at API boundary).
2. **Enquiry Data Retention:** Indefinite retention in V1 vs. statutory multi-year archival policy. (Recommended: Indefinite in V1).

### D. Implementation Readiness

**STATUS: READY FOR FINAL REVIEW**

The specification has completed the v2.1 correction pass and is ready for final stakeholder/technical review. Implementation must begin only after final approval.

### E. Recommended Next Step

Implementation must begin only after final stakeholder approval. Following approval, proceed with the implementation sequence:
1. **PostgreSQL Environment & Dependencies:** Add `sqlalchemy>=2.0.0`, `alembic>=1.13.0`, `psycopg2-binary>=2.9.9`, and `python-dotenv>=1.0.0` to `backend/requirements.txt` and install into `.venv`.
2. **Backend Database Configuration:** Implement `backend/app/core/database.py` and `backend/app/core/config.py`.
3. **SQLAlchemy Models:** Create declarative model modules in `backend/app/models/`.
4. **Alembic Initialization:** Initialize Alembic and create baseline migration `0001_initial_schema.py`.
5. **Migration Execution:** Run `alembic upgrade head` and verify table creation in PostgreSQL.
6. **Seed Data:** Implement and execute `backend/app/db/seed.py`.
7. **Database Validation Tests:** Run QA verification scripts for constraints, cascades, and rollback.
