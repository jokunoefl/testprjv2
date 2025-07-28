from pydantic import BaseModel
from datetime import datetime

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
