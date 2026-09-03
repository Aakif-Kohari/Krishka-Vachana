import type { Metadata } from "next";
import PaymentsPage from "@/components/dashboard/PaymentsPage";

export const metadata: Metadata = {
  title: "Payments — Krishka Vachana",
  description: "Track all procurement payments, pending credits, and download receipts.",
};

export default function Page() {
  return <PaymentsPage />;
}
