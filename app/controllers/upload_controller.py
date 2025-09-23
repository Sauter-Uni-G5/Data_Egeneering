from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.services.upload_service import upload_parquet_to_gcs

router = APIRouter()

@router.post("/data/upload-parquet")
async def upload_parquet_data(
    file: UploadFile = File(..., description="Arquivo Parquet em bytes"),
    dataset_name: str = Form(..., description="Nome do dataset (ex: weather, registry, hydro)")
):
    """
    Endpoint para receber dados Parquet em memória e salvar no bucket
    """
    
    # Validar se é arquivo parquet
    if not file.filename.endswith('.parquet'):
        raise HTTPException(
            status_code=400, 
            detail="Apenas arquivos .parquet são aceitos"
        )
    
    try:
        # Ler o conteúdo do arquivo em bytes
        parquet_bytes = await file.read()
        
        # Fazer upload para GCS
        result = upload_parquet_to_gcs(
            parquet_bytes=parquet_bytes,
            dataset_name=dataset_name,
            original_filename=file.filename
        )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Dados enviados com sucesso",
                "file_path": result["file_path"],
                "upload_date": result["upload_date"],
                "records_count": result.get("records_count")
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro durante o upload: {str(e)}"
        )