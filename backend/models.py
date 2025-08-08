from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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
    
    # リレーションシップ
    questions = relationship(
        "Question",
        back_populates="pdf",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class QuestionType(Base):
    __tablename__ = "question_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    questions = relationship("Question", back_populates="question_type")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(Integer, ForeignKey("pdfs.id", ondelete="CASCADE"), nullable=False)
    question_type_id = Column(Integer, ForeignKey("question_types.id"), nullable=False)
    question_number = Column(String, nullable=False)  # 問題番号（例：1, 2, 3-1, 3-2）
    question_text = Column(Text, nullable=False)  # 問題文
    answer_text = Column(Text)  # 解答文
    difficulty_level = Column(Integer)  # 難易度（1-5）
    points = Column(Float)  # 配点
    page_number = Column(Integer)  # PDFのページ番号
    extracted_text = Column(Text)  # 抽出されたテキスト
    keywords = Column(Text)  # キーワード（カンマ区切り）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # リレーションシップ
    pdf = relationship("PDF", back_populates="questions")
    question_type = relationship("QuestionType", back_populates="questions")
