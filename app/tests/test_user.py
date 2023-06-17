import random
import unittest

from . import TestingSessionLocal
from .db_to_test import client, override_get_db
from faker import Faker

from .constants import TEST_NAME, TEST_SURNAME, TEST_USER_ID_WITHOUT_WALLETS, TEST_USER_ID
from ..database import User, Wallet
# edit test's data to be themselves


class TestUser:
    def setup_all(self):
        pass

    def test_read_users(self):
        response = client.get("/user/")
        assert response.status_code == 200

    def test_create_user(self, db: TestingSessionLocal = override_get_db()):
        fake = Faker()
        email = fake.user_name() + "@gmail.com"
        response = client.post(
            "/user/",
            json={
                "name": TEST_NAME,
                "surname": TEST_SURNAME,
                "email": email
            }
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["email"] == email
        assert "id" in data
        user_id = data["id"]

        response = client.get(f"/user/{user_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == email

        user = db.query(User).filter_by(email=email).first()
        db.delete(user)
        db.commit()
        assert db.query(User).filter_by(email=email).first() is None, response.text


    def test_create_user_with_invalid_email(self):
        response = client.post(
            "/user/",
            json={
                "name": TEST_NAME,
                "surname": TEST_SURNAME,
                "email": "invalid_email"
            }
        )
        assert response.status_code == 422, response.text

    def test_email_already_exists(self):
        response = client.post(
            "/user/",
            json={
                "name": TEST_NAME,
                "surname": TEST_SURNAME,
                "email": "some.email@gmail.com"
            }
        )
        assert response.status_code == 422, response.text

    @staticmethod
    def get_nonexistent_user_id(db: TestingSessionLocal = override_get_db()):
        users_ids = [user_id for (user_id,) in db.query(User.id).all()]
        nonexistent_ids = []
        for row_id in range(int(max(users_ids)) + 2):
            if row_id not in users_ids:
                nonexistent_ids.append(row_id)
        return nonexistent_ids[random.randint(0, len(nonexistent_ids)-1)]

    def test_get_nonexistent_user(self):
        nonexistent_user_id = self.get_nonexistent_user_id()
        response = client.get(f"/user/{nonexistent_user_id}")
        assert response.status_code == 404, response.text

    def test_read_user_wallets_without_wallets(self):
        response = client.get(f"/user/{TEST_USER_ID_WITHOUT_WALLETS}/wallets")
        assert response.status_code == 200, response.text
        assert response.json() == {}, response.text

    def test_create_wallet_by_nonexistent_user(self):
        response = client.post(f"/user/{self.get_nonexistent_user_id()}/", json={"currency": "EUR"})
        assert response.status_code == 404, response.text

    def test_create_user_wallet_with_invalid_currency_format(self):
        response = client.post(f"/user/{TEST_USER_ID}/", json={"currency": "EURO"})
        assert response.status_code == 400, response.text

    def test_create_user_wallet_with_already_exists_currency(self):
        response = client.post(f"/user/{TEST_USER_ID}/", json={"currency": "PLN"})
        assert response.status_code == 400, response.text

    def test_create_user_wallet_with_unavailable_currency(self):
        response = client.post(f"/user/{TEST_USER_ID}/", json={"currency": "UAH"})
        assert response.status_code == 406, response.text

    def test_create_user_wallet(self, db: TestingSessionLocal = override_get_db()):
        response = client.post(f"/user/{TEST_USER_ID}/", json={"currency": "EUR"})
        assert response.status_code == 201, response.text
        wallet = response.json()
        assert wallet["currency"] == "EUR"

        assert "number" in wallet
        wallet_number = wallet["number"]

        response = client.get(f"/user/{TEST_USER_ID}/wallets/")
        wallets = response.json()
        assert wallets.get(wallet_number) is not None

        wallet = db.query(Wallet).filter_by(number=wallet_number).first()
        db.delete(wallet)
        db.commit()
        assert db.query(Wallet).filter_by(number=wallet_number).first() is None, response.text