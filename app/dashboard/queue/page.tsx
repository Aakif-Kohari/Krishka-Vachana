import type { Metadata } from "next";
import QueuePage from "@/components/dashboard/QueuePage";

export const metadata: Metadata = {
  title: "Queue Status — Krishka Vachana",
  description: "Track your real-time queue position at the procurement centre.",
};

export default function Page() {
  return <QueuePage />;
}
