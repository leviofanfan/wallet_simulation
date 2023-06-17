import requests
from requests.structures import CaseInsensitiveDict

class Client:
    def __init__(self, currency_exchange_api_key: str):
        self.currency_exchange_api_key = currency_exchange_api_key
        self.latest_currency_rates = None

    def get_latest_currency_rates(self, api_url: str):
        if self.latest_currency_rates is None:
            headers = CaseInsensitiveDict()
            headers["apikey"] = self.currency_exchange_api_key
            resp = requests.get(api_url, headers=headers)
            self.latest_currency_rates = resp.json()