"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Leaf,
  User,
  Phone,
  CreditCard,
  MapPin,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  Globe,
  Wheat,
  Building2,
  FileCheck2,
  AlertCircle,
} from "lucide-react";

export default function RegisterPage() {
  const router = useRouter();
  const [lang, setLang] = useState<"en" | "hi">("en");
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const isHindi = lang === "hi";

  const [form, setForm] = useState({
    // Step 1
    fullName: "",
    mobile: "",
    aadhaar: "",
    district: "",
    village: "",
    // Step 2
    landAcres: "",
    crops: [] as string[],
    mandi: "",
    // Step 3
    bankName: "",
    accountNo: "",
    ifscCode: "",
  });

  const handleChange = (field: string, val: any) => {
    setForm((prev) => ({ ...prev, [field]: val }));
    if (error) setError("");
  };

  const toggleCrop = (cropName: string) => {
    setForm((prev) => {
      const exists = prev.crops.includes(cropName);
      const updated = exists
        ? prev.crops.filter((c) => c !== cropName)
        : [...prev.crops, cropName];
      return { ...prev, crops: updated };
    });
  };

  const validateStep1 = () => {
    if (!form.fullName.trim()) return isHindi ? "कृपया अपना पूरा नाम दर्ज करें।" : "Please enter your full name.";
    if (!form.mobile.trim() || form.mobile.length < 10)
      return isHindi ? "कृपया 10 अंकों का मोबाइल नंबर दर्ज करें।" : "Please enter a valid 10-digit mobile number.";
    if (!form.district.trim()) return isHindi ? "कृपया अपना जिला दर्ज करें।" : "Please enter your district.";
    return "";
  };

  const validateStep2 = () => {
    if (!form.landAcres.trim()) return isHindi ? "कृपया अपनी कृषि भूमि (एकड़ में) दर्ज करें।" : "Please enter land size in acres.";
    if (form.crops.length === 0) return isHindi ? "कम से कम एक फसल चुनें।" : "Select at least one primary crop.";
    if (!form.mandi) return isHindi ? "पसंदीदा मंडी / केंद्र चुनें।" : "Please select your preferred procurement centre.";
    return "";
  };

  const validateStep3 = () => {
    if (!form.bankName.trim()) return isHindi ? "बैंक का नाम दर्ज करें।" : "Please enter your Bank Name.";
    if (!form.accountNo.trim()) return isHindi ? "खाता संख्या दर्ज करें।" : "Please enter your Account Number.";
    if (!form.ifscCode.trim()) return isHindi ? "IFSC कोड दर्ज करें।" : "Please enter your IFSC Code.";
    return "";
  };

  const handleNext = () => {
    if (step === 1) {
      const err = validateStep1();
      if (err) {
        setError(err);
        return;
      }
      setStep(2);
    } else if (step === 2) {
      const err = validateStep2();
      if (err) {
        setError(err);
        return;
      }
      setStep(3);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const err = validateStep3();
    if (err) {
      setError(err);
      return;
    }

    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      router.push("/dashboard");
    }, 1000);
  };

  const fillDemoData = () => {
    setForm({
      fullName: "Ramesh Singh",
      mobile: "9876543210",
      aadhaar: "4521-8890-1234",
      district: "Khargone",
      village: "Rajpur",
      landAcres: "4.5",
      crops: ["Wheat", "Soybean"],
      mandi: "Rajpur APMC, MP",
      bankName: "State Bank of India",
      accountNo: "30876123490",
      ifscCode: "SBIN0001420",
    });
    setError("");
  };

  const cropList = ["Wheat", "Soybean", "Maize", "Paddy", "Cotton", "Gram"];
  const mandiOptions = ["Rajpur APMC, MP", "Khandwa Mandi, MP", "Harda Centre, MP", "Burhanpur Mandi, MP"];

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
              {isHindi ? "किसान पंजीकरण पोर्टल" : "Farmer Registration Portal"}
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

      {/* Main Content */}
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
            maxWidth: 580,
            padding: 32,
            boxShadow: "var(--shadow-md)",
            border: "1px solid var(--color-divider)",
          }}
        >
          {/* Form Header */}
          <div style={{ textAlign: "center", marginBottom: 28 }}>
            <h1 className="text-h2" style={{ color: "var(--color-text-main)" }}>
              {isHindi ? "नया किसान पंजीकरण" : "Register as a Farmer"}
            </h1>
            <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
              {isHindi
                ? "सीधे एमएसपी भुगतान और स्लॉट बुकिंग के लिए अपना विवरण दर्ज करें।"
                : "Register once to book slots, track queue & receive direct MSP credits."}
            </p>
          </div>

          {/* Stepper Header */}
          <div style={{ display: "flex", gap: 8, marginBottom: 28, alignItems: "center" }}>
            {[
              { s: 1, label: isHindi ? "व्यक्तिगत" : "Personal" },
              { s: 2, label: isHindi ? "कृषि भूमि" : "Farm & Crop" },
              { s: 3, label: isHindi ? "बैंक खाता" : "Bank Details" },
            ].map(({ s, label }) => (
              <div key={s} style={{ display: "flex", alignItems: "center", gap: 8, flex: 1 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: "9999px",
                    background: step >= s ? "var(--color-primary-btn)" : "var(--color-bg-light)",
                    color: step >= s ? "#ffffff" : "var(--color-text-muted)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 13,
                    fontWeight: 700,
                    flexShrink: 0,
                    transition: "all 0.2s ease",
                  }}
                >
                  {step > s ? <CheckCircle2 size={16} /> : s}
                </div>
                <span
                  style={{
                    fontSize: 13,
                    color: step === s ? "var(--color-primary-dark)" : "var(--color-text-muted)",
                    fontWeight: step === s ? 600 : 400,
                    whiteSpace: "nowrap",
                  }}
                >
                  {label}
                </span>
                {s < 3 && (
                  <div
                    style={{
                      flex: 1,
                      height: 2,
                      background: step > s ? "var(--color-primary-btn)" : "var(--color-divider)",
                      minWidth: 12,
                    }}
                  />
                )}
              </div>
            ))}
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
                marginBottom: 20,
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <AlertCircle size={16} style={{ flexShrink: 0 }} />
              <span>{error}</span>
            </div>
          )}

          {/* Step 1: Personal Details */}
          {step === 1 && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
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
                  {isHindi ? "पूरा नाम *" : "Full Name (as per Aadhaar) *"}
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
                    <User size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="e.g. Ramesh Singh"
                    value={form.fullName}
                    onChange={(e) => handleChange("fullName", e.target.value)}
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
                    }}
                  />
                </div>
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
                  {isHindi ? "मोबाइल नंबर *" : "Mobile Number (for SMS Alerts) *"}
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
                    <Phone size={16} />
                  </span>
                  <input
                    type="tel"
                    placeholder="e.g. 9876543210"
                    value={form.mobile}
                    onChange={(e) => handleChange("mobile", e.target.value)}
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
                    }}
                  />
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
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
                    {isHindi ? "जिला *" : "District *"}
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
                      <MapPin size={16} />
                    </span>
                    <input
                      type="text"
                      placeholder="e.g. Khargone"
                      value={form.district}
                      onChange={(e) => handleChange("district", e.target.value)}
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
                      }}
                    />
                  </div>
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
                    {isHindi ? "गाँव / शहर" : "Village / Tehsil"}
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Rajpur"
                    value={form.village}
                    onChange={(e) => handleChange("village", e.target.value)}
                    style={{
                      width: "100%",
                      height: 44,
                      borderRadius: 8,
                      border: "1px solid var(--color-border)",
                      padding: "0 12px",
                      fontSize: 14,
                      color: "var(--color-text-main)",
                      outline: "none",
                    }}
                  />
                </div>
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
                  {isHindi ? "आधार / समग्र आईडी (ऐच्छिक)" : "Aadhaar / ID Card (Optional)"}
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
                    <FileCheck2 size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="xxxx-xxxx-xxxx"
                    value={form.aadhaar}
                    onChange={(e) => handleChange("aadhaar", e.target.value)}
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
                    }}
                  />
                </div>
              </div>

              <button
                type="button"
                className="btn btn-primary"
                onClick={handleNext}
                style={{ width: "100%", marginTop: 8 }}
              >
                {isHindi ? "आगे बढ़ें: फसल एवं मंडी" : "Next: Farm & Crop Details"} <ArrowRight size={16} />
              </button>
            </div>
          )}

          {/* Step 2: Farm & Crop */}
          {step === 2 && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
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
                  {isHindi ? "कुल कृषि भूमि (एकड़ में) *" : "Total Land Area (in Acres) *"}
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
                    <Wheat size={16} />
                  </span>
                  <input
                    type="number"
                    step="0.1"
                    placeholder="e.g. 4.5"
                    value={form.landAcres}
                    onChange={(e) => handleChange("landAcres", e.target.value)}
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
                    }}
                  />
                </div>
              </div>

              <div>
                <label
                  style={{
                    display: "block",
                    fontSize: 14,
                    fontWeight: 500,
                    color: "var(--color-text-secondary)",
                    marginBottom: 8,
                  }}
                >
                  {isHindi ? "मुख्य फसलें (एक या अधिक चुनें) *" : "Primary Crops Produced (Select all that apply) *"}
                </label>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {cropList.map((crop) => {
                    const selected = form.crops.includes(crop);
                    return (
                      <button
                        key={crop}
                        type="button"
                        onClick={() => toggleCrop(crop)}
                        style={{
                          height: 36,
                          padding: "0 14px",
                          borderRadius: 9999,
                          border: selected ? "1px solid var(--color-primary-btn)" : "1px solid var(--color-border)",
                          background: selected ? "var(--color-primary-bg)" : "#ffffff",
                          color: selected ? "var(--color-primary-dark)" : "var(--color-text-secondary)",
                          fontSize: 13,
                          fontWeight: selected ? 600 : 400,
                          cursor: "pointer",
                          display: "inline-flex",
                          alignItems: "center",
                          gap: 6,
                          transition: "all 0.15s ease",
                        }}
                      >
                        {selected && <CheckCircle2 size={14} color="var(--color-primary-btn)" />}
                        {crop}
                      </button>
                    );
                  })}
                </div>
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
                  {isHindi ? "निकटतम उपार्जन केंद्र / मंडी *" : "Preferred Procurement Centre *" }
                </label>
                <select
                  value={form.mandi}
                  onChange={(e) => handleChange("mandi", e.target.value)}
                  style={{
                    width: "100%",
                    height: 44,
                    borderRadius: 8,
                    border: "1px solid var(--color-border)",
                    padding: "0 12px",
                    fontSize: 14,
                    color: "var(--color-text-main)",
                    outline: "none",
                    background: "#ffffff",
                  }}
                >
                  <option value="">Select mandi centre...</option>
                  {mandiOptions.map((m) => (
                    <option key={m} value={m}>
                      {m}
                    </option>
                  ))}
                </select>
              </div>

              <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setStep(1)}
                  style={{ flex: 1 }}
                >
                  <ArrowLeft size={16} /> {isHindi ? "पीछे" : "Back"}
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleNext}
                  style={{ flex: 1 }}
                >
                  {isHindi ? "आगे: बैंक विवरण" : "Next: Bank Details"} <ArrowRight size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Bank Details */}
          {step === 3 && (
            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
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
                  {isHindi ? "बैंक का नाम *" : "Bank Name *"}
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
                    <Building2 size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="e.g. State Bank of India"
                    value={form.bankName}
                    onChange={(e) => handleChange("bankName", e.target.value)}
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
                    }}
                  />
                </div>
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
                  {isHindi ? "बैंक खाता संख्या *" : "Bank Account Number *"}
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
                    <CreditCard size={16} />
                  </span>
                  <input
                    type="text"
                    placeholder="e.g. 30876123490"
                    value={form.accountNo}
                    onChange={(e) => handleChange("accountNo", e.target.value)}
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
                    }}
                  />
                </div>
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
                  {isHindi ? "IFSC कोड *" : "IFSC Code *"}
                </label>
                <input
                  type="text"
                  placeholder="e.g. SBIN0001420"
                  value={form.ifscCode}
                  onChange={(e) => handleChange("ifscCode", e.target.value.toUpperCase())}
                  style={{
                    width: "100%",
                    height: 44,
                    borderRadius: 8,
                    border: "1px solid var(--color-border)",
                    padding: "0 12px",
                    fontSize: 14,
                    color: "var(--color-text-main)",
                    outline: "none",
                    textTransform: "uppercase",
                  }}
                />
              </div>

              <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setStep(2)}
                  style={{ flex: 1 }}
                >
                  <ArrowLeft size={16} /> {isHindi ? "पीछे" : "Back"}
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                  style={{ flex: 1 }}
                >
                  {loading
                    ? isHindi
                      ? "पंजीकरण हो रहा है..."
                      : "Registering..."
                    : isHindi
                    ? "पंजीकरण पूरा करें"
                    : "Complete Registration"}
                  {!loading && <CheckCircle2 size={16} />}
                </button>
              </div>
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
              {isHindi ? "परीक्षण के लिए:" : "Want to test quick registration?"}
            </span>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={fillDemoData}
              style={{ height: 28, fontSize: 12, padding: "0 8px" }}
            >
              {isHindi ? "डेमो फ़ॉर्म भरें" : "Auto-fill Demo Profile"}
            </button>
          </div>

          {/* Footer Link */}
          <div style={{ textAlign: "center", marginTop: 20, fontSize: 14, color: "var(--color-text-muted)" }}>
            {isHindi ? "पहले से पंजीकृत हैं?" : "Already registered?"}{" "}
            <Link
              href="/login"
              style={{ color: "var(--color-primary-btn)", fontWeight: 600, textDecoration: "none" }}
            >
              {isHindi ? "लॉगिन करें" : "Sign In"}
            </Link>
          </div>
        </div>
      </main>

      {/* Footer */}
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
        © 2026 Krishka Vachana. All registrations are verified with State Agriculture Department records.
      </footer>
    </div>
  );
}
