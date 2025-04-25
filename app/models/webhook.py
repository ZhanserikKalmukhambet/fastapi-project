from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class WebhookRequest(Base):
    __tablename__ = "webhook_requests"

    # Required fields (no defaults)
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    callback_url: Mapped[str] = mapped_column(String(512), nullable=False)

    response: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)

    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow()) 