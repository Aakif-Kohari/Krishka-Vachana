"use client";
import React, { Suspense } from "react";
import { LanguageProvider } from "@/context/LanguageContext";
import PageTransitionLoader from "./PageTransitionLoader";
import FarmerChatbot from "./FarmerChatbot";

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <LanguageProvider>
      <Suspense fallback={null}>
        <PageTransitionLoader />
      </Suspense>
      {children}
      <FarmerChatbot />
    </LanguageProvider>
  );
}
