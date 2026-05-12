import { useState, useEffect } from "react";
import { ParticleSphere } from "@/components/ParticleSphere";

interface CaosEntryProps {
  onEnter: () => void;
}

export function CaosEntry({ onEnter }: CaosEntryProps) {
  const [isEntering, setIsEntering] = useState(false);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 80);
    return () => clearTimeout(t);
  }, []);

  const handleEnter = () => {
    if (isEntering) return;
    setIsEntering(true);
    setTimeout(onEnter, 900);
  };

  return (
    <div className="fixed inset-0 bg-black flex flex-col items-center justify-center overflow-hidden select-none">

      {/* Ambient glow behind sphere */}
      <div
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
        aria-hidden="true"
      >
        <div
          className="rounded-full transition-all duration-1000"
          style={{
            width: isEntering ? "700px" : "420px",
            height: isEntering ? "700px" : "420px",
            background: "radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%)",
            filter: "blur(40px)",
            opacity: isEntering ? 0 : 1,
            transition: "all 0.9s ease",
          }}
        />
      </div>

      {/* Sphere container */}
      <div
        style={{
          width: "min(72vw, 340px)",
          height: "min(72vw, 340px)",
          opacity: visible ? (isEntering ? 0 : 1) : 0,
          transform: isEntering ? "scale(1.15)" : visible ? "scale(1)" : "scale(0.85)",
          transition: "opacity 0.9s ease, transform 0.9s ease",
        }}
      >
        <ParticleSphere
          state={isEntering ? "responding" : "listening"}
          shape="sphere"
          className="w-full h-full"
        />
      </div>

      {/* Title block */}
      <div
        className="mt-10 text-center"
        style={{
          opacity: visible ? (isEntering ? 0 : 1) : 0,
          transform: isEntering ? "translateY(12px)" : "translateY(0)",
          transition: "opacity 0.7s ease 0.1s, transform 0.7s ease 0.1s",
        }}
      >
        <h1
          className="font-bold text-white"
          style={{
            fontSize: "clamp(2.8rem, 8vw, 5rem)",
            letterSpacing: "0.35em",
            fontFamily: "'Inter', 'Helvetica Neue', sans-serif",
            textShadow: "0 0 40px rgba(255,255,255,0.25)",
          }}
        >
          CAOS
        </h1>
        <p
          className="mt-2 text-white/35 uppercase tracking-[0.25em]"
          style={{ fontSize: "clamp(0.65rem, 2vw, 0.8rem)" }}
        >
          Inteligência Artificial Pessoal
        </p>
      </div>

      {/* Enter button */}
      <button
        onClick={handleEnter}
        disabled={isEntering}
        className="mt-12 relative group"
        style={{
          opacity: visible ? (isEntering ? 0 : 1) : 0,
          transform: isEntering ? "translateY(8px)" : "translateY(0)",
          transition: "opacity 0.6s ease 0.2s, transform 0.6s ease 0.2s",
        }}
        aria-label="Entrar no Caos"
      >
        {/* Outer glow ring */}
        <span
          className="absolute inset-0 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-500"
          style={{
            background: "radial-gradient(ellipse, rgba(255,255,255,0.08) 0%, transparent 70%)",
            filter: "blur(8px)",
            transform: "scale(1.4)",
          }}
          aria-hidden="true"
        />
        <span
          className="relative flex items-center gap-3 px-10 py-4 rounded-full border text-white/60 group-hover:text-white transition-all duration-300"
          style={{
            borderColor: "rgba(255,255,255,0.15)",
            fontSize: "clamp(0.7rem, 2.5vw, 0.8rem)",
            letterSpacing: "0.22em",
            backdropFilter: "blur(4px)",
            background: "rgba(255,255,255,0.03)",
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.35)";
            (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.06)";
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.15)";
            (e.currentTarget as HTMLElement).style.background = "rgba(255,255,255,0.03)";
          }}
        >
          <span>ENTRAR NO CAOS</span>
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" aria-hidden="true">
            <path d="M1 7h12M8 2l5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </span>
      </button>

      {/* Bottom hint */}
      <p
        className="absolute bottom-8 text-white/18 text-center"
        style={{
          fontSize: "0.65rem",
          letterSpacing: "0.15em",
          opacity: visible ? (isEntering ? 0 : 1) : 0,
          transition: "opacity 0.6s ease 0.4s",
        }}
      >
        EVOLUTIVO · MODULAR · SEGURO
      </p>
    </div>
  );
}
