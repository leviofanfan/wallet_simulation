import datetime
import random
import uuid
from typing import Optional

from app.api.constants import WALLET_PREFIX
from app.api.schemas import WalletNumberType, WalletCreate, AddMoney, TransferMoney
from app.database.database import Session
from app.database.models.transfer_log import TransferLog
from app.database.models.wallet import Wallet
from app.currency_api import Controller


class WalletController:

    def __init__(self, db: Session):
        self._c = Controller()
        self.db = db

    @staticmethod
    def _create_wallet_number(currency: str, db: Session) -> WalletNumberType:
        numbers = db.query(Wallet.number).all()
        wallet_number = WALLET_PREFIX + "".join([str(random.randint(0, 9)) for _ in range(10)]) + currency
        while True:
            try:
                numbers.index(wallet_number)
            except ValueError:
                return wallet_number
            else:
                wallet_number = WALLET_PREFIX + "".join([str(random.randint(0, 9)) for _ in range(10)]) + currency


    def create_wallet_db_from_wallet_in_db(self, wallet: WalletCreate, user_id: int) -> Wallet:
        currency = wallet.currency
        wallet_db = Wallet(
            currency=currency,
            number=WalletController._create_wallet_number(currency=currency, db=self.db),
            owner_id=user_id,
            updated_at=datetime.date.today()
        )
        self.db.add(wallet_db)
        self.db.commit()
        self.db.refresh(wallet_db)
        return wallet_db

    def top_up_wallet_balance(
            self, add_money: AddMoney, user_id: int, wallet_number: WalletNumberType
    ) -> Wallet:
        wallet_query = self.db.query(Wallet).filter_by(owner_id=user_id, number=wallet_number)
        if isinstance(add_money.amount, int) is True:
            add_money.amount = float(add_money.amount)
        wallet_query.update({Wallet.balance: Wallet.balance + add_money.amount})
        self.db.commit()
        return wallet_query.first().balance

    def transfer_money_between_wallets(
            self, sender_number: WalletNumberType, transfer_money: TransferMoney
    ) -> Optional[TransferLog]:
        wallet_sender_query = self.db.query(Wallet).filter_by(number=sender_number)

        if wallet_sender_query.first().balance < transfer_money.amount:
            return None

        if isinstance(transfer_money.amount, int) is True:
            transfer_money.amount = float(transfer_money.amount)

        sender_balance = wallet_sender_query.first().balance
        wallet_sender_query.update({Wallet.balance: round(sender_balance + transfer_money.amount, 2)})
        currency_sender = wallet_sender_query.first().currency

        wallet_receiver_query = self.db.query(Wallet).filter_by(number=transfer_money.receiver)

        currency_receiver = wallet_receiver_query.first().currency

        money_received = self._c.convent_money_from_sender_to_receiver(
            currency_sender=currency_sender, currency_receiver=currency_receiver, amount_sent=transfer_money.amount
        )

        receiver_balance = wallet_receiver_query.first().balance
        wallet_receiver_query.update({Wallet.balance: round(receiver_balance + money_received, 2)})


        transfer_log = TransferLog(
            transfer_uid=uuid.uuid4(),
            sender=sender_number,
            receiver=transfer_money.receiver,
            currency_sent=currency_sender,
            currency_received=currency_receiver,
            money_sent=transfer_money.amount,
            money_received=money_received,
        )
        self.db.add(transfer_log)
        self.db.commit()
        self.db.refresh(transfer_log)
        return transfer_log



