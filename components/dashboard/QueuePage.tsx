"use client";
import { useState, useEffect } from "react";
import {
  Users,
  Clock,
  MapPin,
  Wheat,
  RefreshCw,
  CheckCircle2,
  ArrowRight,
  AlertCircle,
} from "lucide-react";

const queueData = [
  { token: "T-001", name: "Mohan Patel", crop: "Wheat", qty: "20Q", status: "processing" },
  { token: "T-002", name: "Suresh Verma", crop: "Maize", qty: "12Q", status: "waiting" },
  { token: "T-003", name: "Ramesh Singh", crop: "Wheat", qty: "18Q", status: "waiting", isYou: true },
  { token: "T-004", name: "Dinesh Kumar", crop: "Soybean", qty: "25Q", status: "waiting" },
  { token: "T-005", name: "Ashok Yadav", crop: "Cotton", qty: "8Q", status: "waiting" },
  { token: "T-006", name: "Laxmi Devi", crop: "Paddy", qty: "14Q", status: "waiting" },
  { token: "T-007", name: "Ravi Tiwari", crop: "Wheat", qty: "22Q", status: "waiting" },
];

function QueueRadialCard({ position, total }: { position: number; total: number }) {
  const pct = ((total - position) / total) * 100;
  const r = 52;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;

  return (
    <div className="card" style={{
      display: "flex", flexDirection: "column", alignItems: "center",
      padding: "32px 24px", gap: 12, background: "var(--color-primary-bg)",
      borderColor: "#b0ddc5",
    }}>
      <svg width={130} height={130} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={65} cy={65} r={r} fill="none" stroke="var(--color-divider)" strokeWidth={10} />
        <circle
          cx={65} cy={65} r={r} fill="none"
          stroke="var(--color-primary-btn)" strokeWidth={10}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      </svg>
      <div style={{ textAlign: "center", marginTop: -8 }}>
        <div style={{ fontSize: 42, fontWeight: 700, color: "var(--color-primary-dark)", lineHeight: 1 }}>#{position}</div>
        <div style={{ fontSize: 14, color: "var(--color-text-muted)", marginTop: 4 }}>Your queue position</div>
      </div>
      <div style={{ display: "flex", gap: 20, marginTop: 4 }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: "var(--color-text-main)" }}>{total - position}</div>
          <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>Ahead of you</div>
        </div>
        <div style={{ width: 1, background: "var(--color-divider)" }} />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: "var(--color-text-main)" }}>~45 min</div>
          <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>Est. wait</div>
        </div>
        <div style={{ width: 1, background: "var(--color-divider)" }} />
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: "var(--color-text-main)" }}>{total}</div>
          <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>Total today</div>
        </div>
      </div>
    </div>
  );
}

export default function QueuePage() {
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = () => {
    setRefreshing(true);
    setTimeout(() => {
      setLastUpdated(new Date());
      setRefreshing(false);
    }, 800);
  };

  // Auto-refresh every 60s
  useEffect(() => {
    const t = setInterval(() => setLastUpdated(new Date()), 60000);
    return () => clearInterval(t);
  }, []);

  const statusMap: Record<string, string> = {
    processing: "badge-processing",
    waiting: "badge-waiting",
    completed: "badge-completed",
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 className="text-h1" style={{ color: "var(--color-text-main)" }}>Queue Status</h1>
          <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
            Real-time queue position at Rajpur APMC for your booking on 5 Sep 2026.
          </p>
        </div>
        <button
          id="refresh-queue-btn"
          className="btn btn-secondary"
          onClick={handleRefresh}
          disabled={refreshing}
          style={{ flexShrink: 0, gap: 8 }}
        >
          <RefreshCw size={15} style={{ animation: refreshing ? "spin 0.6s linear infinite" : "none" }} />
          {refreshing ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {/* Booking context */}
      <div className="card" style={{ marginBottom: 24, padding: "14px 20px", display: "flex", gap: 20, flexWrap: "wrap" }}>
        {[
          { icon: <Wheat size={15} />, label: "Wheat · 18 Quintal · BK-2024-1071" },
          { icon: <MapPin size={15} />, label: "Rajpur APMC, MP · Slot S-14" },
          { icon: <Clock size={15} />, label: "5 Sep 2026 · 09:00 AM – 11:00 AM" },
        ].map(({ icon, label }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--color-text-secondary)" }}>
            <span style={{ color: "var(--color-primary-btn)" }}>{icon}</span>
            {label}
          </div>
        ))}
        <div style={{ marginLeft: "auto" }}>
          <span className="badge badge-confirmed">Confirmed</span>
        </div>
      </div>

      {/* Main grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.6fr", gap: 20, marginBottom: 24 }} className="queue-main-grid">

        {/* Radial position */}
        <QueueRadialCard position={3} total={28} />

        {/* Live queue list */}
        <div className="card" style={{ padding: 0, overflow: "hidden" }}>
          <div style={{
            padding: "14px 20px",
            borderBottom: "1px solid var(--color-divider)",
            display: "flex", justifyContent: "space-between", alignItems: "center",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <Users size={16} color="var(--color-primary-btn)" />
              <span className="text-h4" style={{ color: "var(--color-text-main)" }}>Live Queue</span>
            </div>
            <span style={{ fontSize: 12, color: "var(--color-text-muted)" }}>
              Updated {lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
            </span>
          </div>

          {queueData.map((item, i) => (
            <div
              key={item.token}
              style={{
                padding: "12px 20px",
                borderBottom: i < queueData.length - 1 ? "1px solid var(--color-divider)" : "none",
                display: "flex", alignItems: "center", gap: 12,
                background: item.isYou ? "var(--color-primary-bg)" : "transparent",
                position: "relative",
              }}
            >
              {item.isYou && (
                <div style={{ position: "absolute", left: 0, top: "50%", transform: "translateY(-50%)", width: 3, height: 32, background: "var(--color-primary-btn)", borderRadius: "0 4px 4px 0" }} />
              )}
              <span style={{
                width: 28, height: 28, borderRadius: "9999px",
                background: item.status === "processing" ? "var(--color-info-bg)" : item.isYou ? "var(--color-primary-light)" : "var(--color-bg-light)",
                color: item.status === "processing" ? "var(--color-info)" : item.isYou ? "var(--color-primary-dark)" : "var(--color-text-muted)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 11, fontWeight: 700, flexShrink: 0,
              }}>
                {i + 1}
              </span>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 13, fontWeight: item.isYou ? 700 : 500, color: item.isYou ? "var(--color-primary-dark)" : "var(--color-text-main)" }}>
                  {item.isYou ? "You — " : ""}{item.name}
                </div>
                <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 1 }}>
                  {item.token} · {item.crop} · {item.qty}
                </div>
              </div>
              <span className={`badge ${statusMap[item.status] ?? "badge-waiting"}`} style={{ fontSize: 11 }}>
                {item.status === "processing" ? "Processing" : "Waiting"}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* What to expect */}
      <div className="card" style={{ marginBottom: 24 }}>
        <h2 className="text-h4" style={{ color: "var(--color-text-main)", marginBottom: 16 }}>What to expect</h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
          {[
            { step: "1", title: "Arrive at Centre", desc: "Arrive 15 min before your slot time with all documents." },
            { step: "2", title: "Token Verification", desc: "Show your booking ID and Aadhaar at the counter." },
            { step: "3", title: "Weighing & Grading", desc: "Crop is weighed and quality checked by officials." },
            { step: "4", title: "Payment Credit", desc: "MSP amount credited to your registered bank within 2 days." },
          ].map(({ step, title, desc }) => (
            <div key={step} style={{ display: "flex", gap: 12 }}>
              <span style={{
                width: 32, height: 32, borderRadius: "9999px",
                background: "var(--color-primary-btn)", color: "#fff",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 13, fontWeight: 700, flexShrink: 0,
              }}>
                {step}
              </span>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--color-text-main)" }}>{title}</div>
                <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 3, lineHeight: "18px" }}>{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Alert */}
      <div style={{
        background: "var(--color-info-bg)", border: "1px solid #bfdbfe",
        borderRadius: 12, padding: "14px 20px",
        display: "flex", gap: 12, alignItems: "flex-start",
      }}>
        <AlertCircle size={18} color="var(--color-info)" style={{ flexShrink: 0, marginTop: 1 }} />
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, color: "var(--color-info)" }}>SMS Alerts Enabled</div>
          <div style={{ fontSize: 13, color: "#1e40af", marginTop: 2 }}>
            You will receive an SMS when it's your turn. Make sure your mobile number is registered with your Krishka Vachana account.
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (max-width: 767px) {
          .queue-main-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
