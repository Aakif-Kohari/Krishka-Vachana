"use client";
import Link from "next/link";
import {
  TrendingUp,
  CalendarCheck,
  Users,
  CreditCard,
  Clock,
  CheckCircle2,
  ArrowRight,
  Wheat,
  Droplets,
  AlertCircle,
} from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

export default function DashboardPage() {
  const { isHindi } = useLanguage();

  const stats = [
    {
      label: isHindi ? "सक्रिय बुकिंग" : "Active Bookings",
      value: "2",
      sub: isHindi ? "अगला: 5 सितंबर 2026" : "Next: 5 Sep, 2026",
      icon: CalendarCheck,
      accent: "var(--color-primary-btn)",
      bg: "var(--color-primary-bg)",
    },
    {
      label: isHindi ? "कतार स्थिति" : "Queue Position",
      value: "#3",
      sub: isHindi ? "अनुमानित प्रतीक्षा: ~45 मिनट" : "Est. wait: ~45 min",
      icon: Users,
      accent: "var(--color-info)",
      bg: "var(--color-info-bg)",
    },
    {
      label: isHindi ? "कुल प्राप्त राशि" : "Total Paid",
      value: "₹48,200",
      sub: isHindi ? "इस सीजन में" : "This season",
      icon: CreditCard,
      accent: "var(--color-success)",
      bg: "var(--color-success-bg)",
    },
    {
      label: isHindi ? "बकाया भुगतान" : "Pending Payment",
      value: "₹6,800",
      sub: isHindi ? "1 लेनदेन प्रक्रिया में" : "1 transaction pending",
      icon: TrendingUp,
      accent: "var(--color-warning)",
      bg: "var(--color-warning-bg)",
    },
  ];

  const recentBookings = [
    {
      id: "BK-2024-1071",
      crop: isHindi ? "गेहूँ (Wheat)" : "Wheat",
      quantity: "18 Quintal",
      date: "5 Sep 2026",
      centre: isHindi ? "राजपुर मंडी (Rajpur APMC)" : "Rajpur APMC",
      status: "confirmed",
    },
    {
      id: "BK-2024-1043",
      crop: isHindi ? "मक्का (Maize)" : "Maize",
      quantity: "10 Quintal",
      date: "28 Aug 2026",
      centre: isHindi ? "खंडवा मंडी" : "Khandwa Mandi",
      status: "completed",
    },
    {
      id: "BK-2024-1029",
      crop: isHindi ? "सोयाबीन (Soybean)" : "Soybean",
      quantity: "22 Quintal",
      date: "15 Aug 2026",
      centre: isHindi ? "राजपुर मंडी" : "Rajpur APMC",
      status: "completed",
    },
  ];

  const recentPayments = [
    { id: "PAY-881", amount: "₹12,400", crop: isHindi ? "मक्का" : "Maize", date: "28 Aug 2026", status: "completed" },
    { id: "PAY-856", amount: "₹18,600", crop: isHindi ? "सोयाबीन" : "Soybean", date: "16 Aug 2026", status: "completed" },
    { id: "PAY-892", amount: "₹6,800", crop: isHindi ? "गेहूँ" : "Wheat", date: isHindi ? "अनुमानित 6 सितंबर" : "Expected 6 Sep", status: "processing" },
  ];

  const StatusBadge = ({ status }: { status: string }) => {
    const map: Record<string, string> = {
      confirmed: "badge-confirmed",
      waiting: "badge-waiting",
      processing: "badge-processing",
      cancelled: "badge-cancelled",
      completed: "badge-completed",
    };
    return (
      <span className={`badge ${map[status] ?? "badge-waiting"}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      {/* Page header */}
      <div style={{ marginBottom: 24 }}>
        <h1 className="text-h1" style={{ color: "var(--color-text-main)" }}>
          {isHindi ? "सुप्रभात, रमेश सिंह 👋" : "Good morning, Ramesh 👋"}
        </h1>
        <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
          {isHindi
            ? "इस सीजन में आपकी उपार्जन गतिविधियों का अवलोकन।"
            : "Here's an overview of your procurement activity this season."}
        </p>
      </div>

      {/* Stat cards */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: 16,
          marginBottom: 32,
        }}
      >
        {stats.map(({ label, value, sub, icon: Icon, accent, bg }) => (
          <div key={label} className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-secondary)" }}>{label}</span>
              <span
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: 8,
                  background: bg,
                  color: accent,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Icon size={18} />
              </span>
            </div>
            <div>
              <div style={{ fontSize: 28, fontWeight: 700, color: "var(--color-text-main)", lineHeight: 1 }}>{value}</div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 4 }}>{sub}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Alert banner */}
      <div
        style={{
          background: "var(--color-warning-bg)",
          border: "1px solid #f5e0a0",
          borderRadius: 12,
          padding: "14px 20px",
          display: "flex",
          alignItems: "flex-start",
          gap: 12,
          marginBottom: 32,
        }}
      >
        <AlertCircle size={20} color="var(--color-warning)" style={{ flexShrink: 0, marginTop: 1 }} />
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--color-warning)" }}>
            {isHindi ? "भुगतान प्रक्रिया में है" : "Payment Pending"}
          </div>
          <div style={{ fontSize: 13, color: "#7c5a1a", marginTop: 2 }}>
            {isHindi
              ? "गेहूँ उपार्जन (BK-2024-1071) के लिए ₹6,800 का भुगतान संसाधित हो रहा है। 2 कार्य दिवसों में जमा होगा।"
              : "Your payment of ₹6,800 for Wheat (BK-2024-1071) is being processed and will be credited within 2 business days."}
          </div>
        </div>
      </div>

      {/* Two-column section */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }} className="dashboard-grid-2col">
        {/* Recent Bookings */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid var(--color-divider)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h2 className="text-h4" style={{ color: "var(--color-text-main)" }}>
              {isHindi ? "हाल की बुकिंग" : "Recent Bookings"}
            </h2>
            <Link href="/dashboard/booking" className="btn btn-ghost" style={{ height: 32, fontSize: 13, gap: 4 }}>
              {isHindi ? "सभी देखें" : "View all"} <ArrowRight size={14} />
            </Link>
          </div>
          <div>
            {recentBookings.map((b, i) => (
              <div
                key={b.id}
                style={{
                  padding: "14px 20px",
                  borderBottom: i < recentBookings.length - 1 ? "1px solid var(--color-divider)" : "none",
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <span
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 8,
                    background: "var(--color-primary-bg)",
                    color: "var(--color-primary-btn)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <Wheat size={16} />
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)" }}>
                    {b.crop} · {b.quantity}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>
                    {b.centre} · {b.date}
                  </div>
                </div>
                <StatusBadge status={b.status} />
              </div>
            ))}
          </div>
        </div>

        {/* Recent Payments */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div
            style={{
              padding: "16px 20px",
              borderBottom: "1px solid var(--color-divider)",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h2 className="text-h4" style={{ color: "var(--color-text-main)" }}>
              {isHindi ? "हाल के भुगतान" : "Recent Payments"}
            </h2>
            <Link href="/dashboard/payments" className="btn btn-ghost" style={{ height: 32, fontSize: 13, gap: 4 }}>
              {isHindi ? "सभी देखें" : "View all"} <ArrowRight size={14} />
            </Link>
          </div>
          <div>
            {recentPayments.map((p, i) => (
              <div
                key={p.id}
                style={{
                  padding: "14px 20px",
                  borderBottom: i < recentPayments.length - 1 ? "1px solid var(--color-divider)" : "none",
                  display: "flex",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <span
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 8,
                    background: p.status === "completed" ? "var(--color-success-bg)" : "var(--color-warning-bg)",
                    color: p.status === "completed" ? "var(--color-success)" : "var(--color-warning)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {p.status === "completed" ? <CheckCircle2 size={16} /> : <Clock size={16} />}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)" }}>
                    {p.id} · {p.crop}
                  </div>
                  <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>{p.date}</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "var(--color-text-main)" }}>{p.amount}</div>
                  <StatusBadge status={p.status} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        @media (max-width: 767px) {
          .dashboard-grid-2col { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
