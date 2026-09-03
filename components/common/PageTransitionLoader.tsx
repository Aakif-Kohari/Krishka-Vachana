"use client";
import React, { useEffect, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import WheatLiquidLoader from "./WheatLiquidLoader";
import { useLanguage } from "@/context/LanguageContext";

export default function PageTransitionLoader() {
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { isHindi } = useLanguage();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Trigger brief liquid wheat grass loading state on route/search changes
    setLoading(true);
    const timer = setTimeout(() => {
      setLoading(false);
    }, 450);

    return () => clearTimeout(timer);
  }, [pathname, searchParams]);

  if (!loading) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        zIndex: 9999,
        background: "rgba(248, 250, 249, 0.82)",
        backdropFilter: "blur(6px)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        animation: "fadeIn 0.15s ease",
      }}
    >
      <div
        style={{
          background: "#ffffff",
          padding: "28px 36px",
          borderRadius: 20,
          boxShadow: "var(--shadow-lg)",
          border: "1px solid var(--color-divider)",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
        }}
      >
        <WheatLiquidLoader
          size={90}
          text={isHindi ? "डेटा लोड हो रहा है..." : "Fetching Procurement Data..."}
        />
      </div>
    </div>
  );
}
