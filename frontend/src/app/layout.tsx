import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cloud OmniChannel CRM & Call Center Portal",
  description: "Real-time ACD Telephony, WebRTC Calling, SLA Tickets & Customer 360",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
