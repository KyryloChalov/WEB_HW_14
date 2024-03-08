from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.conf.config import settings


def reset_db():
    """
    Complete deletion of tables from the database and creation of new ones.
    no param
    """
    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine


def check_tables():
    """
    getting a list of all database tables (if they exist)
    no param
    """
    tables_metadata = MetaData()
    tables_metadata.reflect(bind=engine)
    existing_tables = tables_metadata.tables.keys()

    if not existing_tables:
        reset_db()


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

check_tables()


SessionLocal = sessionmaker(
    expire_on_commit=True, autocommit=False, autoflush=False, bind=engine
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
