from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PDFBase(BaseModel):
    url: str
    school: str
    subject: str
    year: int
    filename: str

class PDFCreate(PDFBase):
    pass

class PDFOut(PDFBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionTypeBase(BaseModel):
    name: str
    description: Optional[str] = None

class QuestionTypeCreate(QuestionTypeBase):
    pass

class QuestionTypeOut(QuestionTypeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    pdf_id: int
    question_type_id: int
    question_number: str
    question_text: str
    answer_text: Optional[str] = None
    difficulty_level: Optional[int] = None
    points: Optional[float] = None
    page_number: Optional[int] = None
    extracted_text: Optional[str] = None
    keywords: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(QuestionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionWithRelations(QuestionOut):
    pdf: PDFOut
    question_type: QuestionTypeOut

class PDFWithQuestions(PDFOut):
    questions: List[QuestionOut] = []
