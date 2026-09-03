"use client";
import { useState } from "react";
import {
  CalendarCheck,
  MapPin,
  Clock,
  Wheat,
  Plus,
  Search,
  ChevronDown,
  X,
  CheckCircle2,
  AlertCircle,
  Users,
} from "lucide-react";

const allBookings = [
  {
    id: "BK-2024-1071",
    crop: "Wheat",
    quantity: "18 Quintal",
    date: "5 Sep 2026",
    time: "09:00 AM – 11:00 AM",
    centre: "Rajpur APMC, MP",
    slotNumber: "S-14",
    queuePosition: 3,
    totalInQueue: 28,
    status: "confirmed",
    notes: "Bring original land records and identity proof.",
  },
  {
    id: "BK-2024-1043",
    crop: "Maize",
    quantity: "10 Quintal",
    date: "28 Aug 2026",
    time: "11:00 AM – 01:00 PM",
    centre: "Khandwa Mandi, MP",
    slotNumber: "S-07",
    queuePosition: null,
    totalInQueue: null,
    status: "completed",
    notes: "",
  },
  {
    id: "BK-2024-1029",
    crop: "Soybean",
    quantity: "22 Quintal",
    date: "15 Aug 2026",
    time: "08:00 AM – 10:00 AM",
    centre: "Rajpur APMC, MP",
    slotNumber: "S-03",
    queuePosition: null,
    totalInQueue: null,
    status: "completed",
    notes: "",
  },
  {
    id: "BK-2024-1012",
    crop: "Soybean",
    quantity: "15 Quintal",
    date: "2 Aug 2026",
    time: "02:00 PM – 04:00 PM",
    centre: "Harda Centre, MP",
    slotNumber: "S-21",
    queuePosition: null,
    totalInQueue: null,
    status: "cancelled",
    notes: "Cancelled by farmer.",
  },
];

const statusOptions = ["All", "Confirmed", "Completed", "Cancelled", "Waiting"];

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

function QueueProgressBar({ position, total }: { position: number; total: number }) {
  const pct = Math.max(0, Math.min(100, ((total - position) / total) * 100));
  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
        <span style={{ fontSize: 12, color: "var(--color-text-muted)" }}>Queue Progress</span>
        <span style={{ fontSize: 12, fontWeight: 600, color: "var(--color-primary)" }}>
          #{position} of {total}
        </span>
      </div>
      <div style={{ height: 6, background: "var(--color-divider)", borderRadius: 9999, overflow: "hidden" }}>
        <div style={{ height: "100%", width: `${pct}%`, background: "var(--color-primary-btn)", borderRadius: 9999, transition: "width 0.4s ease" }} />
      </div>
    </div>
  );
}

// New Booking Modal
function NewBookingModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({ crop: "", quantity: "", centre: "", date: "", slot: "" });

  const centres = ["Rajpur APMC, MP", "Khandwa Mandi, MP", "Harda Centre, MP", "Burhanpur Mandi, MP"];
  const slots = ["08:00 AM – 10:00 AM", "10:00 AM – 12:00 PM", "12:00 PM – 02:00 PM", "02:00 PM – 04:00 PM"];
  const crops = ["Wheat", "Maize", "Soybean", "Cotton", "Paddy"];

  const set = (k: string) => (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const labelStyle = { fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6, display: "block" } as const;
  const inputStyle = {
    width: "100%", height: 44, background: "#fff",
    border: "1px solid var(--color-border)", borderRadius: 8,
    padding: "0 12px", fontSize: 14, color: "var(--color-text-main)",
    outline: "none", display: "block",
  } as const;

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 100, display: "flex", alignItems: "center", justifyContent: "center", padding: 16 }}>
      <div onClick={onClose} style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.4)" }} />
      <div style={{
        position: "relative", background: "#fff", borderRadius: 16,
        padding: 24, width: "100%", maxWidth: 480,
        boxShadow: "var(--shadow-lg)", zIndex: 1,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 className="text-h3" style={{ color: "var(--color-text-main)" }}>Book a Procurement Slot</h2>
          <button onClick={onClose} className="btn btn-ghost" style={{ height: 32, width: 32, padding: 0 }} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        {/* Step indicator */}
        <div style={{ display: "flex", gap: 8, marginBottom: 24, alignItems: "center" }}>
          {[1, 2, 3].map((s) => (
            <div key={s} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <div style={{
                width: 28, height: 28, borderRadius: "9999px",
                background: step >= s ? "var(--color-primary-btn)" : "var(--color-divider)",
                color: step >= s ? "#fff" : "var(--color-text-muted)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 13, fontWeight: 700, flexShrink: 0,
                transition: "background 0.2s",
              }}>
                {step > s ? <CheckCircle2 size={14} /> : s}
              </div>
              <span style={{ fontSize: 12, color: step === s ? "var(--color-primary)" : "var(--color-text-muted)", fontWeight: step === s ? 600 : 400, whiteSpace: "nowrap" }}>
                {s === 1 ? "Crop" : s === 2 ? "Location & Time" : "Confirm"}
              </span>
              {s < 3 && <div style={{ flex: 1, height: 1, background: "var(--color-divider)", minWidth: 16 }} />}
            </div>
          ))}
        </div>

        {step === 1 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label style={labelStyle}>Crop Type</label>
              <select value={form.crop} onChange={set("crop")} style={inputStyle}>
                <option value="">Select crop…</option>
                {crops.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Quantity (Quintal)</label>
              <input type="number" placeholder="e.g. 15" value={form.quantity} onChange={set("quantity")} style={inputStyle} min={1} />
            </div>
            <button
              className="btn btn-primary"
              style={{ width: "100%", marginTop: 8 }}
              disabled={!form.crop || !form.quantity}
              onClick={() => setStep(2)}
            >
              Next: Choose Location
            </button>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label style={labelStyle}>Procurement Centre</label>
              <select value={form.centre} onChange={set("centre")} style={inputStyle}>
                <option value="">Select centre…</option>
                {centres.map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Preferred Date</label>
              <input type="date" value={form.date} onChange={set("date")} style={inputStyle} min={new Date().toISOString().split("T")[0]} />
            </div>
            <div>
              <label style={labelStyle}>Time Slot</label>
              <select value={form.slot} onChange={set("slot")} style={inputStyle}>
                <option value="">Select slot…</option>
                {slots.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setStep(1)}>Back</button>
              <button
                className="btn btn-primary"
                style={{ flex: 1 }}
                disabled={!form.centre || !form.date || !form.slot}
                onClick={() => setStep(3)}
              >
                Review Booking
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div style={{ background: "var(--color-primary-bg)", borderRadius: 12, padding: 16, display: "flex", flexDirection: "column", gap: 10 }}>
              {[
                { label: "Crop", value: form.crop },
                { label: "Quantity", value: `${form.quantity} Quintal` },
                { label: "Centre", value: form.centre },
                { label: "Date", value: form.date },
                { label: "Time Slot", value: form.slot },
              ].map(({ label, value }) => (
                <div key={label} style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
                  <span style={{ color: "var(--color-text-muted)" }}>{label}</span>
                  <span style={{ fontWeight: 600, color: "var(--color-text-main)" }}>{value}</span>
                </div>
              ))}
            </div>
            <div style={{ background: "var(--color-info-bg)", borderRadius: 8, padding: "10px 14px", display: "flex", gap: 10, alignItems: "flex-start" }}>
              <AlertCircle size={16} color="var(--color-info)" style={{ flexShrink: 0, marginTop: 1 }} />
              <span style={{ fontSize: 13, color: "#1e4a9a" }}>Please carry land records and your Krishka Vachana ID to the centre.</span>
            </div>
            <div style={{ display: "flex", gap: 12 }}>
              <button className="btn btn-secondary" style={{ flex: 1 }} onClick={() => setStep(2)}>Back</button>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={onClose}>Confirm Booking</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function BookingPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("All");
  const [showModal, setShowModal] = useState(false);
  const [expanded, setExpanded] = useState<string | null>(null);

  const filtered = allBookings.filter((b) => {
    const matchesSearch = b.id.toLowerCase().includes(search.toLowerCase()) ||
      b.crop.toLowerCase().includes(search.toLowerCase()) ||
      b.centre.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === "All" || b.status === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 24, gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 className="text-h1" style={{ color: "var(--color-text-main)" }}>My Bookings</h1>
          <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
            Manage your procurement slot bookings and track queue status.
          </p>
        </div>
        <button id="book-slot-btn" className="btn btn-primary" onClick={() => setShowModal(true)} style={{ flexShrink: 0 }}>
          <Plus size={16} /> Book a Slot
        </button>
      </div>

      {/* Active queue card */}
      {allBookings.find((b) => b.status === "confirmed") && (
        <div className="card" style={{ marginBottom: 24, background: "var(--color-primary-bg)", borderColor: "#b0ddc5" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
            <Users size={18} color="var(--color-primary-btn)" />
            <span className="text-h4" style={{ color: "var(--color-primary-dark)" }}>Active Queue — BK-2024-1071</span>
            <span className="badge badge-confirmed" style={{ marginLeft: "auto" }}>Confirmed</span>
          </div>
          <QueueProgressBar position={3} total={28} />
          <div style={{ display: "flex", gap: 24, marginTop: 16, flexWrap: "wrap" }}>
            {[
              { icon: <Clock size={14} />, text: "Est. wait: ~45 min" },
              { icon: <MapPin size={14} />, text: "Rajpur APMC, MP" },
              { icon: <CalendarCheck size={14} />, text: "5 Sep 2026, 09:00 AM" },
            ].map(({ icon, text }) => (
              <div key={text} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, color: "var(--color-primary)" }}>
                {icon} {text}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
          <Search size={15} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--color-text-muted)" }} />
          <input
            type="text"
            placeholder="Search by ID, crop, or centre…"
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
            {statusOptions.map((s) => <option key={s}>{s}</option>)}
          </select>
          <ChevronDown size={15} style={{ position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)", pointerEvents: "none", color: "var(--color-text-muted)" }} />
        </div>
      </div>

      {/* Booking list */}
      {filtered.length === 0 ? (
        <div style={{ textAlign: "center", padding: "64px 24px" }}>
          <CalendarCheck size={40} color="var(--color-border)" style={{ margin: "0 auto 16px" }} />
          <h3 className="text-h3" style={{ color: "var(--color-text-secondary)", marginBottom: 8 }}>No bookings found</h3>
          <p className="text-sm" style={{ color: "var(--color-text-muted)", marginBottom: 20 }}>
            {search || statusFilter !== "All" ? "Try adjusting your filters." : "You haven't booked a procurement slot yet."}
          </p>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}><Plus size={16} /> Book a Slot</button>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {filtered.map((b) => (
            <div key={b.id} className="card" style={{ padding: 0, overflow: "hidden" }}>
              {/* Row */}
              <div
                style={{ padding: "16px 20px", display: "flex", alignItems: "center", gap: 16, cursor: "pointer", flexWrap: "wrap" }}
                onClick={() => setExpanded(expanded === b.id ? null : b.id)}
              >
                <span style={{
                  width: 40, height: 40, borderRadius: 8, flexShrink: 0,
                  background: b.status === "confirmed" ? "var(--color-primary-bg)" : b.status === "cancelled" ? "var(--color-error-bg)" : "var(--color-bg-light)",
                  color: b.status === "confirmed" ? "var(--color-primary-btn)" : b.status === "cancelled" ? "var(--color-error)" : "var(--color-text-muted)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  <Wheat size={18} />
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                    <span style={{ fontSize: 14, fontWeight: 600, color: "var(--color-text-main)" }}>{b.crop} · {b.quantity}</span>
                    <StatusBadge status={b.status} />
                  </div>
                  <div style={{ fontSize: 12, color: "var(--color-text-muted)", marginTop: 3 }}>
                    {b.id} · {b.centre} · Slot {b.slotNumber}
                  </div>
                </div>
                <div style={{ textAlign: "right", flexShrink: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "var(--color-text-main)" }}>{b.date}</div>
                  <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>{b.time}</div>
                </div>
                <ChevronDown
                  size={18}
                  color="var(--color-text-muted)"
                  style={{ flexShrink: 0, transform: expanded === b.id ? "rotate(180deg)" : "none", transition: "transform 0.2s" }}
                />
              </div>

              {/* Expanded details */}
              {expanded === b.id && (
                <div style={{ borderTop: "1px solid var(--color-divider)", padding: "16px 20px", background: "var(--color-bg-page)", display: "flex", flexDirection: "column", gap: 12 }}>
                  {b.queuePosition && b.totalInQueue && (
                    <QueueProgressBar position={b.queuePosition} total={b.totalInQueue} />
                  )}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }} className="detail-grid">
                    {[
                      { label: "Booking ID", value: b.id },
                      { label: "Slot Number", value: b.slotNumber },
                      { label: "Centre", value: b.centre },
                      { label: "Date & Time", value: `${b.date}, ${b.time}` },
                    ].map(({ label, value }) => (
                      <div key={label}>
                        <div style={{ fontSize: 12, color: "var(--color-text-muted)" }}>{label}</div>
                        <div style={{ fontSize: 14, fontWeight: 500, color: "var(--color-text-main)", marginTop: 2 }}>{value}</div>
                      </div>
                    ))}
                  </div>
                  {b.notes && (
                    <div style={{ background: "var(--color-info-bg)", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: "#1e4a9a", display: "flex", gap: 8, alignItems: "flex-start" }}>
                      <AlertCircle size={15} color="var(--color-info)" style={{ flexShrink: 0, marginTop: 1 }} />
                      {b.notes}
                    </div>
                  )}
                  {b.status === "confirmed" && (
                    <div style={{ display: "flex", gap: 12 }}>
                      <button className="btn btn-secondary" style={{ fontSize: 13, height: 38 }}>Reschedule</button>
                      <button className="btn btn-ghost" style={{ fontSize: 13, height: 38, color: "var(--color-error)" }}>Cancel Booking</button>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {showModal && <NewBookingModal onClose={() => setShowModal(false)} />}

      <style>{`
        @media (max-width: 767px) {
          .detail-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
