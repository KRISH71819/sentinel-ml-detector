'use client';

import React, { useState, useCallback } from 'react';
import Navbar from './components/Navbar';
import DropZone from './components/DropZone';
import ScanResults, { ScanResult } from './components/ScanResults';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  // ── State ────────────────────────────────────────────────────────────
  const [file, setFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  // ── File selection ───────────────────────────────────────────────────
  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setResult(null);
    setError(null);
  }, []);

  // ── Scan execution ───────────────────────────────────────────────────
  const handleScan = useCallback(async () => {
    if (!file) return;

    setScanning(true);
    setResult(null);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE}/api/scan`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const message =
          errorData?.detail?.message ||
          errorData?.detail ||
          `Scan failed with status ${response.status}`;
        throw new Error(message);
      }

      const data: ScanResult = await response.json();
      setResult(data);
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : 'An unexpected error occurred during the scan.';
      setError(message);
    } finally {
      setScanning(false);
    }
  }, [file]);

  // ── Reset ────────────────────────────────────────────────────────────
  const handleReset = useCallback(() => {
    setFile(null);
    setResult(null);
    setError(null);
  }, []);

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <div className="sentinel-app" id="sentinel-app">
      <Navbar />

      <main className="sentinel-main" id="sentinel-main">
        {/* Center Content */}
        <section className="sentinel-center" id="center-content">
          {/* Drop Zone (shown when no result) */}
          {!result && (
            <DropZone
              file={file}
              scanning={scanning}
              dragActive={dragActive}
              onFileSelect={handleFileSelect}
              onDragActive={setDragActive}
              onScan={handleScan}
            />
          )}

          {/* Scan Results */}
          {result && (
            <ScanResults result={result} onReset={handleReset} />
          )}

          {/* Error Display */}
          {error && (
            <div className="error-panel" id="error-panel">
              <div className="error-title">SCAN_ERROR</div>
              <div className="error-message">{error}</div>
              <button className="error-dismiss" onClick={() => setError(null)}>
                DISMISS
              </button>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
