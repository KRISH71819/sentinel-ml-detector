# Sentinel-Defense — Setup Instructions

## Prerequisites
- **Node.js** 18+ (for the frontend)
- **Python** 3.12 (for the backend)
- **Git** (to clone the EMBER repo)

---

## 1. Frontend Setup

```powershell
cd website\frontend

# Install dependencies
npm install

# Start the dev server (runs on http://localhost:3000)
npm run dev
```

---

## 2. Backend Setup

```powershell
cd website\backend

# Create a virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate

# Install Python dependencies
pip install -r requirements.txt

# Clone and install the EMBER library
git clone https://github.com/elastic/ember.git ember_repo
cd ember_repo
pip install -e .
cd ..

# Start the FastAPI server (runs on http://localhost:8000)
python main.py
```

> **Note:** The EMBER library needs `lief` which is already in `requirements.txt`.
> The model file `xgboost_malware_model.json` is expected at `website/xgboost_malware_model.json`.

---

## 3. Usage

1. Open http://localhost:3000 in your browser
2. Drag and drop a `.exe` or `.dll` file onto the AEGIS_DROP_ZONE
3. Click **INITIATE_INGESTION** to start the scan
4. View the threat assessment results

---

## API Reference

### `POST /api/scan`
Upload a PE binary for malware analysis.

**Request:** `multipart/form-data` with a `file` field.

**Response:**
```json
{
  "filename": "setup.exe",
  "file_size_bytes": 1048576,
  "is_malicious": true,
  "confidence_score": 97.3,
  "scan_duration_ms": 142,
  "detection_type": "PROCESS INJECTION: DETECTED",
  "risk_assessment": "API HOOKING: HIGH RISK",
  "features_extracted": 2381,
  "model_version": "EMBER-2018_XGBoost_v1"
}
```

### `GET /api/health`
Health check endpoint.
