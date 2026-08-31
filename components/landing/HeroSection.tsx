"use client";
import Link from "next/link";
import {
  ArrowRight,
  CalendarCheck,
  ClipboardList,
  Banknote,
  Users,
} from "lucide-react";

const stats = [
  { value: "12,000+", label: "Farmers Served", labelHi: "किसान" },
  { value: "48", label: "Proc. Centres", labelHi: "खरीद केंद्र" },
  { value: "₹ 0", label: "Hidden Charges", labelHi: "छिपा शुल्क" },
  { value: "98%", label: "On-time Slots", labelHi: "समय पर स्लॉट" },
];

const flowSteps = [
  { icon: <ClipboardList size={18} />, en: "Register Crop", hi: "फसल पंजीकरण" },
  { icon: <CalendarCheck size={18} />, en: "Book Smart Slot", hi: "स्मार्ट स्लॉट बुक करें" },
  { icon: <Users size={18} />, en: "Dynamic Queue", hi: "डायनामिक कतार" },
  { icon: <Banknote size={18} />, en: "Get Paid", hi: "भुगतान पाएं" },
];

export default function HeroSection({ lang }: { lang: "en" | "hi" }) {
  const isHindi = lang === "hi";

  return (
    <section
      id="hero"
      style={{
        background: `linear-gradient(160deg, var(--color-primary-dark) 0%, var(--color-primary) 50%, #268a52 100%)`,
        color: "#fff",
        padding: "80px 0 64px",
        position: "relative",
        overflow: "hidden",
      }}
    >
      {/* Subtle grid texture */}
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.06) 1px, transparent 0)`,
          backgroundSize: "28px 28px",
          pointerEvents: "none",
        }}
      />

      <div className="page-container" style={{ position: "relative" }}>
        {/* Language badge */}
        <div
          className="animate-fade-up"
          style={{ marginBottom: 24 }}
        >
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              background: "rgba(255,255,255,0.12)",
              border: "1px solid rgba(255,255,255,0.2)",
              borderRadius: 9999,
              padding: "4px 14px",
              fontSize: 12,
              fontWeight: 500,
              letterSpacing: "0.04em",
              backdropFilter: "blur(6px)",
            }}
          >
            🌾 {isHindi ? "कृषि खरीद का भविष्य" : "The Future of Agricultural Procurement"}
          </span>
        </div>

        {/* Headline */}
        <h1
          className="text-display animate-fade-up delay-100"
          style={{
            maxWidth: 640,
            marginBottom: 20,
            color: "#fff",
            letterSpacing: "-0.01em",
          }}
        >
          {isHindi
            ? <>अपनी फसल बेचें,<br /><span style={{ color: "#a8f0c6" }}>स्मार्ट तरीके से।</span></>
            : <>Sell Your Crop,<br /><span style={{ color: "#a8f0c6" }}>The Smart Way.</span></>}
        </h1>

        <p
          className="text-body-lg animate-fade-up delay-200"
          style={{
            maxWidth: 520,
            marginBottom: 36,
            color: "rgba(255,255,255,0.82)",
            lineHeight: "28px",
          }}
        >
          {isHindi
            ? "Krishka Vachana से खरीद केंद्र चुनें, स्लॉट बुक करें, रियल-टाइम कतार देखें और सीधे भुगतान पाएं।"
            : "Choose a procurement centre, book your slot, monitor the live queue, and receive transparent payments — all from one platform."}
        </p>

        {/* CTA Buttons */}
        <div
          className="animate-fade-up delay-300"
          style={{ display: "flex", flexWrap: "wrap", gap: 12, marginBottom: 56 }}
        >
          <Link
            href="/register"
            id="hero-register-btn"
            className="btn btn-primary"
            style={{
              height: 48,
              padding: "0 24px",
              fontSize: 15,
              background: "#fff",
              color: "var(--color-primary-dark)",
              fontWeight: 700,
            }}
          >
            {isHindi ? "अभी शुरू करें" : "Get Started Free"}
            <ArrowRight size={17} />
          </Link>
          <a
            href="#how-it-works"
            id="hero-learn-btn"
            className="btn"
            style={{
              height: 48,
              padding: "0 24px",
              fontSize: 15,
              background: "rgba(255,255,255,0.12)",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.25)",
              backdropFilter: "blur(6px)",
            }}
          >
            {isHindi ? "और जानें" : "Learn How It Works"}
          </a>
        </div>

        {/* Flow Steps */}
        <div
          className="animate-fade-up delay-400"
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 8,
            alignItems: "center",
            marginBottom: 48,
          }}
        >
          {flowSteps.map((step, i) => (
            <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                  background: "rgba(255,255,255,0.1)",
                  border: "1px solid rgba(255,255,255,0.18)",
                  borderRadius: 9999,
                  padding: "6px 14px",
                  fontSize: 13,
                  fontWeight: 500,
                  color: "rgba(255,255,255,0.92)",
                  backdropFilter: "blur(4px)",
                }}
              >
                <span style={{ opacity: 0.8 }}>{step.icon}</span>
                {isHindi ? step.hi : step.en}
              </div>
              {i < flowSteps.length - 1 && (
                <ArrowRight size={14} style={{ opacity: 0.45, flexShrink: 0 }} />
              )}
            </div>
          ))}
        </div>

        {/* Stats bar */}
        <div
          className="animate-fade-up delay-500"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
            gap: 1,
            background: "rgba(255,255,255,0.12)",
            border: "1px solid rgba(255,255,255,0.15)",
            borderRadius: 12,
            overflow: "hidden",
            backdropFilter: "blur(6px)",
          }}
        >
          {stats.map((s, i) => (
            <div
              key={i}
              style={{
                padding: "20px 16px",
                textAlign: "center",
                background: i % 2 === 0 ? "rgba(255,255,255,0.04)" : "transparent",
              }}
            >
              <div style={{ fontSize: 26, fontWeight: 700, color: "#a8f0c6", lineHeight: 1 }}>
                {s.value}
              </div>
              <div style={{ fontSize: 12, fontWeight: 500, color: "rgba(255,255,255,0.7)", marginTop: 4 }}>
                {isHindi ? s.labelHi : s.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom wave */}
      <div style={{ position: "absolute", bottom: -1, left: 0, right: 0, lineHeight: 0 }}>
        <svg viewBox="0 0 1440 56" preserveAspectRatio="none" style={{ width: "100%", height: 56 }}>
          <path d="M0,56 C360,0 1080,0 1440,56 L1440,56 L0,56 Z" fill="var(--color-bg-page)" />
        </svg>
      </div>
    </section>
  );
}
