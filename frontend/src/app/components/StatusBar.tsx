'use client';

import React from 'react';

export default function StatusBar() {
  return (
    <footer className="status-bar" id="status-bar">
      <div className="status-bar-left">
        <span>CORE_NODE_STABLE // 127.0.0.1</span>
      </div>
      <div className="status-bar-right">
        <span className="status-bar-item active">
          NET_STAT:<span style={{ fontWeight: 700 }}> ACTIVE</span>
        </span>
        <span className="status-bar-item">
          <span className="label">NODES: </span>14
        </span>
        <span className="status-bar-item">
          <span className="label">LATENCY: </span>4MS
        </span>
      </div>
    </footer>
  );
}
