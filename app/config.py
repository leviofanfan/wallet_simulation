import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    BASE_DIR = os.path.dirname(os.path.abspath(__name__))
    TEST_DIR = os.path.join(BASE_DIR, "tests")

    DB_PASSWORD: str = os.environ.get("DB_PASSWORD")
    HOST: str = os.environ.get("HOST", "localhost")
    PORT: int = os.environ.get("PORT", 3000)

    DB_HOST: str = os.environ.get("HOST", "localhost")
    DB_PORT: int = os.environ.get("DB_PORT", 8000)
    DB_NAME: str = os.environ.get("DB_NAME", "online_wallet")

    CURRENCY_EXCHANGE_API_URL: str = os.environ.get("CURRENCY_EXCHANGE_API_URL", "")
    CURRENCY_EXCHANGE_API_KEY: str = os.environ.get("CURRENCY_EXCHANGE_API_KEY", "")

    class Config:
        env_file = ".env"


@lru_cache()
def get_config():
    return Settings()