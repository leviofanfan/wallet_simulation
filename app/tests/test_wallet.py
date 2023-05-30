import unittest
from datetime import datetime

from .constants import TEST_USER_ID, TEST_INVALID_WALLET_NUMBER, TEST_WALLET_NUMBER, TEST_WALLET_NUMBER_RECEIVER, \
    TEST_DATA_TIME_FROM, TEST_DATA_TIME_TO, TEST_INVALID_DATA_TIME

from app.database import Wallet, TransferLog
from app.tests import TestingSessionLocal
from .db_to_test import client, override_get_db
from .test_user import TestUser
from ..api.costants import DATETIME_FORMAT

nonexistent_user_id = TestUser.get_nonexistent_user_id()


class TestWallet(unittest.TestCase):
    def test_top_up_wallet(self):
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/top-up",
            json={"amount": 1.5}
        )
        assert response.status_code == 202, response.text
        balance = response.json()
        assert balance > 1.5, response.text
    # assert balance

    def test_top_up_wallet_with_nonexistent_user_id(self):
        response = client.post(
            f"user/{nonexistent_user_id}/wallet/{TEST_WALLET_NUMBER}/top-up",
            json={"amount": 1}
        )
        assert  response.status_code == 404, response.text

    def test_top_up_nonexistent_wallet(self):
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_INVALID_WALLET_NUMBER}/top-up",
            json={"amount": 1.0}
        )
        assert response.status_code == 404, response.text

    def test_top_up_wallet_with_invalid_amount(self):
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/top-up",
            json={"amount": 1.101}
        )
        assert response.status_code == 417, response.text

    def test_send_money(self, db: TestingSessionLocal = override_get_db()):
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/send",
            json={
                "amount": 1.0,
                "receiver": f"{TEST_WALLET_NUMBER_RECEIVER}"
            }
        )
        assert response.status_code == 202, response.text

        data = response.json()
        assert data["receiver"] == TEST_WALLET_NUMBER_RECEIVER and data["sender"] == TEST_WALLET_NUMBER, response.text
        assert "transfer_uid" in data
        transfer_uid = data["transfer_uid"]

        log = db.query(TransferLog).filter_by(transfer_uid=transfer_uid).first()
        db.delete(log)
        db.commit()
        assert db.query(TransferLog).filter_by(transfer_uid=transfer_uid).first() is None, response.text

    def test_send_money_with_nonexistent_user_id(self):
        response = client.post(
            f"user/{nonexistent_user_id}/wallet/{TEST_WALLET_NUMBER}/send",
            json={
                "amount": 1.0,
                "receiver": f"{TEST_WALLET_NUMBER_RECEIVER}"
            }
        )
        assert response.status_code == 404, response.text

    def test_send_money_with_invalid_wallet_number_sender(self):
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_INVALID_WALLET_NUMBER}/send",
            json={
                "amount": 1,
                "receiver": f"{TEST_WALLET_NUMBER_RECEIVER}"
            }
        )
        assert response.status_code == 404, response.text

    def test_send_money_to_invalid_receiver_wallet_number(self):
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/send",
            json={
                "amount": 1.0,
                "receiver": f"{TEST_INVALID_WALLET_NUMBER}"
            }
        )
        assert response.status_code == 404, response.text

    def test_send_money_with_invalid_amount(self):
        response  = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/send",
            json={
                "amount": 1.01010,
                "receiver": f"{TEST_INVALID_WALLET_NUMBER}"
            }
        )
        assert response.status_code == 404, response.text

    def test_send_money_with_insufficient_funds_in_account(self, db: TestingSessionLocal = override_get_db()):
        wallet_balance = db.query(Wallet.balance).filter_by(owner_id=0).first()
        amount_more_then_wallet_balance = wallet_balance[0] + 1
        response = client.post(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/send",
            json={
                "amount": amount_more_then_wallet_balance,
                "receiver": f"{TEST_WALLET_NUMBER_RECEIVER}"
            }
        )
        assert response.status_code == 405, response.text

    def test_get_logs(self):
        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs"
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list), response.text
        test_log = data[0]
        paid_on = test_log.get("paid_on")
        assert datetime.strptime(paid_on, DATETIME_FORMAT) == datetime(2023, 4, 27, 10, 30, 48), response.text

        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_INVALID_WALLET_NUMBER}/logs"
        )
        assert response.status_code == 404, response.text

        response = client.get(
            f"user/{nonexistent_user_id}/wallet/{TEST_INVALID_WALLET_NUMBER}/logs"
        )
        assert response.status_code == 404, response.text

    def test_logs_with_limits(self):
        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?limit=6"
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) < 6, response.text
        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?limit=3"
        )
        data = response.json()
        assert len(data) == 3, response.text

    def test_logs_with_operation_types(self):
        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?operation_types=out"
        )
        assert response.status_code == 200, response.text
        data = response.json()
        for log in data:
            assert log.get("sender") == TEST_WALLET_NUMBER

        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?operation_types=in"
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 2, response.text

        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?operation_types=in,out"
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 5, response.text

        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?operation_types=out,in"
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 5, response.text

        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?operation_types="
        )
        assert response.status_code == 417, response.text

        response = client.get(
            f"user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?operation_types=invalid_type"
        )
        assert response.status_code == 417, response.text

    def test_logs_with_date_to_and_date_from(self):
        response = client.get(
            f"""user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?date_from={TEST_DATA_TIME_FROM}&date_to={TEST_DATA_TIME_TO}"""
        )
        assert response.status_code == 200, response.text
        data = response.json()
        for log in data:
            assert "paid_on" in log, response.text
            data_time = log["paid_on"]
            assert data_time > TEST_DATA_TIME_FROM, response.text
            assert data_time < TEST_DATA_TIME_TO, response.text

        assert len(data) == 3, response.text

        response = client.get(
            f"""user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?date_from={TEST_DATA_TIME_TO}&date_to={TEST_DATA_TIME_FROM}"""
        )
        assert response.status_code == 200, response.text
        assert len(response.json()) == 0, response.text

        response = client.get(
            f"""user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?date_from={TEST_DATA_TIME_FROM}&date_to={TEST_INVALID_DATA_TIME}"""
        )
        assert response.status_code == 417, response.text

        response = client.get(
            f"""user/{TEST_USER_ID}/wallet/{TEST_WALLET_NUMBER}/logs?date_from={TEST_INVALID_DATA_TIME}&date_to={TEST_DATA_TIME_TO}"""
        )
        assert response.status_code == 417, response.text



