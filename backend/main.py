import os
import shutil
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import crud, models, schemas
from database import SessionLocal, engine
import pdf_utils
import ai_analysis
from config import settings

app = FastAPI()

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# データベース依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# アップロードディレクトリの設定
UPLOAD_DIR = settings.UPLOAD_DIR

@app.on_event("startup")
def on_startup():
    print("アプリケーション起動中...")
    
    # 設定の検証
    if not settings.validate():
        print("設定エラー: アプリケーションを正常に起動できません。")
        return
    
    # アップロードディレクトリの作成
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    print(f"アップロードディレクトリ確認: {UPLOAD_DIR}")
    
    # データベースの初期化
    models.Base.metadata.create_all(bind=engine)
    
    # デフォルトの問題タイプを作成
    db = SessionLocal()
    try:
        default_types = [
            {"name": "選択問題", "description": "選択肢から正解を選ぶ問題"},
            {"name": "記述問題", "description": "文章で答える問題"},
            {"name": "計算問題", "description": "計算を必要とする問題"},
            {"name": "図表問題", "description": "図表を読み取る問題"}
        ]
        
        for type_data in default_types:
            existing = crud.get_question_type_by_name(db, type_data["name"])
            if not existing:
                crud.create_question_type(db, schemas.QuestionTypeCreate(**type_data))
                print(f"問題タイプ作成: {type_data['name']}")
    finally:
        db.close()
    
    print("アプリケーション起動完了")

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
    print(f"PDFアップロード開始: {file.filename}")
    print(f"URL: {url}, 学校: {school}, 科目: {subject}, 年度: {year}")
    
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        # ファイルサイズをチェック
        file_content = file.file.read()
        file_size = len(file_content)
        print(f"ファイルサイズ: {file_size} bytes")
        
        # ファイルを保存
        with open(file_path, "wb") as f:
            f.write(file_content)
        print(f"ファイル保存完了: {file_path}")
        
        # DBに保存
        pdf_in = schemas.PDFCreate(
            url=url,
            school=school,
            subject=subject,
            year=year,
            filename=filename
        )
        result = crud.create_pdf(db, pdf_in)
        print(f"DB保存成功: {filename}")
        return result
    except ValueError as e:
        # ファイル名重複エラーの場合、アップロードされたファイルを削除
        print(f"ファイル名重複エラー: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"重複ファイル削除: {file_path}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他のエラーの場合も、アップロードされたファイルを削除
        print(f"アップロードエラー: {str(e)}")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"エラーファイル削除: {file_path}")
        raise HTTPException(status_code=500, detail=f"アップロードに失敗しました: {str(e)}")

@app.post("/download_pdf/", response_model=schemas.PDFOut)
async def download_pdf_from_url_endpoint(
    url: str = Form(...),
    school: str = Form(None),
    subject: str = Form(None),
    year: int = Form(None),
    db: Session = Depends(get_db)
):
    print(f"PDFダウンロード開始: {url}")
    print(f"メタデータ: 学校={school}, 科目={subject}, 年度={year}")
    
    # PDFをダウンロード
    filename, error = await pdf_utils.download_pdf_from_url(url, UPLOAD_DIR)
    if error:
        print(f"ダウンロードエラー: {error}")
        raise HTTPException(status_code=400, detail=error)
    
    print(f"ダウンロード成功: {filename}")
    
    # メタデータを抽出（指定されていない場合）
    if not school or not subject or not year:
        print("メタデータを自動抽出中...")
        metadata = pdf_utils.extract_metadata_from_url(url)
        school = school or metadata['school']
        subject = subject or metadata['subject']
        year = year or metadata['year']
        print(f"抽出されたメタデータ: 学校={school}, 科目={subject}, 年度={year}")
    
    try:
        # DBに保存
        pdf_in = schemas.PDFCreate(
            url=url,
            school=school,
            subject=subject,
            year=year,
            filename=filename
        )
        result = crud.create_pdf(db, pdf_in)
        print(f"DB保存成功: {filename}")
        return result
    except ValueError as e:
        # ファイル名重複エラーの場合、ダウンロードされたファイルを削除
        print(f"ファイル名重複エラー: {str(e)}")
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"重複ファイル削除: {file_path}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他のエラーの場合も、ダウンロードされたファイルを削除
        print(f"DB保存エラー: {str(e)}")
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"エラーファイル削除: {file_path}")
        raise HTTPException(status_code=500, detail=f"ダウンロードに失敗しました: {str(e)}")

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
        print(f"クローリング開始: {url}")
        
        # サイトをクローリングしてPDFをダウンロード
        downloaded_files, error = await pdf_utils.crawl_and_download_pdfs(url, UPLOAD_DIR)
        
        if error:
            print(f"クローリングエラー: {error}")
            raise HTTPException(status_code=400, detail=error)
        
        print(f"ダウンロード完了: {len(downloaded_files)}個のファイル")
        
        if not downloaded_files:
            raise HTTPException(status_code=404, detail="PDFファイルが見つかりませんでした")
        
        # ダウンロードされたPDFをDBに登録
        saved_pdfs = []
        failed_saves = []
        
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
                print(f"DB保存成功: {filename}")
                
            except ValueError as e:
                # ファイル名重複エラーの場合、ファイルを削除
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"ファイル名重複: {filename} - {str(e)}")
                failed_saves.append(f"重複: {filename}")
            except Exception as e:
                # その他のエラーの場合も、ファイルを削除
                file_path = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                print(f"DB保存エラー: {filename} - {str(e)}")
                failed_saves.append(f"保存失敗: {filename}")
        
        print(f"保存完了: {len(saved_pdfs)}/{len(downloaded_files)}個成功")
        
        # 結果メッセージを詳細化
        message = f"{len(saved_pdfs)}個のPDFファイルをダウンロード・保存しました"
        if failed_saves:
            message += f" (失敗: {len(failed_saves)}個)"
        
        return {
            "message": message,
            "downloaded_files": [pdf.filename for pdf in saved_pdfs],
            "total_found": len(downloaded_files),
            "successfully_saved": len(saved_pdfs),
            "failed_saves": failed_saves
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"予期しないエラー: {str(e)}")
        import traceback
        traceback.print_exc()
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

@app.get("/pdfs/{pdf_id}/with-questions", response_model=schemas.PDFWithQuestions)
def get_pdf_with_questions(pdf_id: int, db: Session = Depends(get_db)):
    pdf = crud.get_pdf_by_id(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    questions = crud.get_questions_by_pdf_id(db, pdf_id)
    return schemas.PDFWithQuestions(
        id=pdf.id,
        url=pdf.url,
        school=pdf.school,
        subject=pdf.subject,
        year=pdf.year,
        filename=pdf.filename,
        created_at=pdf.created_at,
        questions=questions
    )

# 問題タイプ関連のエンドポイント
@app.get("/question-types/", response_model=List[schemas.QuestionTypeOut])
def get_question_types(db: Session = Depends(get_db)):
    return crud.get_question_types(db)

@app.post("/question-types/", response_model=schemas.QuestionTypeOut)
def create_question_type(question_type: schemas.QuestionTypeCreate, db: Session = Depends(get_db)):
    return crud.create_question_type(db, question_type)

# 問題関連のエンドポイント
@app.get("/questions/", response_model=List[schemas.QuestionWithRelations])
def get_questions(db: Session = Depends(get_db)):
    return crud.get_questions(db)

@app.get("/questions/{question_id}", response_model=schemas.QuestionWithRelations)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = crud.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@app.post("/questions/", response_model=schemas.QuestionOut)
def create_question(question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    return crud.create_question(db, question)

@app.put("/questions/{question_id}", response_model=schemas.QuestionOut)
def update_question(question_id: int, question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    updated_question = crud.update_question(db, question_id, question)
    if not updated_question:
        raise HTTPException(status_code=404, detail="Question not found")
    return updated_question

@app.delete("/questions/{question_id}")
def delete_question(question_id: int, db: Session = Depends(get_db)):
    success = crud.delete_question(db, question_id)
    if not success:
        raise HTTPException(status_code=404, detail="Question not found")
    return {"message": "Question deleted successfully"}

@app.post("/questions/batch")
def create_multiple_questions(questions: List[schemas.QuestionCreate], db: Session = Depends(get_db)):
    created_questions = crud.create_multiple_questions(db, questions)
    return {"message": f"Successfully created {len(created_questions)} questions", "questions": created_questions}

@app.post("/pdfs/{pdf_id}/analyze")
async def analyze_pdf_with_ai(pdf_id: int, db: Session = Depends(get_db)):
    """
    PDFをClaudeで分析する
    """
    try:
        # PDF情報を取得
        pdf = crud.get_pdf_by_id(db, pdf_id)
        if not pdf:
            raise HTTPException(status_code=404, detail="PDFが見つかりません")
        
        # PDFファイルパスを構築
        pdf_path = os.path.join(UPLOAD_DIR, pdf.filename)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDFファイルが見つかりません")
        
        # AI分析を実行
        result = await ai_analysis.analyze_pdf_with_claude(
            pdf_id=pdf_id,
            pdf_path=pdf_path,
            school=pdf.school,
            subject=pdf.subject,
            year=pdf.year
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析中にエラーが発生しました: {str(e)}")
