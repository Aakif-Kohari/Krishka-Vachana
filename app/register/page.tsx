import type { Metadata } from "next";
import RegisterPage from "@/components/auth/RegisterPage";

export const metadata: Metadata = {
  title: "Farmer Registration — Krishka Vachana",
  description: "Register your farm and bank details to start booking smart procurement slots.",
};

export default function Page() {
  return <RegisterPage />;
}
