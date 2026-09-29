from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import CheckConstraint, DateTime, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WebsiteContent(Base):
    """Website CMS dynamic content block (Hero, About Us, Quality Standards)."""

    __tablename__ = "website_contents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_key: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True, default=dict
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

    __table_args__ = (
        CheckConstraint("length(title) > 0", name="chk_content_title_len"),
        CheckConstraint("length(content) > 0", name="chk_content_body_len"),
    )
