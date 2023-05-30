from sqlalchemy import URL, create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_config



url_object = URL.create(
    "postgresql",
    username=get_config().db_username,
    password=get_config().db_password,
    host=get_config().db_host,
    port=get_config().db_port,
    database=get_config().db_name
)


engine = create_engine(url_object)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

Base.metadata.create_all(engine)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
