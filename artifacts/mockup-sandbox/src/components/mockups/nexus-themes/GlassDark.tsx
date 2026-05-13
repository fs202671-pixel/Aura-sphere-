import "@/components/mockups/nexus-themes/_group.css";

const skills = [
  { name: "Lógica Computacional", cat: "Programação", xp: 50, color: "#34d399" },
  { name: "Análise de Padrões", cat: "Análise", xp: 60, color: "#60a5fa" },
  { name: "Comunicação Natural", cat: "Geral", xp: 75, color: "#a78bfa" },
];

const stats = [
  { label: "Habilidades", val: 3, color: "#34d399" },
  { label: "Pendentes", val: 0, color: "#fbbf24" },
  { label: "Fundidas", val: 0, color: "#f472b6" },
  { label: "XP Total", val: 0, color: "#60a5fa" },
];

const nav = ["Dashboard", "Inventory", "Study", "Fusion", "Terminal", "System"];

const glass = {
  background: "rgba(255,255,255,0.03)",
  border: "1px solid rgba(255,255,255,0.07)",
  backdropFilter: "blur(20px)",
};

export function GlassDark() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", fontFamily: "'Inter', system-ui, sans-serif", background: "#080808", color: "rgba(255,255,255,0.9)" }}>
      {/* Ambient glows */}
      <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 0 }}>
        <div style={{ position: "absolute", top: -200, left: -200, width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(52,211,153,0.04) 0%, transparent 70%)" }} />
        <div style={{ position: "absolute", bottom: -200, right: -200, width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(96,165,250,0.04) 0%, transparent 70%)" }} />
      </div>

      {/* Sidebar */}
      <aside style={{ width: 240, ...glass, borderRight: "1px solid rgba(255,255,255,0.06)", display: "flex", flexDirection: "column", position: "relative", zIndex: 1 }}>
        <div style={{ padding: "28px 24px 24px", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
            <div style={{ width: 36, height: 36, borderRadius: 8, background: "rgba(52,211,153,0.1)", border: "1px solid rgba(52,211,153,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontSize: 16, color: "#34d399" }}>◈</span>
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 600, letterSpacing: "0.02em" }}>NEXUS AI</div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.3)", marginTop: 1 }}>v1.0 · Online</div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px", borderRadius: 8, background: "rgba(52,211,153,0.05)", border: "1px solid rgba(52,211,153,0.1)" }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399", boxShadow: "0 0 8px #34d399" }} />
            <span style={{ fontSize: 10, color: "rgba(255,255,255,0.4)", letterSpacing: "0.05em" }}>Neural Link Active</span>
          </div>
        </div>

        <nav style={{ flex: 1, padding: "12px 12px" }}>
          {nav.map((item, i) => (
            <div
              key={item}
              style={{
                padding: "10px 14px",
                borderRadius: 8,
                marginBottom: 2,
                fontSize: 13,
                fontWeight: i === 0 ? 500 : 400,
                color: i === 0 ? "#fff" : "rgba(255,255,255,0.35)",
                background: i === 0 ? "rgba(255,255,255,0.06)" : "transparent",
                border: i === 0 ? "1px solid rgba(255,255,255,0.08)" : "1px solid transparent",
                cursor: "pointer",
              }}
            >
              {item}
            </div>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, overflowY: "auto", padding: "32px", position: "relative", zIndex: 1 }}>
        <div style={{ maxWidth: 900 }}>
          {/* Header */}
          <div style={{ marginBottom: 32 }}>
            <div style={{ fontSize: 11, color: "rgba(255,255,255,0.2)", letterSpacing: "0.15em", marginBottom: 6 }}>// Sistema Neural Ativo</div>
            <div style={{ fontSize: 28, fontWeight: 600, letterSpacing: "-0.02em" }}>Dashboard</div>
          </div>

          {/* Profile card */}
          <div style={{ ...glass, borderRadius: 16, padding: "28px", marginBottom: 24, position: "relative", overflow: "hidden" }}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 1, background: "linear-gradient(90deg, transparent, rgba(52,211,153,0.5), transparent)" }} />
            <div style={{ display: "flex", gap: 24, alignItems: "flex-start" }}>
              <div style={{ width: 80, height: 80, borderRadius: 16, background: "rgba(52,211,153,0.08)", border: "1px solid rgba(52,211,153,0.15)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <span style={{ fontSize: 32, color: "rgba(52,211,153,0.8)" }}>◈</span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 22, fontWeight: 600, marginBottom: 4 }}>NEXUS</div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", marginBottom: 16 }}>Classe: Iniciante · Personalidade: Analítico</div>
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "rgba(255,255,255,0.3)", marginBottom: 6 }}>
                    <span>XP: 0</span>
                    <span>Próximo nível: 100 XP</span>
                  </div>
                  <div style={{ height: 4, borderRadius: 99, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: "0%", background: "linear-gradient(90deg, #34d399, #60a5fa)", borderRadius: 99 }} />
                  </div>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 44, fontWeight: 700, color: "rgba(255,255,255,0.1)", lineHeight: 1 }}>01</div>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.2)", letterSpacing: "0.1em" }}>LEVEL</div>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
            {stats.map(s => (
              <div key={s.label} style={{ ...glass, borderRadius: 12, padding: "20px", position: "relative", overflow: "hidden" }}>
                <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)", letterSpacing: "0.05em", marginBottom: 10 }}>{s.label}</div>
                <div style={{ fontSize: 30, fontWeight: 700, color: s.color }}>{s.val}</div>
                <div style={{ position: "absolute", bottom: 0, right: 0, width: 40, height: 40, borderRadius: "50%", background: `radial-gradient(circle, ${s.color}15, transparent)`, transform: "translate(10px, 10px)" }} />
              </div>
            ))}
          </div>

          {/* Bottom */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div style={{ ...glass, borderRadius: 12, padding: "24px" }}>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.25)", letterSpacing: "0.1em", marginBottom: 18 }}>HABILIDADES RECENTES</div>
              {skills.map(s => (
                <div key={s.name} style={{ display: "flex", gap: 12, alignItems: "center", padding: "10px 0", borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                  <div style={{ width: 32, height: 32, borderRadius: 8, background: `${s.color}15`, border: `1px solid ${s.color}25`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <span style={{ fontSize: 14, color: s.color }}>{s.name[0]}</span>
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 12, fontWeight: 500 }}>{s.name}</div>
                    <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)", marginTop: 1 }}>{s.cat}</div>
                  </div>
                  <div style={{ fontSize: 11, color: "#34d399" }}>+{s.xp}</div>
                </div>
              ))}
            </div>
            <div style={{ ...glass, borderRadius: 12, padding: "24px" }}>
              <div style={{ fontSize: 11, color: "rgba(255,255,255,0.25)", letterSpacing: "0.1em", marginBottom: 18 }}>AÇÕES RÁPIDAS</div>
              {[
                { label: "Estudar Tópico", color: "#34d399", desc: "Propor novos conhecimentos" },
                { label: "Conversar", color: "#60a5fa", desc: "Terminal de comunicação" },
                { label: "Fundir Skills", color: "#f472b6", desc: "Combinar habilidades" },
              ].map(a => (
                <div key={a.label} style={{ padding: "12px 14px", borderRadius: 10, border: `1px solid ${a.color}20`, background: `${a.color}08`, marginBottom: 8, cursor: "pointer" }}>
                  <div style={{ fontSize: 12, fontWeight: 500, color: a.color }}>{a.label}</div>
                  <div style={{ fontSize: 10, color: "rgba(255,255,255,0.25)", marginTop: 2 }}>{a.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
