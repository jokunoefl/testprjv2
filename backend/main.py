from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import models, schemas, crud, database
from fastapi.middleware.cors import CORSMiddleware
import os
import pdf_utils
from fastapi.responses import FileResponse
from typing import List

app = FastAPI()

# CORS設定（React/Streamlitからのアクセス用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    database.init_db()
    # デフォルトの問題タイプを作成
    db = database.SessionLocal()
    try:
        default_types = [
            {"name": "選択問題", "description": "選択肢から正解を選ぶ問題"},
            {"name": "記述問題", "description": "文章で答える問題"},
            {"name": "計算問題", "description": "計算をして答える問題"},
            {"name": "図表問題", "description": "図や表を見て答える問題"},
            {"name": "作文問題", "description": "作文を書く問題"}
        ]
        for type_data in default_types:
            existing = crud.get_question_type_by_name(db, type_data["name"])
            if not existing:
                crud.create_question_type(db, schemas.QuestionTypeCreate(**type_data))
    finally:
        db.close()

@app.post("/pdfs/", response_model=schemas.PDFOut)
def create_pdf(pdf: schemas.PDFCreate, db: Session = Depends(get_db)):
    return crud.create_pdf(db, pdf)

@app.get("/pdfs/", response_model=list[schemas.PDFOut])
def read_pdfs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_pdfs(db, skip=skip, limit=limit)

@app.post("/upload_pdf/", response_model=schemas.PDFOut)
def upload_pdf(
    url: str = Form(...),
    school: str = Form(...),
    subject: str = Form(...),
    year: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        pdf_in = schemas.PDFCreate(
            url=url,
            school=school,
            subject=subject,
            year=year,
            filename=filename
        )
        return crud.create_pdf(db, pdf_in)
    except ValueError as e:
        # ファイル名重複エラーの場合、アップロードされたファイルを削除
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他のエラーの場合も、アップロードされたファイルを削除
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="アップロードに失敗しました")

@app.post("/download_pdf/", response_model=schemas.PDFOut)
async def download_pdf_from_url_endpoint(
    url: str = Form(...),
    school: str = Form(None),
    subject: str = Form(None),
    year: int = Form(None),
    db: Session = Depends(get_db)
):
    # PDFをダウンロード
    filename, error = await pdf_utils.download_pdf_from_url(url, UPLOAD_DIR)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # メタデータを抽出（指定されていない場合）
    if not school or not subject or not year:
        metadata = pdf_utils.extract_metadata_from_url(url)
        school = school or metadata['school']
        subject = subject or metadata['subject']
        year = year or metadata['year']
    
    try:
        # DBに保存
        pdf_in = schemas.PDFCreate(
            url=url,
            school=school,
            subject=subject,
            year=year,
            filename=filename
        )
        return crud.create_pdf(db, pdf_in)
    except ValueError as e:
        # ファイル名重複エラーの場合、ダウンロードされたファイルを削除
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他のエラーの場合も、ダウンロードされたファイルを削除
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail="ダウンロードに失敗しました")

@app.post("/crawl_pdfs/")
async def crawl_pdfs_from_url(
    url: str = Form(...),
    school: str = Form(None),
    subject: str = Form(None),
    year: int = Form(None),
    db: Session = Depends(get_db)
):
    """
    WebサイトをクローリングしてPDFリンクを抽出し、ダウンロードする
    """
    try:
        # サイトをクローリングしてPDFをダウンロード
        downloaded_files, error = await pdf_utils.crawl_and_download_pdfs(url, UPLOAD_DIR)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        if not downloaded_files:
            raise HTTPException(status_code=404, detail="PDFファイルが見つかりませんでした")
        
        # ダウンロードされたPDFをDBに登録
        saved_pdfs = []
        for filename in downloaded_files:
            try:
                # メタデータを抽出（指定されていない場合）
                if not school or not subject or not year:
                    metadata = pdf_utils.extract_metadata_from_url(url)
                    pdf_school = school or metadata['school']
                    pdf_subject = subject or metadata['subject']
                    pdf_year = year or metadata['year']
                else:
                    pdf_school = school
                    pdf_subject = subject
                    pdf_year = year
                
                # DBに保存
                pdf_in = schemas.PDFCreate(
                    url=url,  # 元のサイトURL
                    school=pdf_school,
                    subject=pdf_subject,
                    year=pdf_year,
                    filename=filename
                )
                saved_pdf = crud.create_pdf(db, pdf_in)
                saved_pdfs.append(saved_pdf)
                
            except ValueError as e:
                # ファイル名重複エラーの場合、ファイルを削除
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"ファイル名重複: {filename} - {str(e)}")
            except Exception as e:
                # その他のエラーの場合も、ファイルを削除
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"DB保存エラー: {filename} - {str(e)}")
        
        return {
            "message": f"{len(saved_pdfs)}個のPDFファイルをダウンロード・保存しました",
            "downloaded_files": [pdf.filename for pdf in saved_pdfs],
            "total_found": len(downloaded_files),
            "successfully_saved": len(saved_pdfs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"クローリングに失敗しました: {str(e)}")

@app.get("/pdfs/{pdf_id}/view")
def view_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """
    PDFファイルを表示する
    """
    pdf = db.query(models.PDF).filter(models.PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDFが見つかりません")
    
    file_path = os.path.join(UPLOAD_DIR, pdf.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDFファイルが見つかりません")
    
    return FileResponse(file_path, media_type='application/pdf')

@app.get("/pdfs/{pdf_id}")
def get_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """
    PDFのメタデータを取得する
    """
    pdf = db.query(models.PDF).filter(models.PDF.id == pdf_id).first()
    if not pdf:
        raise HTTPException(status_code=404, detail="PDFが見つかりません")
    
    return pdf

# QuestionType エンドポイント
@app.post("/question-types/", response_model=schemas.QuestionTypeOut)
def create_question_type(question_type: schemas.QuestionTypeCreate, db: Session = Depends(get_db)):
    return crud.create_question_type(db, question_type)

@app.get("/question-types/", response_model=List[schemas.QuestionTypeOut])
def get_question_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_question_types(db, skip=skip, limit=limit)

@app.get("/question-types/{question_type_id}", response_model=schemas.QuestionTypeOut)
def get_question_type(question_type_id: int, db: Session = Depends(get_db)):
    question_type = crud.get_question_type_by_id(db, question_type_id)
    if not question_type:
        raise HTTPException(status_code=404, detail="問題タイプが見つかりません")
    return question_type

# Question エンドポイント
@app.post("/questions/", response_model=schemas.QuestionOut)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db, question)

@app.get("/questions/", response_model=List[schemas.QuestionOut])
def get_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_questions(db, skip=skip, limit=limit)

@app.get("/questions/{question_id}", response_model=schemas.QuestionOut)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = crud.get_question_by_id(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="問題が見つかりません")
    return question

@app.get("/pdfs/{pdf_id}/questions", response_model=List[schemas.QuestionOut])
def get_questions_by_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """
    PDFに関連する問題一覧を取得
    """
    pdf = crud.get_pdf_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDFが見つかりません")
    return crud.get_questions_by_pdf_id(db, pdf_id)

@app.put("/questions/{question_id}", response_model=schemas.QuestionOut)
def update_question(question_id: int, question_update: dict, db: Session = Depends(get_db)):
    """
    問題を更新
    """
    question = crud.update_question(db, question_id, question_update)
    if not question:
        raise HTTPException(status_code=404, detail="問題が見つかりません")
    return question

@app.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """
    問題を削除
    """
    success = crud.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="問題が見つかりません")
    return {"message": "問題を削除しました"}

# PDFから問題を抽出するエンドポイント
@app.post("/pdfs/{pdf_id}/extract-questions")
def extract_questions_from_pdf(pdf_id: int, db: Session = Depends(get_db)):
    """
    PDFから問題を自動抽出してデータベースに登録
    """
    # PDFを取得
    pdf = crud.get_pdf_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDFが見つかりません")
    
    # PDFファイルのパス
    file_path = os.path.join(UPLOAD_DIR, pdf.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDFファイルが見つかりません")
    
    try:
        # PDFから問題を抽出
        extracted_questions = pdf_utils.extract_questions_from_pdf(file_path, pdf.subject)
        
        if not extracted_questions:
            return {"message": "問題を抽出できませんでした", "extracted_count": 0}
        
        # デフォルトの問題タイプを取得
        default_question_type = crud.get_question_type_by_name(db, "記述問題")
        if not default_question_type:
            # デフォルトタイプが存在しない場合は最初のタイプを使用
            question_types = crud.get_question_types(db, limit=1)
            if not question_types:
                raise HTTPException(status_code=500, detail="問題タイプが設定されていません")
            default_question_type = question_types[0]
        
        # 問題をデータベースに登録
        created_questions = []
        for extracted_q in extracted_questions:
            question_data = schemas.QuestionCreate(
                pdf_id=pdf_id,
                question_type_id=default_question_type.id,
                question_number=extracted_q['question_number'],
                question_text=extracted_q['question_text'],
                answer_text=extracted_q.get('answer_text'),
                difficulty_level=extracted_q.get('difficulty_level'),
                points=extracted_q.get('points'),
                page_number=extracted_q.get('page_number'),
                extracted_text=extracted_q.get('extracted_text')
            )
            created_question = crud.create_question(db, question_data)
            created_questions.append(created_question)
        
        return {
            "message": f"{len(created_questions)}個の問題を抽出・登録しました",
            "extracted_count": len(created_questions),
            "questions": [schemas.QuestionOut.from_orm(q) for q in created_questions]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"問題抽出に失敗しました: {str(e)}")

@app.get("/pdfs/{pdf_id}/with-questions", response_model=schemas.PDFWithQuestions)
def get_pdf_with_questions(pdf_id: int, db: Session = Depends(get_db)):
    """
    PDFとその関連問題を一緒に取得
    """
    pdf = crud.get_pdf_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDFが見つかりません")
    
    questions = crud.get_questions_by_pdf_id(db, pdf_id)
    
    # PDFWithQuestionsスキーマに変換
    pdf_with_questions = schemas.PDFWithQuestions(
        id=pdf.id,
        url=pdf.url,
        school=pdf.school,
        subject=pdf.subject,
        year=pdf.year,
        filename=pdf.filename,
        created_at=pdf.created_at,
        questions=[schemas.QuestionOut.from_orm(q) for q in questions]
    )
    
    return pdf_with_questions
