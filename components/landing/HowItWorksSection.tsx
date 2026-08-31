"use client";

const steps = [
  {
    num: "01",
    titleEn: "Register with Aadhaar",
    titleHi: "आधार से पंजीकरण करें",
    descEn: "Create your Krishka Vachana profile linked to your Aadhaar number. One-time setup.",
    descHi: "अपने आधार से Krishka Vachana प्रोफ़ाइल बनाएं। एक बार की प्रक्रिया।",
  },
  {
    num: "02",
    titleEn: "Add Crop & Quantity",
    titleHi: "फसल और मात्रा दर्ज करें",
    descEn: "Select your crop type and enter the expected harvest quantity for procurement.",
    descHi: "फसल का प्रकार और अपेक्षित उत्पादन मात्रा दर्ज करें।",
  },
  {
    num: "03",
    titleEn: "Choose Centre & Book Slot",
    titleHi: "केंद्र और स्लॉट चुनें",
    descEn: "View nearby procurement centres with live congestion data, then book your preferred slot.",
    descHi: "लाइव भीड़ डेटा के साथ नज़दीकी केंद्र देखें, फिर अपना स्लॉट बुक करें।",
  },
  {
    num: "04",
    titleEn: "Get Your Token",
    titleHi: "टोकन प्राप्त करें",
    descEn: "Receive a digital QR token or print it at a local kiosk if you don't have a smartphone.",
    descHi: "डिजिटल QR टोकन पाएं या स्थानीय कियोस्क से प्रिंट करें।",
  },
  {
    num: "05",
    titleEn: "Smart Queue Adjustment",
    titleHi: "स्मार्ट कतार समायोजन",
    descEn: "Running late? The queue system auto-adjusts your position so you don't lose your slot.",
    descHi: "देर हो रही है? कतार प्रणाली स्वचालित रूप से आपकी स्थिति समायोजित कर देती है।",
  },
  {
    num: "06",
    titleEn: "Quality & Weight Check",
    titleHi: "गुणवत्ता और वज़न जांच",
    descEn: "Your crop is weighed and quality-checked at the centre. Records are instantly saved.",
    descHi: "आपकी फसल का वज़न और गुणवत्ता जांच होती है। रिकॉर्ड तुरंत सेव होता है।",
  },
  {
    num: "07",
    titleEn: "Transparent Payment",
    titleHi: "पारदर्शी भुगतान",
    descEn: "See MSP rate, deductions, and net amount in real-time. Payment directly to your bank.",
    descHi: "MSP दर, कटौती और शुद्ध राशि रियल-टाइम में देखें। भुगतान सीधे आपके बैंक में।",
  },
  {
    num: "08",
    titleEn: "Historical Records",
    titleHi: "ऐतिहासिक रिकॉर्ड",
    descEn: "All transactions and farm records are stored and accessible anytime from your dashboard.",
    descHi: "सभी लेनदेन और खेत रिकॉर्ड आपके डैशबोर्ड पर हमेशा उपलब्ध।",
  },
];

export default function HowItWorksSection({ lang }: { lang: "en" | "hi" }) {
  const isHindi = lang === "hi";
  return (
    <section
      id="how-it-works"
      style={{ padding: "80px 0", background: "var(--color-primary-bg)" }}
    >
      <div className="page-container">
        <div style={{ textAlign: "center", marginBottom: 48 }}>
          <span
            className="badge badge-processing"
            style={{ marginBottom: 12, display: "inline-flex" }}
          >
            {isHindi ? "प्रक्रिया" : "How It Works"}
          </span>
          <h2 className="text-h1" style={{ color: "var(--color-text-main)", marginBottom: 12 }}>
            {isHindi ? "8 सरल चरण" : "8 Simple Steps"}
          </h2>
          <p
            className="text-body-lg"
            style={{ color: "var(--color-text-muted)", maxWidth: 480, margin: "0 auto" }}
          >
            {isHindi
              ? "पंजीकरण से लेकर भुगतान तक — पूरी प्रक्रिया एक प्लेटफ़ॉर्म पर।"
              : "From farm gate to bank account — the entire procurement flow on one platform."}
          </p>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
            gap: 16,
          }}
        >
          {steps.map((step, i) => (
            <div
              key={i}
              className="card"
              style={{
                display: "flex",
                flexDirection: "column",
                gap: 12,
                transition: "transform 0.2s, box-shadow 0.2s",
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
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span
                  style={{
                    fontWeight: 700,
                    fontSize: 11,
                    color: "var(--color-primary-btn)",
                    background: "var(--color-primary-light)",
                    borderRadius: 6,
                    padding: "3px 8px",
                    letterSpacing: "0.04em",
                  }}
                >
                  {step.num}
                </span>
                <span style={{ fontSize: 22 }}></span>
              </div>
              <h3 className="text-h4" style={{ color: "var(--color-text-main)" }}>
                {isHindi ? step.titleHi : step.titleEn}
              </h3>
              <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>
                {isHindi ? step.descHi : step.descEn}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
