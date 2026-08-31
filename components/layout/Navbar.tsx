"use client";
import { useState } from "react";
import Link from "next/link";
import { Menu, X, Leaf, Globe } from "lucide-react";

const navLinks = [
  { label: "Features", labelHi: "सुविधाएं", href: "#features" },
  { label: "How It Works", labelHi: "कैसे काम करता है", href: "#how-it-works" },
  { label: "Centres", labelHi: "केंद्र", href: "#centres" },
  { label: "About", labelHi: "हमारे बारे में", href: "#about" },
];

export default function Navbar({ lang, onToggleLang }: { lang: "en" | "hi"; onToggleLang: () => void }) {
  const [open, setOpen] = useState(false);
  const isHindi = lang === "hi";

  return (
    <header
      style={{
        position: "sticky",
        top: 0,
        zIndex: 50,
        background: "rgba(255,255,255,0.95)",
        backdropFilter: "blur(8px)",
        borderBottom: "1px solid var(--color-divider)",
        boxShadow: "var(--shadow-sm)",
      }}
    >
      <div className="page-container" style={{ display: "flex", alignItems: "center", height: 64, gap: 16 }}>
        {/* Logo */}
        <Link
          href="/"
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            textDecoration: "none",
            flex: "0 0 auto",
          }}
        >
          <span
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              width: 36,
              height: 36,
              background: "var(--color-primary-btn)",
              borderRadius: 8,
              color: "#fff",
            }}
          >
            <Leaf size={20} />
          </span>
          <span style={{ display: "flex", flexDirection: "column", lineHeight: 1 }}>
            <span style={{ fontWeight: 700, fontSize: 15, color: "var(--color-primary-dark)" }}>
              Krishka Vachana
            </span>
            <span style={{ fontSize: 10, color: "var(--color-text-muted)", fontWeight: 500, letterSpacing: "0.03em" }}>
              {isHindi ? "कृषक वचन" : "Farmer's Promise"}
            </span>
          </span>
        </Link>

        {/* Desktop Nav */}
        <nav
          style={{ display: "flex", alignItems: "center", gap: 4, marginLeft: "auto" }}
          className="hidden-mobile"
        >
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              style={{
                padding: "8px 12px",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 500,
                color: "var(--color-text-secondary)",
                textDecoration: "none",
                transition: "background 0.15s, color 0.15s",
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLElement).style.background = "var(--color-primary-bg)";
                (e.currentTarget as HTMLElement).style.color = "var(--color-primary)";
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLElement).style.background = "transparent";
                (e.currentTarget as HTMLElement).style.color = "var(--color-text-secondary)";
              }}
            >
              {isHindi ? l.labelHi : l.label}
            </a>
          ))}
        </nav>

        {/* Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginLeft: 16 }} className="hidden-mobile">
          <button
            id="lang-toggle-btn"
            onClick={onToggleLang}
            className="btn btn-secondary"
            style={{ height: 36, padding: "0 12px", fontSize: 13, gap: 6 }}
            aria-label="Toggle language"
          >
            <Globe size={15} />
            {isHindi ? "English" : "हिंदी"}
          </button>
          <Link href="/login" className="btn btn-secondary" style={{ height: 36, padding: "0 16px", fontSize: 13 }}>
            {isHindi ? "लॉग इन" : "Login"}
          </Link>
          <Link href="/register" className="btn btn-primary" style={{ height: 36, padding: "0 16px", fontSize: 13 }}>
            {isHindi ? "शुरू करें" : "Get Started"}
          </Link>
        </div>

        {/* Mobile hamburger */}
        <div style={{ marginLeft: "auto", display: "none" }} className="show-mobile">
          <button
            onClick={onToggleLang}
            className="btn btn-ghost"
            style={{ height: 36, padding: "0 8px" }}
            aria-label="Toggle language"
          >
            <Globe size={16} />
          </button>
          <button
            id="mobile-menu-btn"
            onClick={() => setOpen(!open)}
            className="btn btn-ghost"
            style={{ height: 36, padding: "0 8px" }}
            aria-label="Open menu"
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {open && (
        <div
          style={{
            borderTop: "1px solid var(--color-divider)",
            background: "#fff",
            padding: "12px 16px 20px",
            display: "flex",
            flexDirection: "column",
            gap: 4,
          }}
        >
          {navLinks.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={() => setOpen(false)}
              style={{
                padding: "12px 12px",
                borderRadius: 8,
                fontSize: 15,
                fontWeight: 500,
                color: "var(--color-text-secondary)",
                textDecoration: "none",
              }}
            >
              {isHindi ? l.labelHi : l.label}
            </a>
          ))}
          <div style={{ height: 1, background: "var(--color-divider)", margin: "8px 0" }} />
          <Link href="/login" className="btn btn-secondary" onClick={() => setOpen(false)}>
            {isHindi ? "लॉग इन" : "Login"}
          </Link>
          <Link href="/register" className="btn btn-primary" onClick={() => setOpen(false)}>
            {isHindi ? "शुरू करें" : "Get Started"}
          </Link>
        </div>
      )}

      <style>{`
        @media (min-width: 768px) { .hidden-mobile { display: flex !important; } .show-mobile { display: none !important; } }
        @media (max-width: 767px) { .hidden-mobile { display: none !important; } .show-mobile { display: flex !important; } }
      `}</style>
    </header>
  );
}
