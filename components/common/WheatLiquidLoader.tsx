"use client";
import React from "react";

interface WheatLiquidLoaderProps {
  size?: number;
  text?: string;
}

export default function WheatLiquidLoader({ size = 80, text }: WheatLiquidLoaderProps) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
      }}
    >
      <div style={{ position: "relative", width: size, height: size }}>
        {/* Outer subtle glow/border glass ring */}
        <div
          style={{
            position: "absolute",
            inset: -8,
            borderRadius: "50%",
            background: "radial-gradient(circle, rgba(46,139,87,0.15) 0%, rgba(255,255,255,0) 70%)",
            animation: "pulseGlow 2s ease-in-out infinite",
          }}
        />

        <svg
          width={size}
          height={size}
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            {/* Wheat Grass / Sprout Mask ClipPath */}
            <clipPath id="wheat-grass-clip">
              {/* Wheat head grains & leaves */}
              <path
                d="M50 90V40M50 40C45 35 35 32 30 35C28 42 38 48 50 48M50 40C55 35 65 32 70 35C72 42 62 48 50 48M50 55C42 50 30 48 25 52C23 60 35 65 50 63M50 55C58 50 70 48 75 52C77 60 65 65 50 63M50 70C40 68 28 68 22 72C22 79 34 82 50 77M50 70C60 68 72 68 78 72C78 79 66 82 50 77M50 25C47 18 42 12 50 5C58 12 53 18 50 25Z"
                stroke="#000"
                strokeWidth="7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </clipPath>
          </defs>

          {/* Background outline of Wheat Grass (Glass empty container) */}
          <path
            d="M50 90V40M50 40C45 35 35 32 30 35C28 42 38 48 50 48M50 40C55 35 65 32 70 35C72 42 62 48 50 48M50 55C42 50 30 48 25 52C23 60 35 65 50 63M50 55C58 50 70 48 75 52C77 60 65 65 50 63M50 70C40 68 28 68 22 72C22 79 34 82 50 77M50 70C60 68 72 68 78 72C78 79 66 82 50 77M50 25C47 18 42 12 50 5C58 12 53 18 50 25Z"
            stroke="#D1D8D3"
            strokeWidth="5"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="#F0FAF4"
          />

          {/* Liquid Fill Element inside ClipPath */}
          <g clipPath="url(#wheat-grass-clip)">
            {/* Wave Animated Liquid Rectangle */}
            <g className="wheat-liquid-wrapper">
              <path
                d="M 0 0 Q 25 -6, 50 0 T 100 0 V 120 H 0 Z"
                fill="url(#liquidGradient)"
              />
            </g>
          </g>

          {/* Foreground Crisp Stroke */}
          <path
            d="M50 90V40M50 40C45 35 35 32 30 35C28 42 38 48 50 48M50 40C55 35 65 32 70 35C72 42 62 48 50 48M50 55C42 50 30 48 25 52C23 60 35 65 50 63M50 55C58 50 70 48 75 52C77 60 65 65 50 63M50 70C40 68 28 68 22 72C22 79 34 82 50 77M50 70C60 68 72 68 78 72C78 79 66 82 50 77M50 25C47 18 42 12 50 5C58 12 53 18 50 25Z"
            stroke="var(--color-primary-dark)"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />

          <defs>
            <linearGradient id="liquidGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#2E8B57" />
              <stop offset="100%" stopColor="#123524" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {text && (
        <span
          style={{
            fontSize: 14,
            fontWeight: 600,
            color: "var(--color-primary-dark)",
            letterSpacing: "0.02em",
          }}
        >
          {text}
        </span>
      )}

      <style>{`
        @keyframes liquidFillUpDown {
          0% {
            transform: translateY(95px);
          }
          50% {
            transform: translateY(5px);
          }
          100% {
            transform: translateY(95px);
          }
        }

        @keyframes waveMotion {
          0% {
            transform: translateX(0);
          }
          100% {
            transform: translateX(-50px);
          }
        }

        @keyframes pulseGlow {
          0%, 100% { opacity: 0.4; transform: scale(1); }
          50% { opacity: 0.9; transform: scale(1.08); }
        }

        .wheat-liquid-wrapper {
          animation: liquidFillUpDown 2.4s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
