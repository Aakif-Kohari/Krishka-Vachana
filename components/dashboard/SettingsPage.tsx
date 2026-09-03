"use client";
import { useState } from "react";
import { User, Phone, Building2, Bell, Shield, Check, Save } from "lucide-react";

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [profile, setProfile] = useState({
    name: "Ramesh Singh",
    farmerId: "KV-2024-0471",
    phone: "9876543210",
    district: "Khargone",
    village: "Rajpur",
    bankName: "State Bank of India",
    accountNo: "••••••••3490",
    ifsc: "SBIN0001420",
    smsAlerts: true,
    whatsappAlerts: true,
  });

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <h1 className="text-h1" style={{ color: "var(--color-text-main)" }}>Account Settings</h1>
        <p className="text-sm" style={{ color: "var(--color-text-muted)", marginTop: 4 }}>
          Manage your farmer profile, contact preferences, and verified bank account.
        </p>
      </div>

      {saved && (
        <div
          style={{
            background: "var(--color-success-bg)",
            border: "1px solid #b4e0c4",
            color: "var(--color-success)",
            padding: "12px 16px",
            borderRadius: 8,
            fontSize: 14,
            fontWeight: 500,
            marginBottom: 20,
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <Check size={18} /> Settings updated successfully!
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {/* Personal Details Card */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <User size={18} color="var(--color-primary-btn)" />
            <h2 className="text-h4" style={{ color: "var(--color-text-main)" }}>Farmer Profile</h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                Full Name
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                style={{
                  width: "100%",
                  height: 44,
                  borderRadius: 8,
                  border: "1px solid var(--color-border)",
                  padding: "0 12px",
                  fontSize: 14,
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                Farmer ID
              </label>
              <input
                type="text"
                disabled
                value={profile.farmerId}
                style={{
                  width: "100%",
                  height: 44,
                  borderRadius: 8,
                  border: "1px solid var(--color-border)",
                  padding: "0 12px",
                  fontSize: 14,
                  background: "var(--color-bg-light)",
                  color: "var(--color-text-muted)",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                Mobile Phone
              </label>
              <input
                type="text"
                value={profile.phone}
                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                style={{
                  width: "100%",
                  height: 44,
                  borderRadius: 8,
                  border: "1px solid var(--color-border)",
                  padding: "0 12px",
                  fontSize: 14,
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                District / Village
              </label>
              <input
                type="text"
                value={`${profile.district}, ${profile.village}`}
                onChange={(e) => setProfile({ ...profile, district: e.target.value })}
                style={{
                  width: "100%",
                  height: 44,
                  borderRadius: 8,
                  border: "1px solid var(--color-border)",
                  padding: "0 12px",
                  fontSize: 14,
                  outline: "none",
                }}
              />
            </div>
          </div>
        </div>

        {/* Bank Account Details */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Building2 size={18} color="var(--color-primary-btn)" />
            <h2 className="text-h4" style={{ color: "var(--color-text-main)" }}>Verified MSP Direct Bank Account</h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                Bank Name
              </label>
              <input
                type="text"
                value={profile.bankName}
                onChange={(e) => setProfile({ ...profile, bankName: e.target.value })}
                style={{
                  width: "100%",
                  height: 44,
                  borderRadius: 8,
                  border: "1px solid var(--color-border)",
                  padding: "0 12px",
                  fontSize: 14,
                  outline: "none",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 14, fontWeight: 500, color: "var(--color-text-secondary)", marginBottom: 6 }}>
                Account Number
              </label>
              <input
                type="text"
                value={profile.accountNo}
                onChange={(e) => setProfile({ ...profile, accountNo: e.target.value })}
                style={{
                  width: "100%",
                  height: 44,
                  borderRadius: 8,
                  border: "1px solid var(--color-border)",
                  padding: "0 12px",
                  fontSize: 14,
                  outline: "none",
                }}
              />
            </div>
          </div>
        </div>

        {/* Notification Preferences */}
        <div className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
            <Bell size={18} color="var(--color-primary-btn)" />
            <h2 className="text-h4" style={{ color: "var(--color-text-main)" }}>Notifications & Alerts</h2>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", fontSize: 14 }}>
              <input
                type="checkbox"
                checked={profile.smsAlerts}
                onChange={(e) => setProfile({ ...profile, smsAlerts: e.target.checked })}
                style={{ width: 18, height: 18, accentColor: "var(--color-primary-btn)" }}
              />
              <span>Receive SMS alerts when queue position updates</span>
            </label>
            <label style={{ display: "flex", alignItems: "center", gap: 10, cursor: "pointer", fontSize: 14 }}>
              <input
                type="checkbox"
                checked={profile.whatsappAlerts}
                onChange={(e) => setProfile({ ...profile, whatsappAlerts: e.target.checked })}
                style={{ width: 18, height: 18, accentColor: "var(--color-primary-btn)" }}
              />
              <span>Receive payment credit receipts on WhatsApp</span>
            </label>
          </div>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button type="submit" className="btn btn-primary" style={{ padding: "0 24px" }}>
            <Save size={16} /> Save Changes
          </button>
        </div>
      </form>
    </div>
  );
}
