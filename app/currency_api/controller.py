from typing import Optional

from app.currency_api.client import Client
from config import config


class Controller:
    def __init__(self, rates: Optional[dict] = None):
        self.exchange_rates = {}
        self.rates = rates
        self.update_rates()

    @staticmethod
    def get_rates() -> dict:
        client = Client(currency_exchange_api_key=config.CURRENCY_EXCHANGE_API_KEY)
        if client.latest_currency_rates is None:
            client.get_latest_currency_rates(config.CURRENCY_EXCHANGE_API_URL)
        return client.latest_currency_rates

    def update_rates(self):
        if self.rates is None:
            self.rates = self.get_rates()

    def _update_exchange_rates(self, currency_sender: str, currency_receiver: str):
        client = Client(currency_exchange_api_key=config.CURRENCY_EXCHANGE_API_KEY)
        if client.latest_currency_rates is None:
            client.get_latest_currency_rates(config.CURRENCY_EXCHANGE_API_URL)

        receiver_rate_by_dollar = client.latest_currency_rates.get(currency_receiver)
        sender_rate_by_dollar = client.latest_currency_rates.get(currency_sender)

        exchange_rate = round(receiver_rate_by_dollar / sender_rate_by_dollar, 2)
        self.exchange_rates[(currency_sender, currency_receiver,)] = exchange_rate

    def convent_money_from_sender_to_receiver(self, currency_sender: str, currency_receiver: str, amount_sent: float):
        while True:
            try:
                rate = self.exchange_rates[(currency_sender, currency_receiver,)]
            except KeyError:
                self._update_exchange_rates(currency_sender=currency_sender, currency_receiver=currency_receiver)
            else:
                return round(amount_sent * rate, 2)
