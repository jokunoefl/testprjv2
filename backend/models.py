from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PDF(Base):
    __tablename__ = "pdfs"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    school = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
