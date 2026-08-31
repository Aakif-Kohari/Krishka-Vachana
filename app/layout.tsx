import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Krishka Vachana – Smart Farmer Procurement Platform",
  description:
    "Krishka Vachana helps farmers book smart procurement slots, track their queue in real-time, and receive transparent payments — all in one place.",
  keywords: [
    "krishka vachana",
    "farmer procurement",
    "slot booking",
    "agriculture",
    "kisan",
  ],
  openGraph: {
    title: "Krishka Vachana",
    description: "Smart Farmer Procurement Platform",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
