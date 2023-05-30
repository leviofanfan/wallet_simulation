from datetime import datetime
from typing import Annotated

from email_validator import validate_email
from fastapi import APIRouter, Body, Depends, Query
from starlette import status

from .dependencies import get_db
from .costants import USER_CREATE_EXAMPLE, DATETIME_FORMAT, EARLIEST_DATETIME
from .schemas import UserCreate, WalletCreate, WalletDB, WalletNumberType, WalletBalanceType, UserDB, AddMoney, \
    TransferMoney, TransferLogDB
from .utils import validation_user_id, validation_wallet_number, email_validation_if_exists, \
    wallet_receiver_validation, validation_transfer_amount, validation_operation_types, validation_date_time

from app.database import UserController, WalletController, LogController

from fastapi import HTTPException

from app.currency_api import Controller
from ..database.database import Session


router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.post("/", response_model=UserDB, status_code=201)
def create_user(new_user: UserCreate = Body(example=USER_CREATE_EXAMPLE), db: Session = Depends(get_db)):
    if validate_email(new_user.email) is False:
         raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="email is not valid")
    email_validation_if_exists(new_user.email, db)
    uc = UserController(db)
    return uc.create_userdb_from_user(new_user)


@router.get("/", status_code=status.HTTP_200_OK)
def read_users(db: Session = Depends(get_db)) -> list[UserDB]:
    uc = UserController(db)
    return uc.get_users()


@router.get("/{user_id}/", status_code=status.HTTP_200_OK, response_model=UserDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    validation_user_id(user_id, db)
    uc = UserController(db)
    return uc.get_user(user_id)


@router.get("/{user_id}/wallets", status_code=status.HTTP_200_OK)
def read_user_wallets(user_id: int, db: Session = Depends(get_db)) -> dict[WalletNumberType, WalletBalanceType]:
    validation_user_id(user_id, db)
    uc = UserController(db)
    return uc.read_wallets_balance_by_user_id(user_id)


@router.post("/{user_id}/", status_code=status.HTTP_201_CREATED, response_model=WalletDB)
def create_wallet_for_user(user_id: int, new_wallet: WalletCreate, db: Session = Depends(get_db)):
    validation_user_id(user_id, db)
    currency = new_wallet.currency
    if len(currency) != 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid currency format")
    uc = UserController(db)
    if currency in uc.get_currencies_by_user(user_id=user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User already has some {currency} wallet"
        )

    c = Controller()
    if currency not in c.rates:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="unavailable currency")
    wc = WalletController(db)
    return wc.create_wallet_db_from_wallet_in_db(wallet=new_wallet, user_id=user_id)


@router.post("/{user_id}/wallet/{wallet_number}/top-up", status_code=status.HTTP_202_ACCEPTED)
def top_up_wallet(
        user_id: int, wallet_number: WalletNumberType, add_money: AddMoney, db: Session = Depends(get_db)
) -> WalletBalanceType:
    validation_user_id(user_id, db)
    validation_wallet_number(wallet_number,user_id, db)
    validation_transfer_amount(add_money.amount)
    wc = WalletController(db)
    return wc.top_up_wallet_balance(add_money, user_id, wallet_number)


@router.post(
    "/{user_id}/wallet/{wallet_number}/send", status_code=status.HTTP_202_ACCEPTED, response_model=TransferLogDB
)
def send_money_from_wallet_number(
        user_id: int, wallet_number: WalletNumberType, transfer_money: TransferMoney, db: Session = Depends(get_db)
):
    validation_user_id(user_id, db)
    validation_wallet_number(wallet_number, user_id, db)
    wallet_receiver_validation(transfer_money.receiver, db)
    validation_transfer_amount(transfer_money.amount)

    wc = WalletController(db)
    transfer_log = wc.transfer_money_between_wallets(sender_number=wallet_number, transfer_money=transfer_money)
    if transfer_log is None:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Insufficient funds in the account"
        )
    return transfer_log


@router.get("/{user_id}/wallet/{wallet_number}/logs", response_model=list[TransferLogDB], status_code=200)
def read_logs(
        user_id: int,
        wallet_number: WalletNumberType,
        operation_types: Annotated[str, Query(
            examples={
                "all_logs": "in,out",
                "logs_input": "in",
                "logs_output": "out"
            }
        )] = "out,in",
        date_from: str = EARLIEST_DATETIME,
        date_to: str = datetime.strftime(datetime.now(), DATETIME_FORMAT),
        limit: int|None = None,
        db: Session = Depends(get_db),
    ):
    validation_user_id(user_id, db)
    validation_wallet_number(wallet_number, user_id, db)
    validation_operation_types(operation_types.split(","))
    validation_date_time(date_from)
    validation_date_time(date_to)
    lc = LogController(db)
    return lc.get_logs_using_operation_types(
        operation_types = operation_types.split(','),
        wallet_number=wallet_number,
        date_from=date_from,
        date_to=date_to,
        data_limit=limit
    )
