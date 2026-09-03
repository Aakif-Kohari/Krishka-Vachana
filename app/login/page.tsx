import type { Metadata } from "next";
import LoginPage from "@/components/auth/LoginPage";

export const metadata: Metadata = {
  title: "Farmer Login — Krishka Vachana",
  description: "Login to your Krishka Vachana farmer portal to manage slot bookings and view payments.",
};

export default function Page() {
  return <LoginPage />;
}
