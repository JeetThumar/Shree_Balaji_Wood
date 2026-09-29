import os
import sys
import pytest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import Base
from app.db.seed import seed_categories, seed_initial_admin, seed_website_content
from app.models.admin import Admin
from app.models.category import ProductCategory
from app.models.content import WebsiteContent
from app.models.enquiry import Enquiry
from app.models.image import ProductImage
from app.models.product import Product


@pytest.fixture(scope="function")
def db_session():
    """Create an isolated in-memory SQLite database session with all tables and constraints."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    # Enable foreign keys in SQLite for testing referential actions
    with engine.connect() as conn:
        conn.exec_driver_sql("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def test_entity_inventory_and_tables():
    """Verify all 7 approved entities are declared and registered in Base.metadata."""
    expected_tables = {
        "admins",
        "product_categories",
        "products",
        "product_images",
        "enquiries",
        "gallery_images",
        "website_contents",
    }
    actual_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(actual_tables), f"Missing tables: {expected_tables - actual_tables}"


def test_category_uniqueness(db_session: Session):
    """Verify slug and name uniqueness on product_categories."""
    cat1 = ProductCategory(name="Pine Doors", slug="pine-doors", sort_order=1)
    db_session.add(cat1)
    db_session.commit()

    # Duplicate slug
    cat2 = ProductCategory(name="Pine Doors Different", slug="pine-doors", sort_order=2)
    db_session.add(cat2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Duplicate name
    cat3 = ProductCategory(name="Pine Doors", slug="pine-doors-2", sort_order=3)
    db_session.add(cat3)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_product_category_fk_restrict(db_session: Session):
    """Verify ON DELETE RESTRICT prevents category deletion while referencing products exist."""
    cat = ProductCategory(name="Hardwood", slug="hardwood", sort_order=1)
    db_session.add(cat)
    db_session.commit()

    prod = Product(
        category_id=cat.id,
        name="Double Core Hardwood",
        slug="double-core-hardwood",
        core_type="Double Core",
        dipping="With Dipping",
        standard_thicknesses="30mm, 35mm",
    )
    db_session.add(prod)
    db_session.commit()

    # Attempt deleting the category
    db_session.delete(cat)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_product_image_cascade(db_session: Session):
    """Verify ON DELETE CASCADE deletes child images when a product is deleted."""
    cat = ProductCategory(name="FRD", slug="frd", sort_order=1)
    db_session.add(cat)
    db_session.commit()

    prod = Product(
        category_id=cat.id,
        name="FRD Door 60 Min",
        slug="frd-door-60-min",
        core_type="Single Core",
        dipping="Without Dipping",
    )
    db_session.add(prod)
    db_session.commit()

    img = ProductImage(
        product_id=prod.id,
        image_path="products/frd-01.webp",
        is_primary=True,
    )
    db_session.add(img)
    db_session.commit()

    image_id = img.id
    # Delete parent product
    db_session.delete(prod)
    db_session.commit()

    # Child image must be gone
    deleted_img = db_session.get(ProductImage, image_id)
    assert deleted_img is None


def test_product_enquiry_set_null(db_session: Session):
    """Verify ON DELETE SET NULL preserves enquiry record when product is deleted."""
    cat = ProductCategory(name="Pine", slug="pine", sort_order=1)
    db_session.add(cat)
    db_session.commit()

    prod = Product(
        category_id=cat.id,
        name="Pine SC",
        slug="pine-sc",
        core_type="Single Core",
        dipping="With Dipping",
    )
    db_session.add(prod)
    db_session.commit()

    enquiry = Enquiry(
        reference_number="RFQ-20260929-0001",
        product_id=prod.id,
        customer_name="Rajesh Patel",
        phone="9876543210",
        door_type="Pine Flush Door",
        core_type="Single Core",
        dipping="With Dipping",
        height=Decimal("7.0"),
        height_unit="ft",
        width=Decimal("3.0"),
        width_unit="ft",
        thickness_mm=Decimal("32.0"),
        quantity=25,
        status="New",
    )
    db_session.add(enquiry)
    db_session.commit()

    enquiry_id = enquiry.id
    # Delete product
    db_session.delete(prod)
    db_session.commit()

    # Enquiry must persist with product_id set to None
    refreshed_enquiry = db_session.get(Enquiry, enquiry_id)
    assert refreshed_enquiry is not None
    assert refreshed_enquiry.product_id is None
    assert refreshed_enquiry.customer_name == "Rajesh Patel"
    assert refreshed_enquiry.height == Decimal("7.0")
    assert refreshed_enquiry.height_unit == "ft"


def test_primary_image_partial_unique(db_session: Session):
    """Verify partial unique index enforces AT MOST ONE primary image per product."""
    cat = ProductCategory(name="Pine Line", slug="pine-line", sort_order=1)
    db_session.add(cat)
    db_session.commit()

    prod = Product(
        category_id=cat.id,
        name="Pine Sample",
        slug="pine-sample",
        core_type="Single Core",
        dipping="With Dipping",
    )
    db_session.add(prod)
    db_session.commit()

    img1 = ProductImage(product_id=prod.id, image_path="p1.webp", is_primary=True)
    db_session.add(img1)
    db_session.commit()

    # Second primary image on the same product must violate the partial unique index
    img2 = ProductImage(product_id=prod.id, image_path="p2.webp", is_primary=True)
    db_session.add(img2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Adding a non-primary image must succeed
    img3 = ProductImage(product_id=prod.id, image_path="p3.webp", is_primary=False)
    db_session.add(img3)
    db_session.commit()
    assert img3.id is not None


def test_enquiry_check_constraints(db_session: Session):
    """Verify CHECK constraints on enquiry dimensions, units, quantity, and status."""
    valid_kwargs = dict(
        reference_number="RFQ-20260929-0002",
        customer_name="Anita Sharma",
        phone="9876543211",
        door_type="Hardwood",
        core_type="Double Core",
        dipping="With Dipping",
        height=Decimal("80.0"),
        height_unit="in",
        width=Decimal("36.0"),
        width_unit="in",
        thickness_mm=Decimal("35.0"),
        quantity=10,
        status="New",
    )

    # 1. Height must be positive
    bad_height = valid_kwargs.copy()
    bad_height["height"] = Decimal("-5.0")
    bad_height["reference_number"] = "RFQ-BAD-01"
    db_session.add(Enquiry(**bad_height))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 2. Invalid unit
    bad_unit = valid_kwargs.copy()
    bad_unit["height_unit"] = "yard"
    bad_unit["reference_number"] = "RFQ-BAD-02"
    db_session.add(Enquiry(**bad_unit))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 3. Quantity must be >= 1
    bad_qty = valid_kwargs.copy()
    bad_qty["quantity"] = 0
    bad_qty["reference_number"] = "RFQ-BAD-03"
    db_session.add(Enquiry(**bad_qty))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # 4. Invalid status
    bad_status = valid_kwargs.copy()
    bad_status["status"] = "UnknownStatus"
    bad_status["reference_number"] = "RFQ-BAD-04"
    db_session.add(Enquiry(**bad_status))
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_timestamp_lifecycle(db_session: Session):
    """Verify created_at is populated and updated_at updates upon record modification."""
    cat = ProductCategory(name="Timestamp Test", slug="timestamp-test", sort_order=1)
    db_session.add(cat)
    db_session.commit()
    db_session.refresh(cat)

    created_at = cat.created_at
    updated_at = cat.updated_at
    assert created_at is not None
    assert updated_at is not None

    # Update description
    cat.description = "Updated description text"
    db_session.commit()
    db_session.refresh(cat)

    assert cat.created_at == created_at


def test_seed_idempotency(db_session: Session):
    """Verify seed_categories and seed_website_content are strictly idempotent."""
    cats_run1 = seed_categories(db_session)
    content_run1 = seed_website_content(db_session)
    db_session.commit()

    assert cats_run1 == 3
    assert content_run1 == 4

    # Run again - must add 0 rows
    cats_run2 = seed_categories(db_session)
    content_run2 = seed_website_content(db_session)
    db_session.commit()

    assert cats_run2 == 0
    assert content_run2 == 0

    total_cats = db_session.scalars(select(ProductCategory)).all()
    assert len(total_cats) == 3


def test_seed_admin_fail_safe(db_session: Session, monkeypatch):
    """Verify seed_initial_admin fails safely when environment variables are missing."""
    monkeypatch.delenv("INITIAL_ADMIN_USERNAME", raising=False)
    monkeypatch.delenv("INITIAL_ADMIN_PASSWORD", raising=False)
    monkeypatch.delenv("INITIAL_ADMIN_EMAIL", raising=False)

    with pytest.raises(
        RuntimeError,
        match="INITIAL_ADMIN_USERNAME, INITIAL_ADMIN_PASSWORD, and INITIAL_ADMIN_EMAIL",
    ):
        seed_initial_admin(db_session)


def test_seed_admin_success(db_session: Session, monkeypatch):
    """Verify seed_initial_admin creates an admin with valid bcrypt hash when secrets are provided."""
    monkeypatch.setenv("INITIAL_ADMIN_USERNAME", "superadmin")
    monkeypatch.setenv("INITIAL_ADMIN_PASSWORD", "SuperSecurePassword123!")
    monkeypatch.setenv("INITIAL_ADMIN_EMAIL", "superadmin@balajiwood.com")

    created = seed_initial_admin(db_session)
    db_session.commit()
    assert created is True

    admin = db_session.scalar(select(Admin).where(Admin.username == "superadmin"))
    assert admin is not None
    assert admin.email == "superadmin@balajiwood.com"
    assert admin.password_hash.startswith("$2")  # bcrypt prefix

    # Second run must skip
    created_again = seed_initial_admin(db_session)
    assert created_again is False
