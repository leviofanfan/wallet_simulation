from datetime import datetime

from fastapi import HTTPException
from pydantic import EmailStr
from starlette import status

from .schemas import WalletNumberType
from app.database import controllers, User, Wallet
from ..database.database import Session


def validation_user_id(user_id: int, db: Session):
    uc = controllers.UserController(db)
    users_ids = [user.id for user in uc.get_users()]
    if user_id not in users_ids:
        raise HTTPException(
            status_code=404, detail="User not found", headers={"header": "user not found"})


def validation_wallet_number(wallet_number: WalletNumberType, user_id: int, db: Session):
    uc = controllers.UserController(db)
    if wallet_number not in uc.read_wallets_balance_by_user_id(user_id).keys():
        raise HTTPException(
            status_code=404,
            detail=f"User #{user_id} has not a {wallet_number} wallet",
            headers={"header": "wallet not found"}
        )


def email_validation_if_exists(email: EmailStr, db: Session):
    if db.query(User).filter_by(email=email).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="try entering a different email",
            headers={"header": "email already exists"}
        )


def wallet_receiver_validation(wallet_number: WalletNumberType, db: Session):
    numbers = [number[0] for number in db.query(Wallet.number).all()]
    if wallet_number not in numbers:
        raise HTTPException(
            status_code=404,
            detail=f"Wallet '{wallet_number}' doesn't exist",
            headers={"header": "Wallet not found"}
        )


def validation_transfer_amount(transfer_amount: float|int):
    amount_validation = str(transfer_amount)
    transfer_amount = float(transfer_amount)
    if transfer_amount <= 0.0:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Impossible to transfer amount less or quel to zero",
            headers={"headers": "Expectation failed"}
        )
    if "." in amount_validation and len(amount_validation.split(".")[1]) > 2:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="You can transfer an amount that has less than three digits after the decimal point",
            headers={"headers": "Expectation failed"}
        )

def validation_operation_types(operation_types: list):
    if len(operation_types) > 2:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Invalid operation types.",
            headers={"headers": "Expectation failed"}
        )
    allowed_types = {'in', 'out'}
    if all(op_type in allowed_types for op_type in operation_types) is False:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Invalid operation types.",
            headers={"headers": "Expectation failed"}
        )

def validation_date_time(date_time: str):
    try:
        datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail=f"Time data {date_time} does not match format '%Y-%m-%d %H:%M:%S'",
            headers={"headers": "Expectation failed"}
        )
