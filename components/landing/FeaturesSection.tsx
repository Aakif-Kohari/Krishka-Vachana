"use client";
import {
  CalendarClock,
  QrCode,
  TrendingUp,
  MapPin,
  Users,
  FileText,
  Banknote,
  History,
} from "lucide-react";

interface Feature {
  icon: React.ReactNode;
  titleEn: string;
  titleHi: string;
  descEn: string;
  descHi: string;
  badge?: string;
  badgeHi?: string;
  badgeType?: "confirmed" | "waiting" | "processing" | "completed" | "cancelled";
}

const features: Feature[] = [
  {
    icon: <QrCode size={22} />,
    titleEn: "Aadhaar-Linked Farmer ID",
    titleHi: "आधार-लिंक्ड किसान पहचान",
    descEn: "Secure digital identity linked to Aadhaar. No paperwork, no queues at the counter.",
    descHi: "आधार से जुड़ी सुरक्षित डिजिटल पहचान। कोई कागज़ात नहीं, कोई काउंटर पर लाइन नहीं।",
    badge: "Secure",
    badgeHi: "सुरक्षित",
    badgeType: "confirmed",
  },
  {
    icon: <CalendarClock size={22} />,
    titleEn: "Smart Slot Booking",
    titleHi: "स्मार्ट स्लॉट बुकिंग",
    descEn: "Pick your crop, quantity, and preferred procurement centre. Get a confirmed time slot.",
    descHi: "अपनी फसल, मात्रा और केंद्र चुनें। पुष्ट समय-स्लॉट पाएं।",
    badge: "New",
    badgeHi: "नया",
    badgeType: "processing",
  },
  {
    icon: <TrendingUp size={22} />,
    titleEn: "Dynamic Queue System",
    titleHi: "डायनामिक कतार प्रणाली",
    descEn: "If a farmer is late, the queue auto-adjusts so no slot is wasted and no farmer is penalised.",
    descHi: "अगर कोई किसान देर से आता है तो कतार अपने आप ठीक हो जाती है।",
    badge: "Live",
    badgeHi: "लाइव",
    badgeType: "waiting",
  },
  {
    icon: <FileText size={22} />,
    titleEn: "Printable Tokens",
    titleHi: "प्रिंट करने योग्य टोकन",
    descEn: "No smartphone? No problem. Generate a printable token at the nearest kiosk.",
    descHi: "स्मार्टफ़ोन नहीं है? कोई बात नहीं। नज़दीकी कियोस्क से टोकन प्रिंट करें।",
    badgeType: "completed",
  },
  {
    icon: <MapPin size={22} />,
    titleEn: "Congestion Prediction",
    titleHi: "भीड़ की भविष्यवाणी",
    descEn: "AI-powered crowd forecasting alerts you a day before so you can choose a less busy centre.",
    descHi: "AI आधारित भीड़ पूर्वानुमान एक दिन पहले सूचित करता है।",
    badge: "AI",
    badgeHi: "एआई",
    badgeType: "processing",
  },
  {
    icon: <MapPin size={22} />,
    titleEn: "Alternative Centre Recommendation",
    titleHi: "वैकल्पिक केंद्र सुझाव",
    descEn: "Overcrowded centre? Get smart recommendations for nearby alternatives with available slots.",
    descHi: "एक केंद्र पर भीड़ है? पास के खाली केंद्रों के सुझाव पाएं।",
    badgeType: "confirmed",
  },
  {
    icon: <Users size={22} />,
    titleEn: "Village Cluster Booking",
    titleHi: "ग्राम समूह बुकिंग",
    descEn: "Same village? Book together. Group scheduling ensures farmers from one village arrive together.",
    descHi: "एक गांव के किसान मिलकर बुकिंग करें। समूह शेड्यूलिंग से सभी साथ पहुंचें।",
    badge: "Community",
    badgeHi: "समुदाय",
    badgeType: "confirmed",
  },
  {
    icon: <Banknote size={22} />,
    titleEn: "Payment Tracking",
    titleHi: "भुगतान ट्रैकिंग",
    descEn: "Track deductions, MSP rate, and payment status in real-time. Full transparency.",
    descHi: "कटौती, MSP दर और भुगतान स्थिति रियल-टाइम में देखें।",
    badgeType: "confirmed",
  },
  {
    icon: <History size={22} />,
    titleEn: "Historical Farm Records",
    titleHi: "ऐतिहासिक खेत रिकॉर्ड",
    descEn: "Every transaction, weight record, and payment archived forever for your reference.",
    descHi: "हर लेनदेन, वज़न रिकॉर्ड और भुगतान स्थायी रूप से संग्रहीत।",
    badgeType: "completed",
  },
];

function FeatureCard({ f, lang }: { f: Feature; lang: "en" | "hi" }) {
  const isHindi = lang === "hi";
  return (
    <div
      className="card"
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 12,
        transition: "transform 0.2s ease, box-shadow 0.2s ease",
        cursor: "default",
      }}
      onMouseEnter={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "translateY(-3px)";
        (e.currentTarget as HTMLElement).style.boxShadow = "var(--shadow-md)";
      }}
      onMouseLeave={(e) => {
        (e.currentTarget as HTMLElement).style.transform = "none";
        (e.currentTarget as HTMLElement).style.boxShadow = "var(--shadow-sm)";
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
        <span
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            width: 44,
            height: 44,
            background: "var(--color-primary-bg)",
            borderRadius: 12,
            color: "var(--color-primary)",
            flexShrink: 0,
          }}
        >
          {f.icon}
        </span>
        {f.badge && (
          <span className={`badge badge-${f.badgeType}`}>
            {isHindi ? f.badgeHi : f.badge}
          </span>
        )}
      </div>
      <div>
        <h3 className="text-h4" style={{ color: "var(--color-text-main)", marginBottom: 6 }}>
          {isHindi ? f.titleHi : f.titleEn}
        </h3>
        <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
          {isHindi ? f.descHi : f.descEn}
        </p>
      </div>
    </div>
  );
}

export default function FeaturesSection({ lang }: { lang: "en" | "hi" }) {
  const isHindi = lang === "hi";
  return (
    <section id="features" style={{ padding: "80px 0" }}>
      <div className="page-container">
        {/* Section header */}
        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <span
            className="badge badge-confirmed"
            style={{ marginBottom: 12, display: "inline-flex" }}
          >
            {isHindi ? "सुविधाएं" : "Platform Features"}
          </span>
          <h2 className="text-h1" style={{ color: "var(--color-text-main)", marginBottom: 12 }}>
            {isHindi ? "हर कदम पर आपके साथ" : "Everything a Farmer Needs"}
          </h2>
          <p
            className="text-body-lg"
            style={{ color: "var(--color-text-muted)", maxWidth: 540, margin: "0 auto" }}
          >
            {isHindi
              ? "पंजीकरण से लेकर भुगतान तक — Krishka Vachana हर चरण में आपकी मदद करता है।"
              : "From registration to payment — Krishka Vachana supports every step of the procurement journey."}
          </p>
        </div>

        {/* Grid */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
            gap: 16,
          }}
        >
          {features.map((f, i) => (
            <FeatureCard key={i} f={f} lang={lang} />
          ))}
        </div>
      </div>
    </section>
  );
}
