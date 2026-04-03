'use client';

import React from 'react';

export interface ScanResult {
  filename: string;
  file_size_bytes: number;
  is_malicious: boolean;
  confidence_score: number;
  scan_duration_ms: number;
  detection_type: string;
  risk_assessment: string;
  features_extracted: number;
  model_version: string;
}

interface ScanResultsProps {
  result: ScanResult;
  onReset: () => void;
}

export default function ScanResults({ result, onReset }: ScanResultsProps) {
  const isMalicious = result.is_malicious;
  const confidenceClass = isMalicious ? 'high' : 'low';
  const badgeClass = isMalicious ? 'malicious' : 'safe';
  const badgeText = isMalicious ? 'MALICIOUS' : 'SAFE';

  return (
    <div className="results-panel" id="scan-results-panel">
      {/* Header: filename + badge */}
      <div className="results-header">
        <div className="results-target">
          <span className="results-target-label">TARGET_OBJECT</span>
          <span className="results-target-name" id="result-filename">
            {result.filename}
          </span>
        </div>
        <div className={`results-badge ${badgeClass}`} id="result-badge">
          <span className="results-badge-dot" />
          {badgeText}
        </div>
      </div>

      {/* Threat level bar */}
      <div className="threat-section">
        <div className="threat-header">
          <span className="threat-label">THREAT_LEVEL_INTENSITY</span>
          <span className={`threat-value ${confidenceClass}`} id="result-confidence">
            {result.confidence_score}%
          </span>
        </div>
        <div className="threat-bar-track">
          <div
            className={`threat-bar-fill ${confidenceClass}`}
            style={{ width: `${result.confidence_score}%` }}
            id="threat-bar"
          />
        </div>
      </div>

      {/* Detection details grid */}
      <div className="detection-grid">
        <div className="detection-card" id="detection-type-card">
          <div className="detection-card-label">DETECTION_TYPE</div>
          <div className={`detection-card-value ${isMalicious ? 'danger' : 'success'}`}>
            {result.detection_type}
          </div>
        </div>
        <div className="detection-card" id="risk-assessment-card">
          <div className="detection-card-label">RISK_ASSESSMENT</div>
          <div className={`detection-card-value ${isMalicious ? 'danger' : 'success'}`}>
            {result.risk_assessment}
          </div>
        </div>
      </div>

      {/* Scan metadata */}
      <div className="detection-grid" style={{ marginBottom: '20px' }}>
        <div className="detection-card">
          <div className="detection-card-label">SCAN_DURATION</div>
          <div className="detection-card-value">
            {result.scan_duration_ms} MS
          </div>
        </div>
        <div className="detection-card">
          <div className="detection-card-label">FEATURES_ANALYZED</div>
          <div className="detection-card-value">
            {result.features_extracted.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Scan another */}
      <button
        className="scan-another-button"
        onClick={onReset}
        id="scan-another-button"
      >
        SCAN_ANOTHER_FILE
      </button>
    </div>
  );
}
