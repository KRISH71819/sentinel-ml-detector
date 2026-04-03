"""
Sentinel-Defense Malware Detection API
FastAPI backend serving XGBoost inference on PE binaries via EMBER feature extraction.
"""

import os
import uuid
import time
import tempfile
import shutil
from contextlib import asynccontextmanager

import numpy as np
import xgboost as xgb
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from feature_extractor import (
    extract_features,
    get_pe_metadata,
    NotPEFileError,
    FeatureExtractionError,
)

# ── Global model reference ────────────────────────────────────────────────
model: xgb.Booster | None = None
# This looks one level up from the 'backend' folder to find the model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "xgboost_malware_model.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the XGBoost model once at startup."""
    global model
    abs_model_path = os.path.abspath(MODEL_PATH)
    
    if not os.path.exists(abs_model_path):
        print(f"[ERROR] Model not found at: {abs_model_path}")
        # On Render, we want to know exactly what the file system looks like if it fails
        print(f"Current Directory: {os.getcwd()}")
        print(f"Directory Contents: {os.listdir(os.path.dirname(abs_model_path))}")
        raise RuntimeError("Model file missing.")

    print(f"[SENTINEL] Loading XGBoost model from {abs_model_path} ...")
    model = xgb.Booster()
    model.load_model(abs_model_path)
    print(f"[SENTINEL] Model loaded successfully. Ready for inference.")
    yield
    print("[SENTINEL] Shutting down.")


# ── App initialization ────────────────────────────────────────────────────
app = FastAPI(
    title="Sentinel-Defense Malware Detection API",
    lifespan=lifespan,
)

# FIXED: Correct way to add CORS in FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://sentinel-ml-detector-ziw4.vercel.app"  # Your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Base Routes ───────────────────────────────────────────────────────────
@app.get("/")
async def root():
    """Root endpoint for Render health checks."""
    return {
        "message": "Sentinel-Defense API is Online",
        "docs": "/docs"
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "model_loaded": model is not None,
    }


# ── Scan endpoint ─────────────────────────────────────────────────────────
@app.post("/api/scan")
async def scan_file(file: UploadFile = File(...)):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded.")

    if file.filename:
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in {'.exe', '.dll'}:
            raise HTTPException(
                status_code=400,
                detail={"message": f"File type '{ext}' is not supported."}
            )

    temp_dir = tempfile.mkdtemp(prefix="sentinel_scan_")
    temp_path = os.path.join(temp_dir, file.filename or f"upload_{uuid.uuid4().hex}")

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        scan_start = time.time()
        
        # 1. Extract 2,381 features
        features = extract_features(temp_path)

        # 2. Native XGBoost Inference
        dmatrix = xgb.DMatrix(features)
        probabilities = model.predict(dmatrix)
        confidence_score_raw = float(probabilities)

        # 3. Meta-analysis
        scan_duration_ms = round((time.time() - scan_start) * 1000)
        pe_metadata = get_pe_metadata(temp_path)
        
        return {
            "filename": file.filename,
            "file_size_bytes": os.path.getsize(temp_path),
            "is_malicious": confidence_score_raw > 0.5,
            "confidence_score": round(confidence_score_raw * 100, 1),
            "scan_duration_ms": scan_duration_ms,
            "detection_type": pe_metadata["detection_type"],
            "risk_assessment": pe_metadata["risk_assessment"],
            "features_extracted": 2381,
        }

    except NotPEFileError as e:
        raise HTTPException(status_code=400, detail={"message": str(e)})
    except FeatureExtractionError as e:
        raise HTTPException(status_code=422, detail={"message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"Internal Error: {str(e)}"})
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)