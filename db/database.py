from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


def create_sql_lite_engine(path: str | None = None):
    # if path is None:
    #     path = settings.sqlite_database_url

    # if not path:
    #     raise ValueError("SQLITE_database_url environment variable is not set")

    return create_engine(f"sqlite:///{path}")


engine = create_sql_lite_engine("chatbox.db")
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    if Session is None:
        raise ValueError("Database not configured.")
    db = Session()
    try:
        yield db
    finally:
        db.close()
