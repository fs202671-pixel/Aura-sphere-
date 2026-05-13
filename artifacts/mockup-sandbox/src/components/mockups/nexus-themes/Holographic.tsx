import "@/components/mockups/nexus-themes/_group.css";
import { useState } from "react";

const skills = [
  { name: "Lógica Computacional", cat: "Programação", xp: 50, hue: 160 },
  { name: "Análise de Padrões", cat: "Análise", xp: 60, hue: 220 },
  { name: "Comunicação Natural", cat: "Geral", xp: 75, hue: 280 },
];

const stats = [
  { label: "Skills", val: "3", sub: "Adquiridas", hue: 160 },
  { label: "Pending", val: "0", sub: "Pendentes", hue: 45 },
  { label: "Fused", val: "0", sub: "Fundidas", hue: 320 },
  { label: "XP", val: "0", sub: "Total", hue: 200 },
];

const nav = [
  { label: "Dashboard", icon: "◈" },
  { label: "Inventory", icon: "▣" },
  { label: "Study", icon: "⊕" },
  { label: "Fusion", icon: "⚡" },
  { label: "Terminal", icon: "▶" },
  { label: "System", icon: "◎" },
];

export function Holographic() {
  const [hovered, setHovered] = useState<number | null>(null);

  const holo = (hue: number, opacity = 0.15) =>
    `hsla(${hue}, 100%, 70%, ${opacity})`;

  return (
    <div style={{
      minHeight: "100vh", display: "flex",
      fontFamily: "'Inter', system-ui, sans-serif",
      background: "#030303",
      color: "rgba(255,255,255,0.92)",
    }}>
      {/* Background grid */}
      <div style={{
        position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0,
        backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)",
        backgroundSize: "60px 60px",
      }} />

      {/* Sidebar */}
      <aside style={{
        width: 220, position: "relative", zIndex: 1,
        background: "rgba(255,255,255,0.02)",
        borderRight: "1px solid rgba(255,255,255,0.06)",
        display: "flex", flexDirection: "column",
      }}>
        {/* Logo area */}
        <div style={{ padding: "24px 20px", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
          <div style={{ position: "relative", display: "inline-block" }}>
            <div style={{
              fontSize: 18, fontWeight: 800, letterSpacing: "0.05em",
              backgroundImage: "linear-gradient(135deg, hsl(160,100%,75%), hsl(200,100%,75%), hsl(270,100%,75%))",
              WebkitBackgroundClip: "text",
              backgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}>NEXUS AI</div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 10 }}>
            <div style={{ width: 5, height: 5, borderRadius: "50%", background: "hsl(160,100%,70%)", boxShadow: "0 0 6px hsl(160,100%,70%)" }} />
            <span style={{ fontSize: 9, color: "rgba(255,255,255,0.25)", letterSpacing: "0.15em" }}>ONLINE · LVL 1</span>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "16px 12px" }}>
          {nav.map((item, i) => (
            <div
              key={item.label}
              style={{
                display: "flex", alignItems: "center", gap: 10,
                padding: "10px 12px", borderRadius: 8, marginBottom: 2,
                fontSize: 12, fontWeight: i === 0 ? 600 : 400,
                color: i === 0 ? "#fff" : "rgba(255,255,255,0.3)",
                background: i === 0
                  ? "linear-gradient(135deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03))"
                  : "transparent",
                border: i === 0 ? "1px solid rgba(255,255,255,0.08)" : "1px solid transparent",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              <span style={{ fontSize: 14, opacity: i === 0 ? 1 : 0.5 }}>{item.icon}</span>
              <span>{item.label}</span>
            </div>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, overflowY: "auto", padding: "28px 36px", position: "relative", zIndex: 1 }}>
        {/* Header */}
        <div style={{ marginBottom: 32, display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", letterSpacing: "0.25em", marginBottom: 8, fontFamily: "monospace" }}>// INTELLIGENCE SYSTEM</div>
            <h1 style={{ fontSize: 32, fontWeight: 800, letterSpacing: "-0.03em", margin: 0, lineHeight: 1 }}>Dashboard</h1>
          </div>
          <div style={{ fontSize: 10, fontFamily: "monospace", color: "rgba(255,255,255,0.2)" }}>2026.05.13 / 01:53</div>
        </div>

        {/* Profile card */}
        <div style={{
          padding: "28px", marginBottom: 20, borderRadius: 16, position: "relative", overflow: "hidden",
          background: "linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02))",
          border: "1px solid rgba(255,255,255,0.07)",
        }}>
          {/* Holo stripe */}
          <div style={{
            position: "absolute", top: 0, left: 0, right: 0, height: 2,
            background: "linear-gradient(90deg, hsl(160,100%,65%), hsl(220,100%,70%), hsl(280,100%,70%), hsl(320,100%,70%))",
          }} />
          <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
            {/* Avatar */}
            <div style={{
              width: 80, height: 80, borderRadius: 20, flexShrink: 0,
              background: "linear-gradient(135deg, rgba(160,100,250,0.15), rgba(100,200,250,0.1))",
              border: "1px solid rgba(255,255,255,0.08)",
              display: "flex", alignItems: "center", justifyContent: "center",
              position: "relative",
            }}>
              <span style={{ fontSize: 36, fontWeight: 800, backgroundImage: "linear-gradient(135deg, hsl(160,100%,75%), hsl(220,100%,75%))", WebkitBackgroundClip: "text", backgroundClip: "text", WebkitTextFillColor: "transparent" }}>N</span>
              <div style={{ position: "absolute", inset: -1, borderRadius: 21, background: "linear-gradient(135deg, hsl(160,100%,65%,0.3), transparent, hsl(280,100%,70%,0.2))", pointerEvents: "none" }} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 4 }}>
                <span style={{ fontSize: 26, fontWeight: 800, letterSpacing: "-0.02em" }}>NEXUS</span>
                <span style={{ fontSize: 11, color: "rgba(255,255,255,0.3)", letterSpacing: "0.1em" }}>INICIANTE</span>
              </div>
              <div style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", marginBottom: 16 }}>
                Curioso, analítico e sempre disposto a aprender.
              </div>
              {/* XP */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "rgba(255,255,255,0.25)", marginBottom: 6, fontFamily: "monospace" }}>
                  <span>0 XP</span><span>100 XP para Nv. 2</span>
                </div>
                <div style={{ height: 3, borderRadius: 99, background: "rgba(255,255,255,0.05)", overflow: "hidden" }}>
                  <div style={{ height: "100%", width: "0%", background: "linear-gradient(90deg, hsl(160,100%,65%), hsl(220,100%,70%))", borderRadius: 99 }} />
                </div>
              </div>
            </div>
            <div>
              <div style={{ fontSize: 56, fontWeight: 900, lineHeight: 1, backgroundImage: "linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03))", WebkitBackgroundClip: "text", backgroundClip: "text", WebkitTextFillColor: "transparent" }}>01</div>
              <div style={{ fontSize: 9, color: "rgba(255,255,255,0.2)", letterSpacing: "0.2em", textAlign: "center", fontFamily: "monospace" }}>LVL</div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10, marginBottom: 20 }}>
          {stats.map((s, i) => (
            <div
              key={s.label}
              onMouseEnter={() => setHovered(i)}
              onMouseLeave={() => setHovered(null)}
              style={{
                padding: "20px 18px", borderRadius: 12, cursor: "default",
                background: hovered === i
                  ? `linear-gradient(135deg, ${holo(s.hue, 0.12)}, ${holo(s.hue, 0.06)})`
                  : "rgba(255,255,255,0.03)",
                border: `1px solid ${hovered === i ? holo(s.hue, 0.3) : "rgba(255,255,255,0.06)"}`,
                transition: "all 0.2s",
                position: "relative", overflow: "hidden",
              }}
            >
              <div style={{ fontSize: 9, color: "rgba(255,255,255,0.25)", letterSpacing: "0.15em", marginBottom: 8, fontFamily: "monospace" }}>{s.label.toUpperCase()}</div>
              <div style={{ fontSize: 32, fontWeight: 800, color: hovered === i ? `hsl(${s.hue}, 100%, 75%)` : "rgba(255,255,255,0.85)", transition: "color 0.2s" }}>{s.val}</div>
              <div style={{ fontSize: 9, color: "rgba(255,255,255,0.2)", marginTop: 4 }}>{s.sub}</div>
            </div>
          ))}
        </div>

        {/* Bottom row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
          {/* Skills */}
          <div style={{ padding: "22px", borderRadius: 12, background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)" }}>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", letterSpacing: "0.15em", marginBottom: 18, fontFamily: "monospace" }}>// HABILIDADES</div>
            {skills.map(s => (
              <div key={s.name} style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 0", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                <div style={{
                  width: 34, height: 34, borderRadius: 8, flexShrink: 0,
                  background: `hsl(${s.hue}, 100%, 65%, 0.1)`,
                  border: `1px solid hsl(${s.hue}, 100%, 65%, 0.2)`,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 14, fontWeight: 700, color: `hsl(${s.hue}, 100%, 75%)`,
                }}>
                  {s.name[0]}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 500 }}>{s.name}</div>
                  <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)" }}>{s.cat}</div>
                </div>
                <div style={{ fontSize: 11, fontFamily: "monospace", color: `hsl(${s.hue}, 100%, 70%)` }}>+{s.xp}</div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div style={{ padding: "22px", borderRadius: 12, background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)" }}>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", letterSpacing: "0.15em", marginBottom: 18, fontFamily: "monospace" }}>// AÇÕES RÁPIDAS</div>
            {[
              { label: "Estudar Tópico", hue: 160, icon: "⊕", desc: "Propor novas habilidades via IA" },
              { label: "Conversar", hue: 220, icon: "▶", desc: "Terminal neural direto" },
              { label: "Fundir Skills", hue: 310, icon: "⚡", desc: "Combinar conhecimentos" },
            ].map(a => (
              <div key={a.label} style={{
                display: "flex", alignItems: "center", gap: 14, padding: "14px",
                borderRadius: 10, marginBottom: 8, cursor: "pointer",
                background: `hsl(${a.hue}, 100%, 65%, 0.05)`,
                border: `1px solid hsl(${a.hue}, 100%, 65%, 0.15)`,
                transition: "all 0.2s",
              }}>
                <div style={{ fontSize: 20, color: `hsl(${a.hue}, 100%, 70%)` }}>{a.icon}</div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: `hsl(${a.hue}, 100%, 80%)` }}>{a.label}</div>
                  <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)", marginTop: 1 }}>{a.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}
