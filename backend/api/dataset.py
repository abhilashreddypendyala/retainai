import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.schemas.dataset import DatasetAnalysisResponse
from backend.pipeline.pipeline import run_dataset_intelligence
from backend.utils.logger import logger

router = APIRouter(prefix="/dataset", tags=["Dataset Intelligence"])

@router.post("/analyze", response_model=DatasetAnalysisResponse)
async def analyze_dataset_endpoint(file: UploadFile = File(...)):
    """
    Ingest a raw retail transaction dataset (CSV or XLSX), run Stage 1 (Preprocessing)
    and Stage 2 (Analytics ML Inference), and return complete business intelligence metrics.
    Operates strictly in-memory without mutating database records.
    """
    filename = file.filename.lower() if file.filename else "dataset.csv"
    if not (filename.endswith('.csv') or filename.endswith('.xlsx') or filename.endswith('.xls')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file format. Only CSV and Excel (.xlsx, .xls) files are supported for Dataset Intelligence."
        )

    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        if filename.endswith('.csv'):
            try:
                df_raw = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            except UnicodeDecodeError:
                df_raw = pd.read_csv(io.BytesIO(contents), encoding='latin-1')
        else:
            xl = pd.ExcelFile(io.BytesIO(contents))
            # Intelligently pick standard Year 2010-2011 sheet if present in full Online Retail workbook
            target_sheet = "Year 2010-2011" if "Year 2010-2011" in xl.sheet_names else xl.sheet_names[0]
            df_raw = xl.parse(target_sheet)

    except Exception as e:
        logger.error(f"Failed to read file {filename}: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse tabular data from uploaded file: {str(e)}")

    try:
        logger.info(f"Executing Dataset Intelligence pipeline for {filename} ({len(df_raw)} rows)...")
        results = run_dataset_intelligence(df_raw)
        logger.info(f"Successfully analyzed {results['kpi_summary']['total_customers']} customers from {filename}.")
        return results
    except (ValueError, AssertionError) as ve:
        logger.warning(f"Dataset validation error for {filename}: {str(ve)}")
        raise HTTPException(status_code=400, detail=f"Dataset validation error: {str(ve)}")
    except Exception as exc:
        logger.error(f"Unhandled pipeline failure for {filename}: {str(exc)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during analytical execution: {str(exc)}")
