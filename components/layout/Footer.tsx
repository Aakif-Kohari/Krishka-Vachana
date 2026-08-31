"use client";
import { Leaf } from "lucide-react";

const links = {
  platform: {
    en: "Platform",
    hi: "प्लेटफ़ॉर्म",
    items: [
      { en: "Features", hi: "सुविधाएं", href: "#features" },
      { en: "How It Works", hi: "कैसे काम करता है", href: "#how-it-works" },
      { en: "Slot Booking", hi: "स्लॉट बुकिंग", href: "#" },
      { en: "Live Queue", hi: "लाइव कतार", href: "#" },
    ],
  },
  support: {
    en: "Support",
    hi: "सहायता",
    items: [
      { en: "Help Centre", hi: "सहायता केंद्र", href: "#" },
      { en: "Contact", hi: "संपर्क करें", href: "#" },
      { en: "Kiosk Locator", hi: "कियोस्क खोजें", href: "#" },
      { en: "SMS Helpline", hi: "SMS हेल्पलाइन", href: "#" },
    ],
  },
  legal: {
    en: "Legal",
    hi: "कानूनी",
    items: [
      { en: "Privacy Policy", hi: "गोपनीयता नीति", href: "#" },
      { en: "Terms of Use", hi: "उपयोग की शर्तें", href: "#" },
      { en: "Grievance Policy", hi: "शिकायत नीति", href: "#" },
    ],
  },
};

export default function Footer({ lang }: { lang: "en" | "hi" }) {
  const isHindi = lang === "hi";
  const year = new Date().getFullYear();

  return (
    <footer
      style={{
        background: "var(--color-primary-dark)",
        color: "rgba(255,255,255,0.75)",
        padding: "56px 0 32px",
      }}
    >
      <div className="page-container">
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr 1fr 1fr",
            gap: 40,
            marginBottom: 48,
          }}
          className="footer-grid"
        >
          {/* Brand */}
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
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
                <Leaf size={18} />
              </span>
              <span style={{ fontWeight: 700, fontSize: 16, color: "#fff" }}>
                Krishka Vachana
              </span>
            </div>
            <p style={{ fontSize: 14, lineHeight: "22px", maxWidth: 260, marginBottom: 20 }}>
              {isHindi
                ? "किसानों के लिए स्मार्ट खरीद — पारदर्शी, भरोसेमंद और सुलभ।"
                : "Smart procurement for farmers — transparent, trustworthy, and accessible."}
            </p>
            <div style={{ display: "flex", gap: 8 }}>
              {["कृषि", "किसान", "MSP"].map((tag) => (
                <span
                  key={tag}
                  style={{
                    padding: "3px 10px",
                    borderRadius: 9999,
                    fontSize: 11,
                    fontWeight: 500,
                    background: "rgba(255,255,255,0.08)",
                    color: "rgba(255,255,255,0.6)",
                    border: "1px solid rgba(255,255,255,0.12)",
                  }}
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Links */}
          {Object.values(links).map((col, i) => (
            <div key={i}>
              <p
                style={{
                  fontWeight: 600,
                  fontSize: 13,
                  color: "#fff",
                  marginBottom: 16,
                  letterSpacing: "0.04em",
                  textTransform: "uppercase",
                }}
              >
                {isHindi ? col.hi : col.en}
              </p>
              <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: 10 }}>
                {col.items.map((item, j) => (
                  <li key={j}>
                    <a
                      href={item.href}
                      style={{
                        fontSize: 14,
                        color: "rgba(255,255,255,0.65)",
                        textDecoration: "none",
                        transition: "color 0.15s",
                      }}
                      onMouseEnter={(e) =>
                        ((e.currentTarget as HTMLElement).style.color = "#a8f0c6")
                      }
                      onMouseLeave={(e) =>
                        ((e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.65)")
                      }
                    >
                      {isHindi ? item.hi : item.en}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div
          style={{
            borderTop: "1px solid rgba(255,255,255,0.1)",
            paddingTop: 24,
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            alignItems: "center",
            justifyContent: "space-between",
          }}
        >
          <p style={{ fontSize: 13, color: "rgba(255,255,255,0.45)" }}>
            © {year} Krishka Vachana.{" "}
            {isHindi ? "सभी अधिकार सुरक्षित।" : "All rights reserved."}
          </p>
          <p style={{ fontSize: 12, color: "rgba(255,255,255,0.35)" }}>
            {isHindi
              ? "भारत सरकार की कृषि नीतियों के अनुरूप।"
              : "Aligned with Government of India agricultural policies."}
          </p>
        </div>
      </div>

      <style>{`
        @media (max-width: 767px) {
          .footer-grid { grid-template-columns: 1fr 1fr !important; }
        }
        @media (max-width: 480px) {
          .footer-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </footer>
  );
}
