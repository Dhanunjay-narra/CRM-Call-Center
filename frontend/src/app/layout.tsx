'use client';

import React, { useState } from 'react';
import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Navbar from '@/components/layout/Navbar';
import SoftphoneModal from '@/components/softphone/SoftphoneModal';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [isSoftphoneOpen, setIsSoftphoneOpen] = useState(false);

  return (
    <html lang="en">
      <head>
        <title>CallSphere CRM - Intelligent Call Center &amp; CRM Platform</title>
        <meta name="description" content="Unified Enterprise CRM + Contact Center + Omnichannel Communication" />
      </head>
      <body className="flex h-screen overflow-hidden bg-slate-50 text-slate-900">
        {/* Left Navigation Sidebar */}
        <Sidebar />

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Navbar */}
          <Navbar onOpenSoftphone={() => setIsSoftphoneOpen(true)} />

          {/* Page View Container */}
          <main className="flex-1 overflow-y-auto p-6 bg-slate-50">
            {children}
          </main>
        </div>

        {/* Persistent Floating WebRTC Softphone Dialer */}
        <SoftphoneModal
          isOpen={isSoftphoneOpen}
          onClose={() => setIsSoftphoneOpen(false)}
        />
      </body>
    </html>
  );
}
