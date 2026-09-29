import os
import sys
from pathlib import Path
import bcrypt
from sqlalchemy import select
from sqlalchemy.orm import Session

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.models.admin import Admin
from app.models.category import ProductCategory
from app.models.content import WebsiteContent

DEFAULT_CATEGORIES = [
    {
        "name": "Pine Flush Doors",
        "slug": "pine-flush-doors",
        "description": "High-grade imported pine timber flush doors offering superior stability, smooth surface finish, and high dimensional accuracy.",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "name": "Hardwood Flush Doors",
        "slug": "hardwood-flush-doors",
        "description": "Robust, high-density hardwood flush doors designed for maximum structural strength, longevity, and impact resistance.",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "name": "FRD Flush Doors",
        "slug": "frd-flush-doors",
        "description": "Fire Retardant Doors (FRD) engineered with certified chemical core treatments for industrial and commercial fire-safety compliance.",
        "sort_order": 3,
        "is_active": True,
    },
]

DEFAULT_CONTENT_SECTIONS = [
    {
        "section_key": "hero_section",
        "title": "Master Craftsmanship in Wooden Flush Doors",
        "content": "Shree Balaji Wood manufactures world-class Pine, Hardwood, and Fire Retardant flush doors built with premium seasoned timber.",
        "meta_data": {
            "tagline": "Durable. Certified. Engineered for Excellence.",
            "experience_years": "25+",
        },
    },
    {
        "section_key": "about_company",
        "title": "About Shree Balaji Wood",
        "content": "With decades of experience in the wood manufacturing industry, Shree Balaji Wood operates advanced kiln-seasoning facilities and automated hydraulic hot presses to deliver superior flush doors across India.",
        "meta_data": {
            "focus": "Quality Manufacturing & Precision Wood Processing",
            "standards": "IS:2202 Compliance",
        },
    },
    {
        "section_key": "quality_assurance",
        "title": "Our Quality & Chemical Treatment Standards",
        "content": "Every door core undergoes automated vacuum chemical dipping against termites and borers, balanced cross-band veneers, and rigorous bonding tests.",
        "meta_data": {
            "treatments": ["Anti-Termite", "Anti-Borer", "Boiling Waterproof (BWP) Option"],
        },
    },
    {
        "section_key": "contact_details",
        "title": "Factory & Sales Inquiries",
        "content": "Reach out directly to our production and sales coordinators for customized bulk orders, dealer inquiries, and architect specifications.",
        "meta_data": {
            "phone": "+91 98765 43210",
            "email": "inquiry@shreebalajiwood.com",
            "address": "Survey No. 123, Industrial Area, Gujarat, India",
        },
    },
]


def seed_categories(db: Session) -> int:
    """Idempotently seed default product categories."""
    created = 0
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.scalar(
            select(ProductCategory).where(ProductCategory.slug == cat_data["slug"])
        )
        if not existing:
            category = ProductCategory(**cat_data)
            db.add(category)
            created += 1
    db.flush()
    return created


def seed_website_content(db: Session) -> int:
    """Idempotently seed default CMS content sections."""
    created = 0
    for content_data in DEFAULT_CONTENT_SECTIONS:
        existing = db.scalar(
            select(WebsiteContent).where(
                WebsiteContent.section_key == content_data["section_key"]
            )
        )
        if not existing:
            content = WebsiteContent(**content_data)
            db.add(content)
            created += 1
    db.flush()
    return created


def seed_initial_admin(db: Session) -> bool:
    """Seed the initial administrator account.

    Enforces Phase 3 v2.1 fail-safe security:
    If zero admins exist, INITIAL_ADMIN_USERNAME and INITIAL_ADMIN_PASSWORD
    MUST be provided via environment variables. If missing, raises a RuntimeError.
    """
    existing_admin = db.scalar(select(Admin).limit(1))
    if existing_admin:
        print("[Seed] Administrator account already exists. Skipping admin creation.")
        return False

    username = os.getenv("INITIAL_ADMIN_USERNAME", "").strip()
    password = os.getenv("INITIAL_ADMIN_PASSWORD", "").strip()
    email = os.getenv("INITIAL_ADMIN_EMAIL", "").strip()

    if not username or not password or not email:
        raise RuntimeError(
            "INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_PASSWORD, and "
            "INITIAL_ADMIN_EMAIL environment variables must all be configured."
        )

    # Hash password securely with bcrypt
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    admin = Admin(
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    print(f"[Seed] Created initial administrator: {username}")
    return True


def run_seed(db: Session = None) -> None:
    """Run full idempotent database seeding."""
    close_session = False
    if db is None:
        db = SessionLocal()
        close_session = True

    try:
        cats_added = seed_categories(db)
        content_added = seed_website_content(db)
        admin_added = seed_initial_admin(db)
        db.commit()
        print(f"[Seed] Successfully seeded {cats_added} categories, {content_added} content blocks. Admin added: {admin_added}")
    except Exception as e:
        db.rollback()
        print(f"[Seed Error] {e}", file=sys.stderr)
        raise
    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    run_seed()
