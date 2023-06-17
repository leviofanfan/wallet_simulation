import uuid
import datetime
from sqlalchemy import UUID, String, Float, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class TransferLog(Base):
    __tablename__ = "wallets"

    transfer_uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sender: Mapped[str] = mapped_column(String(16), nullable=False)
    receiver: Mapped[str] = mapped_column(String(16), nullable=False)
    currency_sent: Mapped[str] = mapped_column(String(4), nullable=False)
    currency_received: Mapped[str] = mapped_column(String(4), nullable=False)
    money_sent: Mapped[float] = mapped_column(Float(2), default=0.0)
    paid_on: Mapped[datetime.date] = mapped_column(Date, default=datetime.date.today())
