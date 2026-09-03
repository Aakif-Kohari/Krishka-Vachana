import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard — Krishka Vachana",
  description: "View your procurement summary, upcoming bookings, queue position, and recent payments.",
};

import DashboardPage from "@/components/dashboard/DashboardPage";

export default function Page() {
  return <DashboardPage />;
}
