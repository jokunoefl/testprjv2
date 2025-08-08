from sqlalchemy.orm import Session
import models, schemas
from typing import List, Optional

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

def get_pdfs_by_school(db: Session, school: str, skip: int = 0, limit: int = 100):
    return db.query(models.PDF).filter(models.PDF.school == school).offset(skip).limit(limit).all()

def get_distinct_schools(db: Session):
    """全ての学校名を重複なしで取得"""
    result = db.query(models.PDF.school).distinct().all()
    return [school[0] for school in result if school[0]]

def get_pdf_by_filename(db: Session, filename: str):
    return db.query(models.PDF).filter(models.PDF.filename == filename).first()

def get_pdf_by_id(db: Session, pdf_id: int):
    return db.query(models.PDF).filter(models.PDF.id == pdf_id).first()

def update_pdf(db: Session, pdf_id: int, pdf_update: dict):
    """PDFのメタデータを更新する"""
    db_pdf = db.query(models.PDF).filter(models.PDF.id == pdf_id).first()
    if db_pdf:
        for key, value in pdf_update.items():
            if hasattr(db_pdf, key):
                setattr(db_pdf, key, value)
        db.commit()
        db.refresh(db_pdf)
    return db_pdf

def delete_pdf(db: Session, pdf_id: int) -> bool:
    """PDFレコードをデータベースから削除する。関連する質問も削除する。"""
    try:
        print(f"=== PDF削除処理開始: ID {pdf_id} ===")
        
        # PDFレコードを取得
        db_pdf = db.query(models.PDF).filter(models.PDF.id == pdf_id).first()
        if not db_pdf:
            print(f"PDFが見つかりません: ID {pdf_id}")
            return False
        
        print(f"PDF情報: ID {pdf_id}, ファイル名: {db_pdf.filename}")
        
        # まず関連する質問を削除（カスケードが効く場合は不要だが、保険として実行）
        related_questions = db.query(models.Question).filter(models.Question.pdf_id == pdf_id).all()
        if related_questions:
            print(f"関連する質問を {len(related_questions)} 件削除します...")
            for question in related_questions:
                db.delete(question)
            # まず子テーブルの削除を確定
            db.commit()
        
        # PDFレコードを削除
        print("PDFレコードを削除中...")
        db.delete(db_pdf)
        db.commit()
        print(f"PDF削除完了: ID {pdf_id}")
        return True
    except Exception as e:
        print(f"PDF削除エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

# QuestionType CRUD operations
def create_question_type(db: Session, question_type: schemas.QuestionTypeCreate):
    db_question_type = models.QuestionType(**question_type.dict())
    db.add(db_question_type)
    db.commit()
    db.refresh(db_question_type)
    return db_question_type

def get_question_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.QuestionType).offset(skip).limit(limit).all()

def get_question_type_by_id(db: Session, question_type_id: int):
    return db.query(models.QuestionType).filter(models.QuestionType.id == question_type_id).first()

def get_question_type_by_name(db: Session, name: str):
    return db.query(models.QuestionType).filter(models.QuestionType.name == name).first()

# Question CRUD operations
def create_question(db: Session, question: schemas.QuestionCreate):
    db_question = models.Question(**question.dict())
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_questions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Question).offset(skip).limit(limit).all()

def get_questions_by_pdf_id(db: Session, pdf_id: int):
    return db.query(models.Question).filter(models.Question.pdf_id == pdf_id).all()

def get_question_by_id(db: Session, question_id: int):
    return db.query(models.Question).filter(models.Question.id == question_id).first()

def update_question(db: Session, question_id: int, question_update: dict):
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question:
        for key, value in question_update.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int):
    db_question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if db_question:
        db.delete(db_question)
        db.commit()
        return True
    return False

def create_multiple_questions(db: Session, questions: List[schemas.QuestionCreate]):
    """複数の問題を一括で作成"""
    db_questions = []
    for question in questions:
        db_question = models.Question(**question.dict())
        db.add(db_question)
        db_questions.append(db_question)
    db.commit()
    for db_question in db_questions:
        db.refresh(db_question)
    return db_questions
