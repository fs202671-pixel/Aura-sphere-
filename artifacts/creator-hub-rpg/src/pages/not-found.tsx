import { Link } from "wouter";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 text-center gap-6">
      <div className="space-y-2">
        <p className="text-6xl font-bold font-mono text-primary/30">404</p>
        <h1 className="text-2xl font-bold font-mono uppercase tracking-widest">Setor Não Encontrado</h1>
        <p className="text-muted-foreground text-sm">Esta zona do CAOS não existe ou foi corrompida.</p>
      </div>
      <Link href="/">
        <Button className="font-mono uppercase tracking-wider">Retornar à Central</Button>
      </Link>
    </div>
  );
}
