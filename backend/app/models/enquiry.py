from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
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
    from app.models.product import Product


class Enquiry(Base):
    """Customer quotation request (RFQ) with custom dimension specifications."""

    __tablename__ = "enquiries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reference_number: Mapped[str] = mapped_column(
        String(30), unique=True, nullable=False
    )
    product_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("products.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        default=None,
    )
    customer_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(25), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, default=None
    )
    company_name: Mapped[Optional[str]] = mapped_column(
        String(150), nullable=True, default=None
    )
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    gst_number: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True, default=None
    )
    door_type: Mapped[str] = mapped_column(String(50), nullable=False)
    core_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dipping: Mapped[str] = mapped_column(String(50), nullable=False)
    height: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    height_unit: Mapped[str] = mapped_column(String(10), nullable=False)
    width: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    width_unit: Mapped[str] = mapped_column(String(10), nullable=False)
    thickness_mm: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(30), default="New", nullable=False)
    admin_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationship to Product (optional reference)
    product: Mapped[Optional["Product"]] = relationship(
        "Product", back_populates="enquiries"
    )

    __table_args__ = (
        CheckConstraint(
            "length(reference_number) >= 10", name="chk_enquiries_ref_len"
        ),
        CheckConstraint("length(customer_name) >= 2", name="chk_enquiries_name_len"),
        CheckConstraint("length(phone) >= 7", name="chk_enquiries_phone_len"),
        CheckConstraint("length(door_type) > 0", name="chk_enquiries_door_type"),
        CheckConstraint(
            "core_type IN ('Single Core', 'Double Core', 'Not Specified')",
            name="chk_enquiries_core_type",
        ),
        CheckConstraint(
            "dipping IN ('With Dipping', 'Without Dipping', 'Not Specified')",
            name="chk_enquiries_dipping",
        ),
        CheckConstraint("height > 0", name="chk_enquiries_height_pos"),
        CheckConstraint(
            "height_unit IN ('ft', 'in', 'cm', 'm')", name="chk_enquiries_height_unit"
        ),
        CheckConstraint("width > 0", name="chk_enquiries_width_pos"),
        CheckConstraint(
            "width_unit IN ('ft', 'in', 'cm', 'm')", name="chk_enquiries_width_unit"
        ),
        CheckConstraint("thickness_mm > 0", name="chk_enquiries_thickness_pos"),
        CheckConstraint("quantity >= 1", name="chk_enquiries_qty_pos"),
        CheckConstraint(
            "status IN ('New', 'Contacted', 'Quoted', 'In Discussion', 'Closed', 'Archived')",
            name="chk_enquiries_status",
        ),
        Index("ix_enquiries_status_created", "status", created_at.desc()),
        Index("ix_enquiries_phone", "phone"),
    )
