import "@/components/mockups/nexus-themes/_group.css";

const skills = [
  { name: "Lógica Computacional", cat: "Programação", xp: 50, lvl: 1 },
  { name: "Análise de Padrões", cat: "Análise", xp: 60, lvl: 1 },
  { name: "Comunicação Natural", cat: "Geral", xp: 75, lvl: 2 },
];

const nav = [
  { label: "DASHBOARD", active: true },
  { label: "INVENTORY", active: false },
  { label: "STUDY", active: false },
  { label: "FUSION", active: false },
  { label: "TERMINAL", active: false },
  { label: "SYSTEM", active: false },
];

const activity = [
  "> SKILL ACQUIRED: Lógica Computacional +50XP",
  "> SKILL ACQUIRED: Análise de Padrões +60XP",
  "> NEURAL LINK ESTABLISHED",
  "> SYSTEM INITIALIZED: NEXUS v1.0",
];

export function Monolith() {
  return (
    <div className="monolith-root min-h-screen flex font-mono text-white" style={{ background: "#000", color: "#fff" }}>
      {/* Sidebar */}
      <aside style={{ width: 220, borderRight: "1px solid #222", display: "flex", flexDirection: "column", background: "#000" }}>
        {/* Logo */}
        <div style={{ padding: "28px 24px 20px", borderBottom: "1px solid #1a1a1a" }}>
          <div style={{ fontSize: 11, color: "#444", letterSpacing: "0.3em", marginBottom: 6 }}>ARTIFICIAL INTELLIGENCE</div>
          <div style={{ fontSize: 20, fontWeight: 700, letterSpacing: "0.1em", color: "#fff" }}>NEXUS_AI</div>
          <div style={{ marginTop: 10, display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#fff", boxShadow: "0 0 0 2px #fff4" }} />
            <span style={{ fontSize: 9, color: "#555", letterSpacing: "0.2em" }}>NEURAL LINK ACTIVE</span>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "16px 0" }}>
          {nav.map(item => (
            <div
              key={item.label}
              style={{
                padding: "10px 24px",
                fontSize: 10,
                letterSpacing: "0.2em",
                color: item.active ? "#fff" : "#444",
                borderLeft: item.active ? "2px solid #fff" : "2px solid transparent",
                background: item.active ? "#111" : "transparent",
                cursor: "pointer",
              }}
            >
              {item.label}
            </div>
          ))}
        </nav>

        {/* Status */}
        <div style={{ padding: "16px 24px", borderTop: "1px solid #1a1a1a" }}>
          <div style={{ fontSize: 9, color: "#333", letterSpacing: "0.2em", marginBottom: 4 }}>UPTIME</div>
          <div style={{ fontSize: 11, color: "#555" }}>00:42:17</div>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Top bar */}
        <div style={{ padding: "16px 32px", borderBottom: "1px solid #1a1a1a", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ fontSize: 9, color: "#444", letterSpacing: "0.3em" }}>// NEXUS INTELLIGENCE DASHBOARD</div>
          <div style={{ fontSize: 9, color: "#333", letterSpacing: "0.2em" }}>2026.05.13 — 01:53:22</div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "32px" }}>
          {/* Profile block */}
          <div style={{ marginBottom: 32, padding: "28px", border: "1px solid #1a1a1a", position: "relative" }}>
            <div style={{ position: "absolute", top: 0, left: 32, right: 32, height: 1, background: "#fff" }} />
            <div style={{ display: "flex", gap: 28, alignItems: "flex-start" }}>
              <div style={{ width: 72, height: 72, border: "1px solid #333", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <span style={{ fontSize: 28, fontWeight: 700 }}>N</span>
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 9, color: "#444", letterSpacing: "0.3em", marginBottom: 4 }}>DESIGNAÇÃO</div>
                <div style={{ fontSize: 26, fontWeight: 700, letterSpacing: "0.05em", marginBottom: 2 }}>NEXUS</div>
                <div style={{ fontSize: 10, color: "#555", letterSpacing: "0.15em", marginBottom: 16 }}>CLASSE: INICIANTE · NV.1</div>
                {/* XP bar */}
                <div>
                  <div style={{ display: "flex", justifyContent: "space-between", fontSize: 9, color: "#444", letterSpacing: "0.15em", marginBottom: 6 }}>
                    <span>XP: 0</span>
                    <span>PRÓXIMO: 100 XP</span>
                  </div>
                  <div style={{ height: 1, background: "#1a1a1a", position: "relative" }}>
                    <div style={{ position: "absolute", left: 0, top: 0, height: 1, width: "0%", background: "#fff" }} />
                  </div>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 48, fontWeight: 700, color: "#222", letterSpacing: "-0.02em" }}>01</div>
                <div style={{ fontSize: 9, color: "#444", letterSpacing: "0.2em" }}>LEVEL</div>
              </div>
            </div>
          </div>

          {/* Stats row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 1, marginBottom: 32, background: "#111" }}>
            {[
              { label: "HABILIDADES", val: "3" },
              { label: "PENDENTES", val: "0" },
              { label: "FUNDIDAS", val: "0" },
              { label: "XP TOTAL", val: "0" },
            ].map(s => (
              <div key={s.label} style={{ padding: "20px 24px", background: "#000", borderBottom: "1px solid #1a1a1a" }}>
                <div style={{ fontSize: 9, color: "#444", letterSpacing: "0.2em", marginBottom: 8 }}>{s.label}</div>
                <div style={{ fontSize: 32, fontWeight: 700 }}>{s.val}</div>
              </div>
            ))}
          </div>

          {/* Bottom 2-col */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 1, background: "#111" }}>
            {/* Skills */}
            <div style={{ background: "#000", padding: "24px", borderBottom: "1px solid #1a1a1a" }}>
              <div style={{ fontSize: 9, color: "#444", letterSpacing: "0.3em", marginBottom: 20 }}>// HABILIDADES RECENTES</div>
              {skills.map(s => (
                <div key={s.name} style={{ padding: "12px 0", borderBottom: "1px solid #111", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 2 }}>{s.name}</div>
                    <div style={{ fontSize: 9, color: "#555", letterSpacing: "0.15em" }}>{s.cat}</div>
                  </div>
                  <div style={{ fontSize: 10, color: "#555" }}>+{s.xp}</div>
                </div>
              ))}
            </div>

            {/* Activity */}
            <div style={{ background: "#000", padding: "24px" }}>
              <div style={{ fontSize: 9, color: "#444", letterSpacing: "0.3em", marginBottom: 20 }}>// LOG DE ATIVIDADE</div>
              {activity.map((a, i) => (
                <div key={i} style={{ fontSize: 9, color: "#444", marginBottom: 10, letterSpacing: "0.05em", lineHeight: 1.6 }}>{a}</div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
