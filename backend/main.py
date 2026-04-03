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
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "xgboost_malware_model.json")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the XGBoost model once at startup."""
    global model
    abs_model_path = os.path.abspath(MODEL_PATH)
    if not os.path.exists(abs_model_path):
        raise RuntimeError(
            f"Model file not found at {abs_model_path}. "
            "Ensure xgboost_malware_model.json is in the website/ root directory."
        )

    print(f"[Sentinel-Defense] Loading XGBoost model from {abs_model_path} ...")
    model = xgb.Booster()
    model.load_model(abs_model_path)
    print(f"[Sentinel-Defense] Model loaded successfully. Ready for inference.")
    yield
    print("[Sentinel-Defense] Shutting down.")


# ── App initialization ────────────────────────────────────────────────────
app = FastAPI(
    title="Sentinel-Defense Malware Detection API",
    description="Deep-packet heuristic analysis for PE binaries using XGBoost + EMBER",
    version="2.4.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health endpoint ───────────────────────────────────────────────────────
@app.get("/api/health")
async def health_check():
    return {
        "status": "operational",
        "model_loaded": model is not None,
        "service": "Sentinel-Defense",
    }


# ── Scan endpoint ─────────────────────────────────────────────────────────
@app.post("/api/scan")
async def scan_file(file: UploadFile = File(...)):
    """
    Accept a PE binary (.exe or .dll), extract EMBER features,
    run XGBoost inference, and return the threat assessment.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Service unavailable.")

    # Validate file extension early
    if file.filename:
        _, ext = os.path.splitext(file.filename)
        if ext.lower() not in {'.exe', '.dll'}:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "INVALID_FILE_TYPE",
                    "message": f"File type '{ext}' is not supported. Please upload a .exe or .dll file.",
                }
            )

    # Create a temp directory for this scan
    temp_dir = tempfile.mkdtemp(prefix="sentinel_scan_")
    temp_path = os.path.join(temp_dir, file.filename or f"upload_{uuid.uuid4().hex}")

    try:
        # Save uploaded file to disk
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        scan_start = time.time()

        # Extract EMBER features (2,381 dimensions)
        features = extract_features(temp_path)

        # Wrap features in DMatrix for native Booster
        dmatrix = xgb.DMatrix(features)

        # Run XGBoost native inference
        probabilities = model.predict(dmatrix)
        confidence_score_raw = float(probabilities[0])

        scan_duration_ms = round((time.time() - scan_start) * 1000)

        # Determine result
        is_malicious = confidence_score_raw > 0.5
        confidence_score = round(confidence_score_raw * 100, 1)  # malicious probability

        # Extract additional PE metadata for the UI
        pe_metadata = get_pe_metadata(temp_path)

        # Get file size
        file_size = os.path.getsize(temp_path)

        return JSONResponse(content={
            "filename": file.filename,
            "file_size_bytes": file_size,
            "is_malicious": is_malicious,
            "confidence_score": confidence_score,
            "scan_duration_ms": scan_duration_ms,
            "detection_type": pe_metadata["detection_type"],
            "risk_assessment": pe_metadata["risk_assessment"],
            "features_extracted": 2381,
            "model_version": "EMBER-2018_XGBoost_v1",
        })

    except NotPEFileError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_PE_FILE",
                "message": str(e),
            }
        )

    except FeatureExtractionError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "FEATURE_EXTRACTION_FAILED",
                "message": str(e),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_SCAN_ERROR",
                "message": f"An unexpected error occurred during scanning: {str(e)}",
            }
        )

    finally:
        # Always clean up the temporary file
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# ── Run directly ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
