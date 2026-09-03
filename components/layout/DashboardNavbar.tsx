"use client";
import Link from "next/link";
import { Bell, Menu, Leaf, Search, ChevronDown, Globe } from "lucide-react";
import { useState } from "react";
import { useLanguage } from "@/context/LanguageContext";

interface DashboardNavbarProps {
  onMenuToggle: () => void;
}

export default function DashboardNavbar({ onMenuToggle }: DashboardNavbarProps) {
  const { lang, toggleLang, isHindi } = useLanguage();
  const [notifOpen, setNotifOpen] = useState(false);

  const notifications = isHindi
    ? [
        { id: 1, text: "5 सितंबर का आपका स्लॉट स्वीकृत हो गया है।", time: "2 घंटे पहले", unread: true },
        { id: 2, text: "₹12,400 का भुगतान खाते में जमा किया गया।", time: "कल", unread: true },
        { id: 3, text: "आपकी कतार स्थिति #3 पर अपडेट हुई।", time: "2 दिन पहले", unread: false },
      ]
    : [
        { id: 1, text: "Your slot for 5 Sep is confirmed.", time: "2 hrs ago", unread: true },
        { id: 2, text: "Payment of ₹12,400 credited.", time: "Yesterday", unread: true },
        { id: 3, text: "Queue position updated to #3.", time: "2 days ago", unread: false },
      ];

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <header
      style={{
        height: 64,
        position: "sticky",
        top: 0,
        zIndex: 30,
        background: "rgba(255,255,255,0.97)",
        backdropFilter: "blur(8px)",
        borderBottom: "1px solid var(--color-divider)",
        boxShadow: "var(--shadow-sm)",
        display: "flex",
        alignItems: "center",
        padding: "0 24px",
        gap: 16,
      }}
    >
      {/* Hamburger (tablet/mobile) */}
      <button
        id="dashboard-menu-btn"
        onClick={onMenuToggle}
        className="btn btn-ghost sidebar-toggle"
        style={{ height: 36, width: 36, padding: 0, display: "none" }}
        aria-label="Open menu"
      >
        <Menu size={20} />
      </button>

      {/* Logo */}
      <Link
        href="/dashboard"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          textDecoration: "none",
          flexShrink: 0,
        }}
      >
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
        <span style={{ fontWeight: 700, fontSize: 15, color: "var(--color-primary-dark)" }} className="logo-text">
          Krishka Vachana
        </span>
      </Link>

      {/* Search */}
      <div
        style={{
          flex: 1,
          maxWidth: 360,
          marginLeft: 16,
          position: "relative",
          display: "flex",
          alignItems: "center",
        }}
        className="search-bar"
      >
        <Search size={16} style={{ position: "absolute", left: 12, color: "var(--color-text-muted)" }} />
        <input
          type="text"
          placeholder={isHindi ? "बुकिंग, भुगतान खोजें..." : "Search bookings, payments..."}
          style={{
            width: "100%",
            height: 38,
            background: "var(--color-bg-light)",
            border: "1px solid var(--color-border)",
            borderRadius: 8,
            paddingLeft: 36,
            paddingRight: 12,
            fontSize: 14,
            color: "var(--color-text-main)",
            outline: "none",
          }}
        />
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Language Switcher */}
      <button
        onClick={toggleLang}
        className="btn btn-secondary"
        style={{ height: 36, padding: "0 12px", fontSize: 13, gap: 6 }}
        aria-label="Toggle language"
      >
        <Globe size={15} />
        {isHindi ? "English" : "हिंदी"}
      </button>

      {/* Notifications */}
      <div style={{ position: "relative" }}>
        <button
          id="notif-btn"
          className="btn btn-ghost"
          onClick={() => setNotifOpen(!notifOpen)}
          style={{ height: 36, width: 36, padding: 0, position: "relative" }}
          aria-label="Notifications"
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span
              style={{
                position: "absolute",
                top: 4,
                right: 4,
                width: 16,
                height: 16,
                borderRadius: "9999px",
                background: "var(--color-error)",
                color: "#fff",
                fontSize: 10,
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                border: "2px solid #fff",
              }}
            >
              {unreadCount}
            </span>
          )}
        </button>

        {notifOpen && (
          <>
            <div onClick={() => setNotifOpen(false)} style={{ position: "fixed", inset: 0, zIndex: 10 }} />
            <div
              style={{
                position: "absolute",
                top: 44,
                right: 0,
                width: 300,
                background: "#fff",
                borderRadius: 12,
                border: "1px solid var(--color-divider)",
                boxShadow: "var(--shadow-md)",
                zIndex: 20,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  padding: "12px 16px",
                  borderBottom: "1px solid var(--color-divider)",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span style={{ fontWeight: 600, fontSize: 14, color: "var(--color-text-main)" }}>
                  {isHindi ? "सूचनाएं" : "Notifications"}
                </span>
                <span className="badge badge-processing" style={{ fontSize: 11 }}>
                  {unreadCount} {isHindi ? "नया" : "new"}
                </span>
              </div>
              {notifications.map((n) => (
                <div
                  key={n.id}
                  style={{
                    padding: "12px 16px",
                    borderBottom: "1px solid var(--color-divider)",
                    background: n.unread ? "var(--color-primary-bg)" : "#fff",
                    cursor: "pointer",
                  }}
                >
                  <div style={{ fontSize: 13, color: "var(--color-text-main)", lineHeight: "18px", fontWeight: n.unread ? 500 : 400 }}>
                    {n.text}
                  </div>
                  <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginTop: 4 }}>{n.time}</div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* User */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer" }}>
        <span
          style={{
            width: 34,
            height: 34,
            borderRadius: "9999px",
            background: "var(--color-primary-light)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
            fontSize: 13,
            color: "var(--color-primary-dark)",
            flexShrink: 0,
          }}
        >
          RS
        </span>
        <div className="user-info" style={{ lineHeight: 1.3 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)" }}>Ramesh Singh</div>
          <div style={{ fontSize: 11, color: "var(--color-text-muted)" }}>KV-2024-0471</div>
        </div>
        <ChevronDown size={16} color="var(--color-text-muted)" />
      </div>

      <style>{`
        @media (max-width: 1023px) {
          .sidebar-toggle { display: flex !important; }
          .logo-text { display: none; }
          .search-bar { max-width: 160px !important; }
          .user-info { display: none; }
        }
        @media (max-width: 767px) {
          .search-bar { display: none !important; }
        }
      `}</style>
    </header>
  );
}
