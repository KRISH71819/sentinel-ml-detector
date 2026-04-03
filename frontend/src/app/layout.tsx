import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Sentinel-Defense — Malware Detection System',
  description: 'Deep-packet heuristic analysis for PE binaries. AI-powered threat detection using XGBoost neural classification on the EMBER-2018 feature set.',
  keywords: ['malware detection', 'threat analysis', 'PE analysis', 'XGBoost', 'EMBER', 'cybersecurity'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
