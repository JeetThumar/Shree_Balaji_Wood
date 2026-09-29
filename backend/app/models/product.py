from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.category import ProductCategory
    from app.models.enquiry import Enquiry
    from app.models.image import ProductImage


class Product(Base):
    """Product showcase entity for wooden flush doors."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_categories.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), unique=True, nullable=False)
    short_description: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True, default=None
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    core_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dipping: Mapped[str] = mapped_column(String(50), nullable=False)
    standard_thicknesses: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, default=None
    )
    base_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), nullable=True, default=None
    )
    show_price: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    category: Mapped["ProductCategory"] = relationship(
        "ProductCategory", back_populates="products"
    )
    images: Mapped[List["ProductImage"]] = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    enquiries: Mapped[List["Enquiry"]] = relationship(
        "Enquiry", back_populates="product"
    )

    __table_args__ = (
        CheckConstraint("length(name) >= 2", name="chk_products_name_len"),
        CheckConstraint(
            "core_type IN ('Single Core', 'Double Core', 'Both')",
            name="chk_products_core_type",
        ),
        CheckConstraint(
            "dipping IN ('With Dipping', 'Without Dipping', 'Both')",
            name="chk_products_dipping",
        ),
        CheckConstraint(
            "base_price IS NULL OR base_price >= 0",
            name="chk_products_base_price",
        ),
        Index("ix_products_category_active_order", "category_id", "is_active", "sort_order"),
        Index("ix_products_featured", "is_featured", "is_active", "sort_order"),
    )
