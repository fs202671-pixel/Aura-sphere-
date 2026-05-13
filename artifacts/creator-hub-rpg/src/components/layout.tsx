import { ReactNode, useState } from "react";
import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import { Home, Shield, Cpu, Zap, Layers, Map, Menu, X } from "lucide-react";

const navItems = [
  { href: "/", label: "Central", icon: Home },
  { href: "/arsenal", label: "Arsenal", icon: Shield },
  { href: "/fragmentos", label: "Fragmentos", icon: Layers },
  { href: "/entidades", label: "Entidades", icon: Cpu },
  { href: "/protocolos", label: "Protocolos", icon: Zap },
  { href: "/missoes", label: "Missões", icon: Map },
];

function NavLink({ item, onClick }: { item: typeof navItems[0]; onClick?: () => void }) {
  const [location] = useLocation();
  const isActive = location === item.href || (item.href !== "/" && location.startsWith(item.href));
  return (
    <Link href={item.href} onClick={onClick}>
      <div
        className={cn(
          "flex items-center gap-3 px-4 py-3 rounded-md cursor-pointer transition-all duration-200 border",
          isActive
            ? "bg-primary/10 border-primary/30 text-primary shadow-[0_0_15px_rgba(255,255,255,0.05)]"
            : "border-transparent text-muted-foreground hover:bg-card hover:text-foreground hover:border-border"
        )}
      >
        <item.icon className="w-5 h-5 flex-shrink-0" />
        <span className="font-medium tracking-wide">{item.label}</span>
      </div>
    </Link>
  );
}

export function AppLayout({ children }: { children: ReactNode }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [location] = useLocation();

  return (
    <div className="flex h-screen w-full bg-background text-foreground grid-bg overflow-hidden font-sans">
      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 border-r border-border bg-card/50 backdrop-blur-md flex-col relative z-20">
        <div className="p-6 border-b border-border">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-red-500 uppercase tracking-widest font-mono">
            CAOS
          </h1>
          <p className="text-xs text-muted-foreground font-mono mt-1">SISTEMA CENTRAL · IA</p>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink key={item.href} item={item} />
          ))}
        </nav>
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3 px-4 py-2 bg-black/40 rounded-md border border-border/50">
            <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e] animate-pulse" />
            <span className="text-xs text-muted-foreground font-mono">SISTEMA ATIVO</span>
          </div>
        </div>
      </aside>

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 z-30 flex items-center justify-between px-4 py-3 bg-background/95 backdrop-blur-md border-b border-border">
        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-red-500 uppercase tracking-widest font-mono">
          CAOS
        </h1>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_6px_#22c55e] animate-pulse" />
            <span className="text-[10px] text-muted-foreground font-mono">ATIVO</span>
          </div>
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-md border border-border text-muted-foreground hover:text-foreground transition-colors"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed top-14 left-0 right-0 z-20 bg-card/98 backdrop-blur-md border-b border-border p-4 space-y-1">
          {navItems.map((item) => (
            <NavLink key={item.href} item={item} onClick={() => setMobileMenuOpen(false)} />
          ))}
        </div>
      )}

      {/* Main Content */}
      <main className="flex-1 h-full overflow-y-auto relative z-10 pt-14 md:pt-0 pb-16 md:pb-0">
        {children}
      </main>

      {/* Mobile Bottom Nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-30 flex items-center justify-around bg-card/95 backdrop-blur-md border-t border-border px-2 py-2">
        {navItems.map((item) => {
          const isActive = location === item.href || (item.href !== "/" && location.startsWith(item.href));
          return (
            <Link key={item.href} href={item.href} onClick={() => setMobileMenuOpen(false)}>
              <div className={cn(
                "flex flex-col items-center gap-0.5 px-2 py-1 rounded-md transition-all",
                isActive ? "text-primary" : "text-muted-foreground"
              )}>
                <item.icon className={cn("w-5 h-5", isActive && "drop-shadow-[0_0_6px_currentColor]")} />
                <span className="text-[9px] font-mono uppercase tracking-wider leading-none">{item.label}</span>
              </div>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
