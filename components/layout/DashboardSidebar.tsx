"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  CalendarCheck,
  Users,
  CreditCard,
  Settings,
  Leaf,
  X,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

export default function DashboardSidebar({ open, onClose }: SidebarProps) {
  const pathname = usePathname();
  const { isHindi } = useLanguage();

  const navItems = [
    { label: isHindi ? "डैशबोर्ड" : "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { label: isHindi ? "मेरी बुकिंग" : "My Bookings", href: "/dashboard/booking", icon: CalendarCheck },
    { label: isHindi ? "कतार स्थिति" : "Queue Status", href: "/dashboard/queue", icon: Users },
    { label: isHindi ? "भुगतान" : "Payments", href: "/dashboard/payments", icon: CreditCard },
    { label: isHindi ? "सेटिंग्स" : "Settings", href: "/dashboard/settings", icon: Settings },
  ];

  return (
    <>
      {/* Overlay for mobile */}
      {open && (
        <div
          onClick={onClose}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.35)",
            zIndex: 40,
            display: "none",
          }}
          className="sidebar-overlay"
        />
      )}

      <aside
        style={{
          width: 240,
          background: "var(--color-bg-card)",
          borderRight: "1px solid var(--color-divider)",
          display: "flex",
          flexDirection: "column",
          flexShrink: 0,
          height: "100%",
          position: "sticky",
          top: 64,
        }}
        className={`dashboard-sidebar ${open ? "sidebar-open" : ""}`}
      >
        {/* Mobile close */}
        <div
          className="sidebar-mobile-header"
          style={{ display: "none", justifyContent: "space-between", alignItems: "center", padding: "16px 16px 8px" }}
        >
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: 32,
                height: 32,
                background: "var(--color-primary-btn)",
                borderRadius: 8,
                color: "#fff",
              }}
            >
              <Leaf size={18} />
            </span>
            <span style={{ fontWeight: 700, fontSize: 14, color: "var(--color-primary-dark)" }}>Krishka Vachana</span>
          </span>
          <button onClick={onClose} className="btn btn-ghost" style={{ height: 36, width: 36, padding: 0 }} aria-label="Close menu">
            <X size={20} />
          </button>
        </div>

        {/* Nav */}
        <nav style={{ padding: "12px 12px", display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
          {navItems.map(({ label, href, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                onClick={onClose}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  height: 44,
                  padding: "0 12px",
                  borderRadius: 8,
                  fontSize: 14,
                  fontWeight: active ? 600 : 500,
                  textDecoration: "none",
                  color: active ? "var(--color-primary-dark)" : "var(--color-text-secondary)",
                  background: active ? "var(--color-primary-light)" : "transparent",
                  position: "relative",
                  transition: "background 0.15s, color 0.15s",
                }}
              >
                {active && (
                  <span
                    style={{
                      position: "absolute",
                      left: 0,
                      top: "50%",
                      transform: "translateY(-50%)",
                      width: 3,
                      height: 24,
                      background: "var(--color-primary-btn)",
                      borderRadius: "0 4px 4px 0",
                    }}
                  />
                )}
                <Icon size={20} color={active ? "var(--color-primary-btn)" : undefined} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div style={{ padding: "16px 12px", borderTop: "1px solid var(--color-divider)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", borderRadius: 8, background: "var(--color-primary-bg)" }}>
            <span
              style={{
                width: 36,
                height: 36,
                borderRadius: "9999px",
                background: "var(--color-primary-light)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontWeight: 700,
                fontSize: 14,
                color: "var(--color-primary-dark)",
                flexShrink: 0,
              }}
            >
              RS
            </span>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                Ramesh Singh
              </div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>ID: KV-2024-0471</div>
            </div>
          </div>
        </div>
      </aside>

      <style>{`
        @media (max-width: 1023px) {
          .dashboard-sidebar {
            position: fixed !important;
            top: 0 !important;
            left: -240px;
            height: 100vh !important;
            z-index: 50;
            transition: left 0.25s ease;
            box-shadow: var(--shadow-lg);
          }
          .dashboard-sidebar.sidebar-open {
            left: 0;
          }
          .sidebar-overlay { display: block !important; }
          .sidebar-mobile-header { display: flex !important; }
        }
      `}</style>
    </>
  );
}
