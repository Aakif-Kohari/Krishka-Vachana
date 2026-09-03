import type { Metadata } from "next";
import BookingPage from "@/components/dashboard/BookingPage";

export const metadata: Metadata = {
  title: "My Bookings — Krishka Vachana",
  description: "View and manage your procurement slot bookings and queue status.",
};

export default function Page() {
  return <BookingPage />;
}
