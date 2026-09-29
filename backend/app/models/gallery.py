from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class GalleryImage(Base):
    """Gallery media asset (factory, machinery, seasoning, installations)."""

    __tablename__ = "gallery_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(
        String(50), default="Factory", nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("length(title) >= 2", name="chk_gallery_title_len"),
        CheckConstraint("length(image_path) > 0", name="chk_gallery_path_len"),
        CheckConstraint(
            "category IN ('Factory', 'Machinery', 'Quality Testing', 'Finished Doors', 'General')",
            name="chk_gallery_category",
        ),
        Index(
            "ix_gallery_images_category_active_order",
            "category",
            "is_active",
            "sort_order",
        ),
    )
