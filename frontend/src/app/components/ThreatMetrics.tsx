'use client';

import React, { useState, useEffect } from 'react';

interface ThreatMetricsProps {
  scanCount: number;
  lastScanDuration: number | null;
}

export default function ThreatMetrics({ scanCount, lastScanDuration }: ThreatMetricsProps) {
  const [vulnCount, setVulnCount] = useState(1_200_000);

  // Simulate live counter increments
  useEffect(() => {
    const interval = setInterval(() => {
      setVulnCount((prev) => prev + Math.floor(Math.random() * 3));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const formatVulnCount = (n: number): string => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
    return n.toString();
  };

  return (
    <>
      {/* Vulnerabilities Patched */}
      <div className="hud-panel metric-card" id="metric-vulnerabilities">
        <div className="metric-label">VULNERABILITIES_PATCHED</div>
        <div className="metric-value cyan flicker">
          {formatVulnCount(vulnCount)}
          <span className="icon">⚙</span>
        </div>
      </div>

      {/* Average Scan Speed */}
      <div className="hud-panel metric-card" id="metric-scan-speed">
        <div className="metric-label">AVG._SCAN_SPEED</div>
        <div className="metric-value">
          {lastScanDuration !== null ? lastScanDuration : 142}
          <span className="unit">MS</span>
        </div>
      </div>

      {/* Neural Nodes Active */}
      <div className="hud-panel metric-card" id="metric-neural-nodes">
        <div className="metric-label">NEURAL_NODES_ACTIVE</div>
        <div className="metric-value flicker">
          {(2381 + scanCount * 17).toLocaleString()}
        </div>
      </div>

      {/* Global Sync */}
      <div className="hud-panel metric-card" id="metric-global-sync">
        <div className="metric-label">GLOBAL_SYNC</div>
        <div className="live-indicator">
          <span className="live-dot" />
          <span className="live-text">LIVE</span>
        </div>
      </div>
    </>
  );
}
