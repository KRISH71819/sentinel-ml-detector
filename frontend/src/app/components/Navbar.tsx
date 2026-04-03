'use client';

import React from 'react';

export default function Navbar() {
  return (
    <nav className="navbar" id="sentinel-navbar">
      <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
        <span className="navbar-brand">Sentinel-Defense</span>
        <ul className="navbar-links">
          <li>
            <a className="navbar-link active" id="nav-threat-intel">
              THREAT_INTEL
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
}
