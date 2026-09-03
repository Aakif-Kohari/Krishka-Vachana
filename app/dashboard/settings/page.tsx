import type { Metadata } from "next";
import SettingsPage from "@/components/dashboard/SettingsPage";

export const metadata: Metadata = {
  title: "Account Settings — Krishka Vachana",
  description: "Manage your profile, notification preferences, and bank details.",
};

export default function Page() {
  return <SettingsPage />;
}
