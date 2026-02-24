from sqlalchemy import String, Text, DateTime, func, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class LedgerEventModel(Base):
    __tablename__ = "ledger_events"
    __table_args__ = (
        UniqueConstraint("org_id", "event_id", name="uq_org_event"),
        Index("ix_org_created", "org_id", "created_at"),
        {"schema": "licitra"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    org_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    event_id: Mapped[str] = mapped_column(String(128), nullable=False)

    prev_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    current_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    payload_cjson: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
