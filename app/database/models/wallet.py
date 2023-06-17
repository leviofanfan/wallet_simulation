import datetime

from sqlalchemy import Integer, String, ForeignKey, Float, Boolean, Date, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(4), nullable=False)
    balance: Mapped[float] = mapped_column(Float(2), default=0.0)
    created_at: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today())
    updated_at: Mapped[datetime.date] = mapped_column(Date, onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
