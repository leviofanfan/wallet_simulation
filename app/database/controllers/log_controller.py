from datetime import datetime
import re

from fastapi import HTTPException
from starlette import status

from app.api.schemas import WalletNumberType
from app.api.constants import DATETIME_FORMAT
from app.database.database import Session
from app.database.models import TransferLog

from sqlalchemy.sql import false as sql_false


class LogController:
    def __init__(self, db: Session):
        self.db = db

    def _get_all_logs_by_wallet_number(self, wallet_number: WalletNumberType) -> list[TransferLog]:
        return self.db.query(TransferLog).filter(
            (TransferLog.receiver == wallet_number) | (TransferLog.sender == wallet_number)
        ).all()

    @staticmethod
    def _get_date_time_object(date_time: str):
        return datetime.strptime(date_time, DATETIME_FORMAT)

    @staticmethod
    def _get_from_to_as_date_time_objects(date_from: str, date_to: str) -> tuple[datetime, datetime]:
        date_from = LogController._get_date_time_object(date_from)
        date_to = LogController._get_date_time_object(date_to)
        return date_from, date_to

    def _get_logs_from_to_time(
            self,
            date_from: str,
            date_to: str
    ):
        date_from, date_to = LogController._get_from_to_as_date_time_objects(date_from=date_from, date_to=date_to)
        return self.db.query(TransferLog).filter(
            date_from < TransferLog.paid_on, TransferLog.paid_on  < date_to
        )

    def old_get_logs_using_operation_types(
            self,
            operation_types: list[str],
            wallet_number: WalletNumberType,
            date_from: str,
            date_to: str,
            data_limit: int|None = None
    ) -> list[TransferLog]:
        operation_types = ','.join(operation_types)

        if data_limit is None:
            out_and_in = {
                "wallet_as_sender": self._get_logs_from_to_time(
                        date_from=date_from, date_to=date_to
                    ).filter(
                        TransferLog.sender == wallet_number
                    ).order_by(
                        TransferLog.paid_on.desc()
                    ).all(),
                "wallet_as_receiver": self._get_logs_from_to_time(
                        date_from=date_from, date_to=date_to
                    ).filter(
                        TransferLog.receiver == wallet_number
                    ).order_by(
                        TransferLog.paid_on.desc()
                    ).all(),
                "all_logs": self._get_logs_from_to_time(
                    date_from=date_from, date_to=date_to
                    ).filter(
                        (TransferLog.sender == wallet_number) | (TransferLog.receiver == wallet_number)
                    ).order_by(
                        TransferLog.paid_on.desc()
                    ).all()
            }
        else:
            out_and_in = {
                "wallet_as_sender": self._get_logs_from_to_time(
                    date_from=date_from, date_to=date_to
                ).filter(
                    TransferLog.sender == wallet_number
                ).order_by(
                    TransferLog.paid_on.desc()
                ).limit(
                    data_limit
                ).all(),
                "wallet_as_receiver": self._get_logs_from_to_time(
                    date_from=date_from, date_to=date_to
                ).filter(
                    TransferLog.receiver == wallet_number
                ).order_by(
                    TransferLog.paid_on.desc()
                ).limit(
                    data_limit
                ).all(),
                "all_logs": self._get_logs_from_to_time(
                    date_from=date_from, date_to=date_to
                ).filter(
                    sql_false() | (TransferLog.sender == wallet_number) | (TransferLog.receiver == wallet_number)
                ).order_by(
                    TransferLog.paid_on.desc()
                ).limit(
                    data_limit
                ).all()
            }

        if re.search("^out$", operation_types):
            return out_and_in["wallet_as_sender"]
        elif re.search("^in$", operation_types):
            return out_and_in["wallet_as_receiver"]
        elif re.search("(^in,out$)|(^out,in$)", operation_types) or operation_types is None:
            return out_and_in["all_logs"]
        else:
            raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Invalid operation types.",
            headers={"headers": "Expectation failed"}
        )


    def get_logs_using_operation_types(
            self,
            operation_types: list[str],
            wallet_number: WalletNumberType,
            date_from: str,
            date_to: str,
            data_limit: int|None = None
    ) -> list[TransferLog]:

        transfer_logs_filter = sql_false()
        if "in" in operation_types:
            transfer_logs_filter |= TransferLog.receiver == wallet_number
        if "out" in operation_types:
            transfer_logs_filter |= TransferLog.sender == wallet_number

        logs = self._get_logs_from_to_time(date_from=date_from, date_to=date_to)
        filtered_logs = logs.filter(transfer_logs_filter).order_by(
            TransferLog.paid_on.desc()
        )
        if data_limit:
            filtered_logs = filtered_logs.limit(data_limit)
        return filtered_logs.all()

