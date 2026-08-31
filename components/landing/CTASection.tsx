"use client";
import Link from "next/link";
import { ArrowRight, Phone, Printer } from "lucide-react";

export default function CTASection({ lang }: { lang: "en" | "hi" }) {
  const isHindi = lang === "hi";
  return (
    <section
      id="about"
      style={{
        padding: "80px 0",
        background: `linear-gradient(135deg, var(--color-primary-dark) 0%, var(--color-primary) 100%)`,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div
        aria-hidden
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage: `radial-gradient(circle at 1px 1px, rgba(255,255,255,0.05) 1px, transparent 0)`,
          backgroundSize: "32px 32px",
          pointerEvents: "none",
        }}
      />

      <div className="page-container" style={{ position: "relative", textAlign: "center" }}>
        <span
          className="badge"
          style={{
            marginBottom: 20,
            display: "inline-flex",
            background: "rgba(255,255,255,0.12)",
            color: "#a8f0c6",
            border: "1px solid rgba(168,240,198,0.3)",
          }}
        >
          {isHindi ? "शुरू करें" : "Get Started Today"}
        </span>

        <h2
          className="text-display"
          style={{ color: "#fff", marginBottom: 16, maxWidth: 560, margin: "0 auto 16px" }}
        >
          {isHindi
            ? "आज ही Krishka Vachana से जुड़ें"
            : "Join Krishka Vachana Today"}
        </h2>
        <p
          className="text-body-lg"
          style={{
            color: "rgba(255,255,255,0.78)",
            maxWidth: 460,
            margin: "0 auto 40px",
          }}
        >
          {isHindi
            ? "12,000+ किसान पहले से जुड़े हैं। अब आपकी बारी है।"
            : "12,000+ farmers are already using it. Be part of the movement."}
        </p>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            justifyContent: "center",
            marginBottom: 40,
          }}
        >
          <Link
            href="/register"
            id="cta-register-btn"
            className="btn"
            style={{
              height: 48,
              padding: "0 28px",
              fontSize: 15,
              fontWeight: 700,
              background: "#fff",
              color: "var(--color-primary-dark)",
            }}
          >
            {isHindi ? "मुफ़्त में शुरू करें" : "Start for Free"}
            <ArrowRight size={17} />
          </Link>
          <Link
            href="/login"
            id="cta-login-btn"
            className="btn"
            style={{
              height: 48,
              padding: "0 28px",
              fontSize: 15,
              background: "rgba(255,255,255,0.12)",
              color: "#fff",
              border: "1px solid rgba(255,255,255,0.25)",
            }}
          >
            {isHindi ? "लॉग इन करें" : "Already have an account?"}
          </Link>
        </div>

        {/* Offline access note */}
        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 24,
            justifyContent: "center",
          }}
        >
          {[
            { icon: <Printer size={16} />, en: "Print tokens at any kiosk", hi: "किसी भी कियोस्क पर टोकन प्रिंट करें" },
            { icon: <Phone size={16} />, en: "Works on basic phones via SMS", hi: "SMS से साधारण फ़ोन पर भी काम करता है" },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                color: "rgba(255,255,255,0.65)",
                fontSize: 13,
                fontWeight: 500,
              }}
            >
              {item.icon}
              {isHindi ? item.hi : item.en}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
