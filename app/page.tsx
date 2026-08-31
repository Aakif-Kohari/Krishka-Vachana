"use client";
import { useState } from "react";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import HeroSection from "@/components/landing/HeroSection";
import FeaturesSection from "@/components/landing/FeaturesSection";
import HowItWorksSection from "@/components/landing/HowItWorksSection";
import CTASection from "@/components/landing/CTASection";

export default function LandingPage() {
  const [lang, setLang] = useState<"en" | "hi">("en");
  const toggleLang = () => setLang((l) => (l === "en" ? "hi" : "en"));

  return (
    <>
      <Navbar lang={lang} onToggleLang={toggleLang} />
      <main>
        <HeroSection lang={lang} />
        <FeaturesSection lang={lang} />
        <HowItWorksSection lang={lang} />
        <CTASection lang={lang} />
      </main>
      <Footer lang={lang} />
    </>
  );
}
