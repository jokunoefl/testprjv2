from sqlalchemy.orm import Session
import models, schemas

def create_pdf(db: Session, pdf: schemas.PDFCreate):
    # ファイル名の重複チェック
    existing_pdf = db.query(models.PDF).filter(models.PDF.filename == pdf.filename).first()
    if existing_pdf:
        raise ValueError(f"ファイル名 '{pdf.filename}' は既に存在します")
    
    db_pdf = models.PDF(**pdf.dict())
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf

def get_pdfs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.PDF).offset(skip).limit(limit).all()

def get_pdf_by_filename(db: Session, filename: str):
    return db.query(models.PDF).filter(models.PDF.filename == filename).first()
