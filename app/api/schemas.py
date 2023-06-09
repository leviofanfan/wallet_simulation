import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, validator

from app.api.constants import DATETIME_FORMAT

WalletNumberType = str
WalletBalanceType = float
CurrencyType = str
EmailType = EmailStr


class WalletBase(BaseModel):
    currency: CurrencyType


class WalletCreate(WalletBase):
    pass


class WalletDB(WalletBase):
    number: WalletNumberType = ""
    balance: float = 0.0
    created_at: datetime.date
    updated_at: datetime.date = datetime.date.today()
    is_active: bool = True
    owner_id: int

    class Config:
        orm_mode = True


class AddMoney(BaseModel):
    amount: float|int


class TransferMoney(AddMoney):
    receiver: WalletNumberType


class TransferLogDB(BaseModel):
    transfer_uid: uuid.UUID
    sender: WalletNumberType
    receiver: WalletNumberType
    currency_sent: str
    currency_received: str
    money_sent: float|int
    money_received: float
    paid_on: str

    @validator("paid_on", pre=True)
    def paid_on_to_str(cls, paid_on: datetime.datetime) -> str:
        if paid_on:
            return paid_on.strftime(DATETIME_FORMAT)

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    name: str
    surname: str
    email: EmailType


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    pass


class UserDB(UserBase):
    id: Optional[int] = None
    created_at: datetime.date = datetime.date.today()

    class Config:
        orm_mode = True
