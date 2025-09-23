"""
TAUI FastAPI Server
Provides RESTful API for Taiwan AI Usage Index calculations.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import pandas as pd
import uvicorn
from pathlib import Path
import tempfile
import logging
from datetime import datetime

# Import TAUI modules
from ..metrics.aui import AUICalculator
from ..labeling.onets import classify_task_llm
from ..labeling.mode import classify_mode_llm
from ..viz.figures import TAUIVisualizer
from ..report.make_report import TAUIReportGenerator, ReportConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Taiwan AI Usage Index API",
    description="RESTful API for TAUI calculations and analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AUIRequest(BaseModel):
    """Request model for AUI calculation."""
    regions: List[str]
    conversation_counts: List[int]
    unique_users: List[int]
    total_populations: List[int]
    working_age_populations: List[int]
    min_conversations: Optional[int] = 15
    min_users: Optional[int] = 5

class ClassificationRequest(BaseModel):
    """Request model for text classification."""
    text: str
    model: Optional[str] = "mock"

class AUIResponse(BaseModel):
    """Response model for AUI results."""
    results: List[Dict[str, Any]]
    summary: Dict[str, float]
    timestamp: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: str

# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with health check."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/v1/aui/calculate", response_model=AUIResponse)
async def calculate_aui(request: AUIRequest):
    """
    Calculate AUI scores for given regional data.

    Args:
        request: AUI calculation request with regional data

    Returns:
        AUI scores and statistics
    """
    try:
        # Create DataFrame from request data
        data = pd.DataFrame({
            'region': request.regions,
            'conversation_count': request.conversation_counts,
            'unique_users': request.unique_users,
            'total_population': request.total_populations,
            'working_age_population': request.working_age_populations
        })

        # Calculate AUI
        calculator = AUICalculator(
            min_conversations=request.min_conversations,
            min_users=request.min_users
        )
        results = calculator.process_data(data)

        # Prepare response
        return AUIResponse(
            results=results.to_dict('records'),
            summary={
                'mean_aui': float(results['aui_score'].mean()) if len(results) > 0 else 0.0,
                'max_aui': float(results['aui_score'].max()) if len(results) > 0 else 0.0,
                'min_aui': float(results['aui_score'].min()) if len(results) > 0 else 0.0,
                'filtered_count': len(data) - len(results)
            },
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"AUI calculation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/classify/task")
async def classify_task(request: ClassificationRequest):
    """
    Classify text into O*NET task categories.

    Args:
        request: Classification request with text

    Returns:
        Task classification result
    """
    try:
        result = classify_task_llm(request.text, model=request.model)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Task classification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/classify/mode")
async def classify_mode(request: ClassificationRequest):
    """
    Classify collaboration mode.

    Args:
        request: Classification request with text

    Returns:
        Mode classification result
    """
    try:
        result = classify_mode_llm(request.text, model=request.model)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Mode classification error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """
    Upload CSV file for processing.

    Args:
        file: CSV file with regional data

    Returns:
        Processing status and file info
    """
    try:
        # Save uploaded file
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir) / file.filename

        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)

        # Read and validate CSV
        df = pd.read_csv(temp_path)
        required_columns = ['region', 'conversation_count', 'unique_users',
                          'total_population', 'working_age_population']

        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict('records')
        })

    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/visualize/demo")
async def generate_demo_visualizations():
    """
    Generate demo visualizations.

    Returns:
        Status of visualization generation
    """
    try:
        visualizer = TAUIVisualizer(language='zh-TW')
        chart_paths = visualizer.generate_all_charts()

        return JSONResponse(content={
            "status": "success",
            "charts": chart_paths
        })

    except Exception as e:
        logger.error(f"Visualization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/report/generate")
async def generate_report(language: str = "zh-TW"):
    """
    Generate analysis report.

    Args:
        language: Report language (zh-TW or en-US)

    Returns:
        Path to generated report
    """
    try:
        config = ReportConfig(language=language)
        generator = TAUIReportGenerator(config)
        report_path = generator.generate_full_report()

        return JSONResponse(content={
            "status": "success",
            "report_path": report_path,
            "language": language
        })

    except Exception as e:
        logger.error(f"Report generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/download/{file_type}/{filename}")
async def download_file(file_type: str, filename: str):
    """
    Download generated files.

    Args:
        file_type: Type of file (report, figure, data)
        filename: Name of file to download

    Returns:
        File download
    """
    try:
        base_paths = {
            "report": Path("report"),
            "figure": Path("figures"),
            "data": Path("data/processed")
        }

        if file_type not in base_paths:
            raise HTTPException(status_code=400, detail="Invalid file type")

        file_path = base_paths[file_type] / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run server
def main():
    """Main entry point for the API server."""
    uvicorn.run(
        "src.api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()