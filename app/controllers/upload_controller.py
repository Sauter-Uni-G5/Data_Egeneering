from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from app.services.upload_service import upload_folder_to_gcs
import shutil
import os
from tempfile import TemporaryDirectory

router = APIRouter()

@router.post("/data/upload-folder")
async def upload_folder_data(
    folder: UploadFile = File(..., description="Pasta compactada (ZIP) contendo os arquivos")
):
    if not folder.filename.endswith('.zip'):
        raise HTTPException(
            status_code=400, 
            detail="Apenas arquivos ZIP são aceitos"
        )
    
    try:
        with TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, folder.filename)
            
            with open(zip_path, "wb") as f:
                f.write(await folder.read())
            
            extract_path = os.path.join(temp_dir, "extracted")
            shutil.unpack_archive(zip_path, extract_path, "zip")
            
            result = upload_folder_to_gcs(folder_path=extract_path)
            
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Pasta enviada com sucesso",
                    "folder_path": result["folder_path"],
                    "upload_date": result["upload_date"],
                    "files_uploaded": result["files_uploaded"]
                }
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro durante o upload: {str(e)}"
        )