'use client';

import React from 'react';

export default function SystemStatus() {
  return (
    <>
      {/* System Status Panel */}
      <div className="hud-panel" id="system-status-panel">
        <div className="hud-panel-title">SYSTEM_STATUS</div>

        <div>
          <div className="status-metric">
            <span className="status-metric-label">CPU_LOAD</span>
            <span className="status-metric-value flicker">24.8%</span>
          </div>
          <div className="status-bar-track">
            <div
              className="status-bar-fill cyan"
              style={{ width: '24.8%' }}
            />
          </div>
        </div>

        <div style={{ marginTop: '18px' }}>
          <div className="status-metric">
            <span className="status-metric-label">RAM_ALLOC</span>
            <span className="status-metric-value flicker">12.1GB</span>
          </div>
          <div className="status-bar-track">
            <div
              className="status-bar-fill green"
              style={{ width: '37.8%' }}
            />
          </div>
        </div>
      </div>

      {/* Active Threads Panel */}
      <div className="hud-panel" id="active-threads-panel">
        <div className="hud-panel-title">ACTIVE_THREADS</div>
        <ul className="thread-list">
          <li className="thread-item">
            <span className="thread-dot active" />
            <span className="thread-label">THREAD_049_LISTENER</span>
          </li>
          <li className="thread-item">
            <span className="thread-dot active" />
            <span className="thread-label">NODE_SYNC_UPSTREAM</span>
          </li>
          <li className="thread-item">
            <span className="thread-dot warning" />
            <span className="thread-label highlight">PARSING_EXTERNAL_EXEC</span>
          </li>
        </ul>
      </div>
    </>
  );
}
