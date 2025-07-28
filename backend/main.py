from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import models, schemas, crud, database
from fastapi.middleware.cors import CORSMiddleware
import os
import pdf_utils
from fastapi.responses import FileResponse

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
