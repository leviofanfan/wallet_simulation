from ..database import Session

from app.api.schemas import UserCreate, WalletNumberType, WalletBalanceType, CurrencyType
from app.database.models.wallet import Wallet
from app.database.models.user import User


class UserController:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int) -> User:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_userdb_from_user(self, user: UserCreate) -> User:
        db_user = User(name=user.name,surname=user.surname,email=user.email)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def read_wallets_balance_by_user_id(self, user_id: int) -> dict[WalletNumberType, WalletBalanceType]:
        numbers = [number[0] for number in self.db.query(Wallet.number).filter_by(owner_id=user_id).all()]
        balances = [balance[0] for balance in self.db.query(Wallet.balance).filter_by(owner_id=user_id).all()]
        return dict(zip(numbers, balances))

    def get_currencies_by_user(self, user_id: int) -> list[CurrencyType]:
        return [currency[0] for currency in self.db.query(Wallet.currency).filter_by(owner_id=user_id)]

    def get_users(self) -> list[User]:
        return list(self.db.query(User).all())