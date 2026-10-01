import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SWDL — SESI World Diplomacy League',
  description:
    'The largest Model UN of SESI. Represent nations, debate resolutions and build diplomatic agreements.',
  keywords: ['Model UN', 'ONU', 'SESI', 'Diplomacia', 'Simulação', 'Debate'],
  openGraph: {
    title: 'SWDL — SESI World Diplomacy League',
    description: 'The largest Model UN of SESI.',
    url: 'https://swdl.vercel.app',
    siteName: 'SWDL',
    locale: 'en_US',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
