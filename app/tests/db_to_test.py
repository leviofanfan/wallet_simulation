from sqlalchemy import URL
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from app.api import get_db
from app.config import config
from app.database.database import Base, engine
from app.main import app

url_object = URL.create(
    "postgresql+psycopg2",
    username=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
    database=config.DB_NAME
)

Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        TestingSessionLocal()
    finally:
        TestingSessionLocal().close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)