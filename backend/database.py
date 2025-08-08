from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
import models
import os

# 環境変数のDATABASE_URLを優先的に使用（未設定ならローカルsqlite）
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pdfs.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SQLiteの外部キー制約を有効にする
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    models.Base.metadata.create_all(bind=engine)
