"use client";
import React, { useState } from "react";
import { MessageSquare, X, Send, Bot, Sparkles, Wheat } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

interface Message {
  id: string;
  sender: "bot" | "user";
  text: string;
  time: string;
}

export default function FarmerChatbot() {
  const { isHindi } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      sender: "bot",
      text: isHindi
        ? "नमस्ते किसान भाई! मैं आपका कृषक सहायक हूँ। आप उपार्जन, स्लॉट बुकिंग या एमएसपी भुगतान से जुड़ा कोई भी प्रश्न पूछ सकते हैं।"
        : "Namaste Farmer! I am your Krishka Sahayak. Ask me anything about procurement, slot booking, live queue, or MSP payments.",
      time: "Just now",
    },
  ]);

  const quickQuestions = isHindi
    ? [
        "स्लॉट कैसे बुक करें?",
        "एमएसपी भुगतान कब मिलेगा?",
        "मंडी में कौन से दस्तावेज चाहिए?",
        "लाइव कतार स्थिति कैसे देखें?",
      ]
    : [
        "How to book a slot?",
        "When will MSP payment arrive?",
        "What documents to bring to APMC?",
        "How to check live queue position?",
      ];

  const getBotResponse = (query: string): string => {
    const q = query.toLowerCase();

    if (q.includes("slot") || q.includes("स्लॉट") || q.includes("book")) {
      return isHindi
        ? "स्लॉट बुक करने के लिए अपने डैशबोर्ड में 'My Bookings' पर जाएँ और 'Book a Slot' पर क्लिक करें। फसल का प्रकार, मात्रा और पसंदीदा समय चुनें।"
        : "To book a procurement slot, navigate to 'My Bookings' on your dashboard and click 'Book a Slot'. Select your crop, quantity, and preferred time.";
    }

    if (q.includes("payment") || q.includes("भुगतान") || q.includes("msp") || q.includes("पैसा")) {
      return isHindi
        ? "उपार्जन और गुणवत्ता जांच पूरी होने के 48 घंटों के भीतर आपका एमएसपी भुगतान सीधे आपके पंजीकृत बैंक खाते में जमा कर दिया जाता है।"
        : "Your MSP payment is credited directly to your registered bank account within 48 hours after crop weighing and quality inspection.";
    }

    if (q.includes("document") || q.includes("दस्तावेज") || q.includes("paper") || q.includes("apmc")) {
      return isHindi
        ? "कृपया अपने साथ: (1) आधार कार्ड, (2) भू-अभिलेख/खसरा नकल, (3) बैंक पासबुक की प्रति, और (4) बुकिंग टोकन पर्ची लेकर आएं।"
        : "Please bring: (1) Aadhaar Card, (2) Land Registration / Khasra records, (3) Bank Passbook copy, and (4) Booking Token receipt.";
    }

    if (q.includes("queue") || q.includes("कतार") || q.includes("token")) {
      return isHindi
        ? "आप अपने डैशबोर्ड पर 'Queue Status' टैब पर क्लिक करके वास्तविक समय में अपनी कतार स्थिति और अनुमानित प्रतीक्षा समय देख सकते हैं।"
        : "You can track real-time queue position and estimated wait time by clicking the 'Queue Status' tab on your dashboard.";
    }

    return isHindi
      ? "धन्यवाद आपके सवाल के लिए। हमारी टीम आपके टोकन और उपार्जन केंद्र की पूरी मदद करेगी। किसी भी सहायता के लिए टोल फ्री 1800-180-1551 पर कॉल करें।"
      : "Thank you for your question. Our team ensures seamless procurement at your centre. For urgent queries, call toll-free 1800-180-1551.";
  };

  const handleSend = (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: text,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!textToSend) setInput("");

    setTimeout(() => {
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: "bot",
        text: getBotResponse(text),
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, botMsg]);
    }, 500);
  };

  return (
    <>
      {/* Floating Launcher Button */}
      <button
        id="farmer-chatbot-trigger"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: "fixed",
          bottom: 24,
          right: 24,
          zIndex: 9000,
          height: 52,
          padding: "0 20px",
          borderRadius: 9999,
          background: "var(--color-primary-dark)",
          color: "#ffffff",
          border: "none",
          boxShadow: "var(--shadow-lg)",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: 10,
          transition: "transform 0.2s ease, background-color 0.2s ease",
        }}
        onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
        onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        aria-label="Open Krishka Sahayak AI Chatbot"
      >
        <span
          style={{
            width: 32,
            height: 32,
            borderRadius: "50%",
            background: "var(--color-primary-btn)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Bot size={18} />
        </span>
        <span style={{ fontSize: 14, fontWeight: 600 }}>
          {isHindi ? "कृषक सहायक" : "Krishka Assistant"}
        </span>
        <Sparkles size={16} color="#ffd700" />
      </button>

      {/* Slide-Up Chat Window */}
      {isOpen && (
        <div
          style={{
            position: "fixed",
            bottom: 88,
            right: 24,
            zIndex: 9001,
            width: "calc(100vw - 32px)",
            maxWidth: 380,
            height: 520,
            background: "#ffffff",
            borderRadius: 16,
            boxShadow: "0 12px 36px rgba(0,0,0,0.18)",
            border: "1px solid var(--color-divider)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
            animation: "fadeUp 0.25s ease",
          }}
        >
          {/* Chat Header */}
          <div
            style={{
              padding: "14px 18px",
              background: "var(--color-primary-dark)",
              color: "#ffffff",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <span
                style={{
                  width: 34,
                  height: 34,
                  borderRadius: "50%",
                  background: "var(--color-primary-btn)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <Wheat size={18} />
              </span>
              <div>
                <div style={{ fontSize: 14, fontWeight: 700 }}>
                  {isHindi ? "कृषक सहायक AI" : "Krishka Sahayak AI"}
                </div>
                <div style={{ fontSize: 11, color: "var(--color-primary-light)", opacity: 0.9 }}>
                  {isHindi ? "24/7 किसान सहायता केंद्र" : "24/7 Farmer Helpdesk"}
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: "none",
                border: "none",
                color: "#ffffff",
                cursor: "pointer",
                padding: 4,
                display: "flex",
              }}
              aria-label="Close chatbot"
            >
              <X size={20} />
            </button>
          </div>

          {/* Messages Body */}
          <div
            style={{
              flex: 1,
              padding: 16,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 12,
              background: "var(--color-bg-page)",
            }}
          >
            {messages.map((m) => (
              <div
                key={m.id}
                style={{
                  alignSelf: m.sender === "user" ? "flex-end" : "flex-start",
                  maxWidth: "85%",
                }}
              >
                <div
                  style={{
                    padding: "10px 14px",
                    borderRadius: m.sender === "user" ? "14px 14px 2px 14px" : "14px 14px 14px 2px",
                    background: m.sender === "user" ? "var(--color-primary-btn)" : "#ffffff",
                    color: m.sender === "user" ? "#ffffff" : "var(--color-text-main)",
                    fontSize: 13,
                    lineHeight: "20px",
                    boxShadow: "var(--shadow-sm)",
                    border: m.sender === "bot" ? "1px solid var(--color-divider)" : "none",
                  }}
                >
                  {m.text}
                </div>
                <div
                  style={{
                    fontSize: 10,
                    color: "var(--color-text-muted)",
                    marginTop: 4,
                    textAlign: m.sender === "user" ? "right" : "left",
                  }}
                >
                  {m.time}
                </div>
              </div>
            ))}
          </div>

          {/* Quick Suggestion Chips */}
          <div
            style={{
              padding: "8px 12px",
              background: "#ffffff",
              borderTop: "1px solid var(--color-divider)",
              display: "flex",
              gap: 6,
              overflowX: "auto",
              whiteSpace: "nowrap",
            }}
          >
            {quickQuestions.map((q) => (
              <button
                key={q}
                onClick={() => handleSend(q)}
                style={{
                  padding: "4px 10px",
                  borderRadius: 9999,
                  background: "var(--color-primary-bg)",
                  color: "var(--color-primary-dark)",
                  border: "1px solid var(--color-primary-light)",
                  fontSize: 11,
                  fontWeight: 500,
                  cursor: "pointer",
                  flexShrink: 0,
                }}
              >
                {q}
              </button>
            ))}
          </div>

          {/* Chat Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            style={{
              padding: 12,
              background: "#ffffff",
              borderTop: "1px solid var(--color-divider)",
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <input
              type="text"
              placeholder={isHindi ? "सवाल पूछें..." : "Type your query..."}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              style={{
                flex: 1,
                height: 38,
                borderRadius: 8,
                border: "1px solid var(--color-border)",
                padding: "0 12px",
                fontSize: 13,
                outline: "none",
                background: "var(--color-bg-light)",
              }}
            />
            <button
              type="submit"
              className="btn btn-primary"
              style={{ height: 38, width: 38, padding: 0 }}
              aria-label="Send message"
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      )}
    </>
  );
}
