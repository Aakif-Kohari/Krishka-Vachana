"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Leaf, Phone, ShieldCheck, ArrowRight, Lock, Globe, CheckCircle2, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const [loginMethod, setLoginMethod] = useState<"mobile" | "farmerId">("mobile");
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [identifier, setIdentifier] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isHindi = lang === "hi";

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!identifier.trim()) {
      setError(
        loginMethod === "mobile"
          ? isHindi
            ? "कृपया अपना 10 अंकों का मोबाइल नंबर दर्ज करें।"
            : "Please enter your 10-digit mobile number."
          : isHindi
          ? "कृपया अपनी किसान आईडी दर्ज करें।"
          : "Please enter your Farmer ID (e.g. KV-2024-0471)."
      );
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setOtpSent(true);
    }, 600);
  };

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!authCode.trim()) {
      setError(isHindi ? "कृपया OTP या पिन दर्ज करें।" : "Please enter the OTP or PIN.");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      router.push("/dashboard");
    }, 800);
  };

  const fillDemoCreds = () => {
    if (loginMethod === "mobile") {
      setIdentifier("9876543210");
    } else {
      setIdentifier("KV-2024-0471");
    }
    setAuthCode("123456");
    setError("");
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "var(--color-bg-page)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      {/* Header */}
      <header
        style={{
          height: 64,
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          borderBottom: "1px solid var(--color-divider)",
          background: "#ffffff",
        }}
      >
        <Link href="/" style={{ display: "flex", alignItems: "center", gap: 8, textDecoration: "none" }}>
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
            <span style={{ fontWeight: 700, fontSize: 16, color: "var(--color-primary-dark)" }}>
              Krishka Vachana
            </span>
            <span style={{ fontSize: 10, color: "var(--color-text-muted)", fontWeight: 500 }}>
              {isHindi ? "किसान का अटूट विश्वास" : "Farmer Procurement Portal"}
            </span>
          </span>
        </Link>

        <button
          className="btn btn-secondary"
          onClick={() => setLang(lang === "en" ? "hi" : "en")}
          style={{ height: 36, padding: "0 12px", fontSize: 13, gap: 6 }}
        >
          <Globe size={15} />
          {isHindi ? "English" : "हिंदी"}
        </button>
      </header>

      {/* Content */}
      <main
        style={{
          flex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "40px 16px",
        }}
      >
        <div
          className="card animate-fade-up"
          style={{
            width: "100%",
            maxWidth: 440,
            padding: 32,
            boxShadow: "var(--shadow-md)",
            border: "1px solid var(--color-divider)",
          }}
        >
          <div style={{ textAlign: "center", marginBottom: 24 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: "var(--color-primary-bg)",
                color: "var(--color-primary-btn)",
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: 12,
              }}
            >
              <ShieldCheck size={24} />
            </div>
            <h1 className="text-h2" style={{ color: "var(--color-text-main)" }}>
              {isHindi ? "पोर्टल में लॉगिन करें" : "Farmer Portal Login"}
            </h1>
            <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
              {isHindi
                ? "अपनी स्लॉट बुकिंग और भुगतान देखने के लिए प्रवेश करें।"
                : "Access slot bookings, live queue & MSP payments."}
            </p>
          </div>

          {/* Login Mode Tabs */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: 4,
              background: "var(--color-bg-light)",
              padding: 4,
              borderRadius: 8,
              marginBottom: 20,
            }}
          >
            <button
              type="button"
              onClick={() => {
                setLoginMethod("mobile");
                setOtpSent(false);
                setError("");
              }}
              style={{
                height: 36,
                border: "none",
                borderRadius: 6,
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
                background: loginMethod === "mobile" ? "#ffffff" : "transparent",
                color: loginMethod === "mobile" ? "var(--color-primary-dark)" : "var(--color-text-muted)",
                boxShadow: loginMethod === "mobile" ? "var(--shadow-sm)" : "none",
                transition: "all 0.15s ease",
              }}
            >
              {isHindi ? "मोबाइल नंबर" : "Mobile Number"}
            </button>
            <button
              type="button"
              onClick={() => {
                setLoginMethod("farmerId");
                setOtpSent(false);
                setError("");
              }}
              style={{
                height: 36,
                border: "none",
                borderRadius: 6,
                fontSize: 13,
                fontWeight: 600,
                cursor: "pointer",
                background: loginMethod === "farmerId" ? "#ffffff" : "transparent",
                color: loginMethod === "farmerId" ? "var(--color-primary-dark)" : "var(--color-text-muted)",
                boxShadow: loginMethod === "farmerId" ? "var(--shadow-sm)" : "none",
                transition: "all 0.15s ease",
              }}
            >
              {isHindi ? "किसान आईडी" : "Farmer ID"}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div
              style={{
                background: "var(--color-error-bg)",
                border: "1px solid #fecaca",
                color: "var(--color-error)",
                padding: "10px 14px",
                borderRadius: 8,
                fontSize: 13,
                marginBottom: 16,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          {!otpSent ? (
            <form onSubmit={handleSendOtp} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: 14,
                    fontWeight: 500,
                    color: "var(--color-text-secondary)",
                    marginBottom: 6,
                  }}
                >
                  {loginMethod === "mobile"
                    ? isHindi
                      ? "10 अंकों का मोबाइल नंबर"
                      : "Mobile Number"
                    : isHindi
                    ? "किसान आईडी (KV-ID)"
                    : "Farmer ID (KV-ID)"}
                </label>
                <div style={{ position: "relative" }}>
                  <span
                    style={{
                      position: "absolute",
                      left: 12,
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "var(--color-text-muted)",
                    }}
                  >
                    {loginMethod === "mobile" ? <Phone size={16} /> : <Lock size={16} />}
                  </span>
                  <input
                    type={loginMethod === "mobile" ? "tel" : "text"}
                    placeholder={
                      loginMethod === "mobile"
                        ? isHindi
                          ? "उदा. 9876543210"
                          : "e.g. 9876543210"
                        : "e.g. KV-2024-0471"
                    }
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    style={{
                      width: "100%",
                      height: 44,
                      borderRadius: 8,
                      border: "1px solid var(--color-border)",
                      paddingLeft: 38,
                      paddingRight: 12,
                      fontSize: 14,
                      color: "var(--color-text-main)",
                      outline: "none",
                      background: "#ffffff",
                    }}
                  />
                </div>
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
                {loading
                  ? isHindi
                    ? "कृपया प्रतीक्षा करें..."
                    : "Sending OTP..."
                  : isHindi
                  ? "OTP प्राप्त करें"
                  : "Get OTP / Continue"}
                {!loading && <ArrowRight size={16} />}
              </button>
            </form>
          ) : (
            <form onSubmit={handleLoginSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div
                style={{
                  background: "var(--color-primary-bg)",
                  border: "1px solid var(--color-primary-light)",
                  borderRadius: 8,
                  padding: "10px 14px",
                  fontSize: 13,
                  color: "var(--color-primary-dark)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                }}
              >
                <span>
                  {isHindi ? "OTP भेजा गया: " : "OTP sent to: "}
                  <strong>{identifier}</strong>
                </span>
                <button
                  type="button"
                  onClick={() => setOtpSent(false)}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--color-primary-btn)",
                    fontWeight: 600,
                    cursor: "pointer",
                    fontSize: 12,
                    textDecoration: "underline",
                  }}
                >
                  {isHindi ? "बदलें" : "Change"}
                </button>
              </div>

              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: 14,
                    fontWeight: 500,
                    color: "var(--color-text-secondary)",
                    marginBottom: 6,
                  }}
                >
                  {isHindi ? "6 अंकों का OTP / पिन" : "Enter 6-digit OTP / Security PIN"}
                </label>
                <input
                  type="password"
                  placeholder="• • • • • •"
                  value={authCode}
                  maxLength={6}
                  onChange={(e) => setAuthCode(e.target.value)}
                  style={{
                    width: "100%",
                    height: 44,
                    borderRadius: 8,
                    border: "1px solid var(--color-border)",
                    padding: "0 12px",
                    fontSize: 18,
                    letterSpacing: "4px",
                    textAlign: "center",
                    color: "var(--color-text-main)",
                    outline: "none",
                    background: "#ffffff",
                  }}
                />
              </div>

              <button type="submit" className="btn btn-primary" style={{ width: "100%" }} disabled={loading}>
                {loading
                  ? isHindi
                    ? "सत्यापित किया जा रहा है..."
                    : "Verifying..."
                  : isHindi
                  ? "लॉगिन की पुष्टि करें"
                  : "Verify & Login"}
                {!loading && <CheckCircle2 size={16} />}
              </button>
            </form>
          )}

          {/* Quick Demo Fill Helper */}
          <div
            style={{
              marginTop: 20,
              paddingTop: 16,
              borderTop: "1px dashed var(--color-divider)",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <span style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
              {isHindi ? "परीक्षण के लिए:" : "Testing demo?"}
            </span>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={fillDemoCreds}
              style={{ height: 28, fontSize: 12, padding: "0 8px" }}
            >
              {isHindi ? "डेमो विवरण भरें" : "Auto-fill Demo Data"}
            </button>
          </div>

          {/* Footer Link */}
          <div style={{ textAlign: "center", marginTop: 20, fontSize: 14, color: "var(--color-text-muted)" }}>
            {isHindi ? "नया खाता बनाएं?" : "Don't have a Farmer Account?"}{" "}
            <Link
              href="/register"
              style={{ color: "var(--color-primary-btn)", fontWeight: 600, textDecoration: "none" }}
            >
              {isHindi ? "पंजीकरण करें" : "Register Now"}
            </Link>
          </div>
        </div>
      </main>

      {/* Bottom bar */}
      <footer
        style={{
          padding: "16px 24px",
          textAlign: "center",
          fontSize: 12,
          color: "var(--color-text-muted)",
          borderTop: "1px solid var(--color-divider)",
          background: "#ffffff",
        }}
      >
        © 2026 Krishka Vachana. All farmer data is protected under Government MSP Guidelines.
      </footer>
    </div>
  );
}
