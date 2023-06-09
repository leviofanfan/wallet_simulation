from sqlalchemy import URL, create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

from config import config

url_object = URL.create(
    "postgresql",
    username=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    port=config.DB_PORT,
    database=config.DB_NAME
)

engine = create_engine(url_object)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
