"use client";
import { useState } from "react";
import {
  CreditCard,
  Download,
  Search,
  ChevronDown,
  CheckCircle2,
  Clock,
  XCircle,
  TrendingUp,
  Banknote,
  ArrowDownCircle,
  FileText,
  X,
} from "lucide-react";

const allPayments = [
  {
    id: "PAY-892",
    bookingId: "BK-2024-1071",
    crop: "Wheat",
    quantity: "18 Quintal",
    msp: "₹2,275 / Quintal",
    grossAmount: "₹40,950",
    deductions: "₹820",
    netAmount: "₹40,130",
    date: "Expected 6 Sep 2026",
    method: "Direct Bank Transfer",
    status: "processing",
    bankRef: "—",
  },
  {
    id: "PAY-881",
    bookingId: "BK-2024-1043",
    crop: "Maize",
    quantity: "10 Quintal",
    msp: "₹2,090 / Quintal",
    grossAmount: "₹20,900",
    deductions: "₹418",
    netAmount: "₹20,482",
    date: "28 Aug 2026",
    method: "Direct Bank Transfer",
    status: "completed",
    bankRef: "NEFT-20240828-7821",
  },
  {
    id: "PAY-856",
    bookingId: "BK-2024-1029",
    crop: "Soybean",
    quantity: "22 Quintal",
    msp: "₹4,600 / Quintal",
    grossAmount: "₹1,01,200",
    deductions: "₹2,024",
    netAmount: "₹99,176",
    date: "16 Aug 2026",
    method: "Direct Bank Transfer",
    status: "completed",
    bankRef: "NEFT-20240816-4430",
  },
  {
    id: "PAY-831",
    bookingId: "BK-2024-1012",
    crop: "Soybean",
    quantity: "15 Quintal",
    msp: "₹4,600 / Quintal",
    grossAmount: "₹69,000",
    deductions: "—",
    netAmount: "—",
    date: "2 Aug 2026",
    method: "—",
    status: "cancelled",
    bankRef: "—",
  },
];

const statusConfig: Record<string, { label: string; badge: string; icon: React.ReactNode }> = {
  completed: { label: "Paid", badge: "badge-completed", icon: <CheckCircle2 size={14} /> },
  processing: { label: "Processing", badge: "badge-processing", icon: <Clock size={14} /> },
  cancelled: { label: "Cancelled", badge: "badge-cancelled", icon: <XCircle size={14} /> },
};

const StatusBadge = ({ status }: { status: string }) => {
  const cfg = statusConfig[status];
  if (!cfg) return null;
  return (
    <span className={`badge ${cfg.badge}`} style={{ gap: 4 }}>
      {cfg.icon}{cfg.label}
    </span>
  );
};

// Receipt Modal
function ReceiptModal({ payment, onClose }: { payment: typeof allPayments[0]; onClose: () => void }) {
  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
      <div onClick={onClose} style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.4)" }} />
      <div style={{
        position: "relative", background: "#fff", borderRadius: 16,
        padding: 24, width: "100%", maxWidth: 440,
        boxShadow: "var(--shadow-lg)", zIndex: 1,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <div>
            <h2 className="text-h3" style={{ color: "var(--color-text-main)" }}>Payment Receipt</h2>
            <p style={{ fontSize: 13, color: "var(--color-text-muted)", marginTop: 2 }}>{payment.id}</p>
          </div>
          <button onClick={onClose} className="btn btn-ghost" style={{ height: 32, width: 32, padding: 0 }} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {/* Header status */}
        <div style={{ background: "var(--color-success-bg)", borderRadius: 12, padding: "16px 20px", textAlign: "center", marginBottom: 20 }}>
          <CheckCircle2 size={32} color="var(--color-success)" style={{ margin: "0 auto 8px" }} />
          <div style={{ fontSize: 26, fontWeight: 700, color: "var(--color-text-main)" }}>{payment.netAmount}</div>
          <div style={{ fontSize: 13, color: "var(--color-text-muted)", marginTop: 4 }}>Net Amount Credited</div>
        </div>

        {/* Details */}
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {[
            { label: "Booking ID", value: payment.bookingId },
            { label: "Crop", value: `${payment.crop} (${payment.quantity})` },
            { label: "MSP Rate", value: payment.msp },
            { label: "Gross Amount", value: payment.grossAmount },
            { label: "Deductions (2%)", value: payment.deductions },
            { label: "Net Credit", value: payment.netAmount },
            { label: "Bank Reference", value: payment.bankRef },
            { label: "Date", value: payment.date },
            { label: "Method", value: payment.method },
          ].map(({ label, value }) => (
            <div key={label} style={{ display: "flex", justifyContent: "space-between", fontSize: 14, paddingBottom: 10, borderBottom: "1px solid var(--color-divider)" }}>
              <span style={{ color: "var(--color-text-muted)" }}>{label}</span>
              <span style={{ fontWeight: 500, color: "var(--color-text-main)", textAlign: "right", maxWidth: "55%" }}>{value}</span>
            </div>
          ))}
        </div>

        <button className="btn btn-primary" style={{ width: "100%", marginTop: 20 }}>
          <Download size={16} /> Download PDF Receipt
        </button>
      </div>
    </div>
  );
}

export default function PaymentsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [receipt, setReceipt] = useState<typeof allPayments[0] | null>(null);

  const filtered = allPayments.filter((p) => {
    const q = search.toLowerCase();
    const match = p.id.toLowerCase().includes(q) || p.crop.toLowerCase().includes(q) || p.bookingId.toLowerCase().includes(q);
    const s = statusFilter === "All" || p.status === statusFilter.toLowerCase();
    return match && s;
  });

  const completedPayments = allPayments.filter((p) => p.status === "completed");
  const totalPaid = completedPayments.length;
  const pendingCount = allPayments.filter((p) => p.status === "processing").length;

  const summaryStats = [
    {
      label: "Total Received",
      value: "₹1,19,658",
      icon: Banknote,
      bg: "var(--color-success-bg)",
      accent: "var(--color-success)",
      sub: `${totalPaid} transactions`,
    },
    {
      label: "Pending",
      value: "₹40,130",
      icon: Clock,
      bg: "var(--color-warning-bg)",
      accent: "var(--color-warning)",
      sub: `${pendingCount} in processing`,
    },
    {
      label: "This Season",
      value: "₹1,59,788",
      icon: TrendingUp,
      bg: "var(--color-info-bg)",
      accent: "var(--color-info)",
      sub: "Gross total",
    },
    {
      label: "Next Credit",
      value: "6 Sep 2026",
      icon: ArrowDownCircle,
      bg: "var(--color-primary-bg)",
      accent: "var(--color-primary-btn)",
      sub: "Wheat — ₹40,130",
    },
  ];

  return (
    <div style={{ maxWidth: 960, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 className="text-h1" style={{ color: "var(--color-text-main)" }}>Payments</h1>
        <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
          Track your MSP credits, deductions, and download receipts for all transactions.
        </p>
      </div>

      {/* Summary cards */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
        gap: 16,
        marginBottom: 32,
      }}>
        {summaryStats.map(({ label, value, icon: Icon, bg, accent, sub }) => (
          <div key={label} className="card" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-secondary)" }}>{label}</span>
              <span style={{ width: 36, height: 36, borderRadius: 8, background: bg, color: accent, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon size={18} />
              </span>
            </div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 700, color: "var(--color-text-main)", lineHeight: 1 }}>{value}</div>
              <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 4 }}>{sub}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
          <Search size={15} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--color-text-muted)" }} />
          <input
            type="text"
            placeholder="Search by ID, crop, or booking…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              width: "100%", height: 44, background: "#fff",
              border: "1px solid var(--color-border)", borderRadius: 8,
              paddingLeft: 36, paddingRight: 12, fontSize: 14,
              color: "var(--color-text-main)", outline: "none",
            }}
          />
        </div>
        <div style={{ position: "relative" }}>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              height: 44, background: "#fff",
              border: "1px solid var(--color-border)", borderRadius: 8,
              padding: "0 36px 0 12px", fontSize: 14,
              color: "var(--color-text-main)", outline: "none",
              appearance: "none", cursor: "pointer",
            }}
          >
            {["All", "Completed", "Processing", "Cancelled"].map((s) => <option key={s}>{s}</option>)}
          </select>
          <ChevronDown size={15} style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", color: "var(--color-text-muted)" }} />
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {/* Table header */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr 100px 120px 110px 80px",
          padding: "0 20px",
          height: 44,
          background: "var(--color-bg-page)",
          borderBottom: "1px solid var(--color-divider)",
          alignItems: "center",
          gap: 12,
        }} className="payment-table-header">
          {["Transaction", "Crop / Booking", "Gross", "Net Credit", "Status", ""].map((h) => (
            <span key={h} style={{ fontSize: 12, fontWeight: 600, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>{h}</span>
          ))}
        </div>

        {/* Rows */}
        {filtered.length === 0 ? (
          <div style={{ textAlign: "center", padding: "48px 24px" }}>
            <CreditCard size={36} color="var(--color-border)" style={{ margin: "0 auto 12px" }} />
            <p className="text-sm" style={{ color: "var(--color-text-muted)" }}>No payments match your search.</p>
          </div>
        ) : (
          filtered.map((p, i) => (
            <div
              key={p.id}
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr 100px 120px 110px 80px",
                padding: "0 20px",
                minHeight: 56,
                borderBottom: i < filtered.length - 1 ? "1px solid var(--color-divider)" : "none",
                alignItems: "center",
                gap: 12,
                transition: "background 0.15s",
              }}
              className="payment-row payment-table-header"
              onMouseEnter={(e) => (e.currentTarget.style.background = "var(--color-bg-page)")}
              onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
            >
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)" }}>{p.id}</div>
                <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>{p.date}</div>
              </div>
              <div>
                <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-main)" }}>{p.crop} · {p.quantity}</div>
                <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 2 }}>{p.bookingId}</div>
              </div>
              <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-main)" }}>{p.grossAmount}</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: "var(--color-text-main)" }}>{p.netAmount}</div>
              <div><StatusBadge status={p.status} /></div>
              <div style={{ display: "flex", gap: 4 }}>
                {p.status === "completed" && (
                  <button
                    className="btn btn-ghost"
                    style={{ height: 32, width: 32, padding: 0 }}
                    title="View receipt"
                    onClick={() => setReceipt(p)}
                    aria-label="View receipt"
                  >
                    <FileText size={16} />
                  </button>
                )}
                {p.status === "completed" && (
                  <button
                    className="btn btn-ghost"
                    style={{ height: 32, width: 32, padding: 0 }}
                    title="Download"
                    aria-label="Download receipt"
                  >
                    <Download size={16} />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Mobile: card fallback */}
      <div className="payment-cards-mobile" style={{ display: "none", flexDirection: "column", gap: 12, marginTop: 12 }}>
        {filtered.map((p) => (
          <div key={`mob-${p.id}`} className="card">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
              <div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "var(--color-text-main)" }}>{p.id}</div>
                <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>{p.date}</div>
              </div>
              <StatusBadge status={p.status} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
              {[
                { label: "Crop", value: p.crop },
                { label: "Quantity", value: p.quantity },
                { label: "Gross", value: p.grossAmount },
                { label: "Net Credit", value: p.netAmount },
              ].map(({ label, value }) => (
                <div key={label}>
                  <div style={{ fontSize: 11, color: "var(--color-text-muted)", marginBottom: 2 }}>{label}</div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)" }}>{value}</div>
                </div>
              ))}
            </div>
            {p.status === "completed" && (
              <button className="btn btn-secondary" style={{ width: "100%", fontSize: 13, height: 38 }} onClick={() => setReceipt(p)}>
                <FileText size={14} /> View Receipt
              </button>
            )}
          </div>
        ))}
      </div>

      {receipt && <ReceiptModal payment={receipt} onClose={() => setReceipt(null)} />}

      <style>{`
        @media (max-width: 767px) {
          .payment-table-header { display: none !important; }
          .payment-row { display: none !important; }
          .payment-cards-mobile { display: flex !important; }
        }
      `}</style>
    </div>
  );
}
