import { ReactNode } from "react";
import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import { Home, Library, Palette, Bot, Sparkles, FolderGit2 } from "lucide-react";

export function AppLayout({ children }: { children: ReactNode }) {
  const [location] = useLocation();

  const navItems = [
    { href: "/", label: "Hub", icon: Home },
    { href: "/library", label: "Library", icon: Library },
    { href: "/themes", label: "Themes", icon: Palette },
    { href: "/agents", label: "Agents", icon: Bot },
    { href: "/skills", label: "Skills", icon: Sparkles },
    { href: "/projects", label: "Projects", icon: FolderGit2 },
  ];

  return (
    <div className="flex h-screen w-full bg-background text-foreground grid-bg overflow-hidden font-sans">
      <aside className="w-64 border-r border-border bg-card/50 backdrop-blur-md flex flex-col relative z-20">
        <div className="p-6 border-b border-border">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60 uppercase tracking-widest font-mono">
            Creator Hub
          </h1>
          <p className="text-xs text-muted-foreground font-mono mt-1">RPG STUDIO</p>
        </div>
        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          {navItems.map((item) => {
            const isActive = location === item.href || (item.href !== "/" && location.startsWith(item.href));
            return (
              <Link key={item.href} href={item.href}>
                <div
                  className={cn(
                    "flex items-center gap-3 px-4 py-3 rounded-md cursor-pointer transition-all duration-200 border",
                    isActive
                      ? "bg-primary/10 border-primary/30 text-primary shadow-[0_0_15px_rgba(255,255,255,0.05)]"
                      : "border-transparent text-muted-foreground hover:bg-card hover:text-foreground hover:border-border"
                  )}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium tracking-wide">{item.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-3 px-4 py-2 bg-black/40 rounded-md border border-border/50">
            <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_8px_#22c55e] animate-pulse" />
            <span className="text-xs text-muted-foreground font-mono">System Online</span>
          </div>
        </div>
      </aside>
      <main className="flex-1 h-full overflow-y-auto relative z-10">
        {children}
      </main>
    </div>
  );
}
