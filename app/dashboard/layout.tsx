"use client";
import { useState } from "react";
import DashboardNavbar from "@/components/layout/DashboardNavbar";
import DashboardSidebar from "@/components/layout/DashboardSidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: "var(--color-bg-page)" }}>
      <DashboardNavbar onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div style={{ display: "flex", flex: 1 }}>
        <DashboardSidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <main style={{ flex: 1, padding: "32px 24px", minWidth: 0 }}>
          {children}
        </main>
      </div>

      <style>{`
        @media (max-width: 767px) {
          main { padding: 20px 16px !important; }
        }
      `}</style>
    </div>
  );
}
