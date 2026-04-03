'use client';

import React, { useRef, useCallback } from 'react';

interface DropZoneProps {
  file: File | null;
  scanning: boolean;
  dragActive: boolean;
  onFileSelect: (file: File) => void;
  onDragActive: (active: boolean) => void;
  onScan: () => void;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export default function DropZone({
  file,
  scanning,
  dragActive,
  onFileSelect,
  onDragActive,
  onScan,
}: DropZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === 'dragenter' || e.type === 'dragover') {
        onDragActive(true);
      } else if (e.type === 'dragleave') {
        onDragActive(false);
      }
    },
    [onDragActive]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      onDragActive(false);

      const droppedFile = e.dataTransfer.files?.[0];
      if (droppedFile) {
        onFileSelect(droppedFile);
      }
    },
    [onDragActive, onFileSelect]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = e.target.files?.[0];
      if (selectedFile) {
        onFileSelect(selectedFile);
      }
    },
    [onFileSelect]
  );

  const handleClick = useCallback(() => {
    if (!scanning) {
      inputRef.current?.click();
    }
  }, [scanning]);

  return (
    <div className="drop-zone-container" id="drop-zone-container">
      {/* Drop zone area */}
      <div
        className={`drop-zone ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleClick}
        id="drop-zone"
      >
        {/* File icon */}
        <svg className="drop-zone-icon" viewBox="0 0 48 48" fill="none">
          <rect x="8" y="4" width="32" height="40" rx="2" stroke="currentColor" strokeWidth="1.5" />
          <path d="M16 4V14H8" stroke="currentColor" strokeWidth="1.5" />
          <polyline
            points="24,18 24,32"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
          />
          <polyline
            points="18,24 24,18 30,24"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>

        <span className="drop-zone-title">AEGIS_DROP_ZONE</span>
        <span className="drop-zone-subtitle">
          INSERT BINARY OR DRAG .EXE / .DLL
          <br />
          FILES FOR DEEP-PACKET
          <br />
          HEURISTIC ANALYSIS
        </span>

        <input
          ref={inputRef}
          type="file"
          className="drop-zone-file-input"
          accept=".exe,.dll"
          onChange={handleInputChange}
          id="file-input"
        />
      </div>

      {/* Selected file display */}
      {file && !scanning && (
        <div className="drop-zone-selected" id="selected-file-info">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--cyan)" strokeWidth="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
          </svg>
          <span className="drop-zone-filename">{file.name}</span>
          <span className="drop-zone-filesize">({formatFileSize(file.size)})</span>
        </div>
      )}

      {/* Scan button */}
      <button
        className={`scan-button ${scanning ? 'scanning' : ''}`}
        disabled={!file || scanning}
        onClick={onScan}
        id="scan-button"
      >
        {scanning ? 'ANALYZING_BINARY...' : 'INITIATE_INGESTION'}
      </button>

      {/* Progress bar during scanning */}
      {scanning && (
        <div className="progress-container">
          <div className="progress-track">
            <div className="progress-bar" />
          </div>
          <div className="progress-label">
            EXTRACTING EMBER FEATURE VECTOR... 2,381 DIMENSIONS
          </div>
        </div>
      )}
    </div>
  );
}
