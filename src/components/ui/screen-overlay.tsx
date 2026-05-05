import * as React from "react";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";
import { getPlatform, isMobilePlatform } from "@/lib/platform";

export interface ScreenOverlayProps {
  title: string;
  description: string;
  visible: boolean;
  onClose: () => void;
  children?: React.ReactNode;
}

export function ScreenOverlay({
  title,
  description,
  visible,
  onClose,
  children,
}: ScreenOverlayProps) {
  if (!visible) {
    return null;
  }

  const platform = getPlatform();

  return (
    <div
      className={cn(
        "fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-4 text-slate-100",
        isMobilePlatform() ? "touch-none" : "",
      )}
    >
      <div className="relative w-full max-w-3xl rounded-[2rem] border border-white/10 bg-slate-950/95 p-6 shadow-2xl backdrop-blur-xl sm:p-8">
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-full border border-white/10 bg-slate-900/90 text-white transition hover:bg-slate-800"
          aria-label="Fechar sobreposição"
        >
          <X className="h-5 w-5" />
        </button>

        <div className="space-y-4">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Sobreposição de tela</p>
            <h2 className="text-2xl font-semibold text-white">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">{description}</p>
          </div>

          <div className="rounded-3xl border border-white/10 bg-slate-900/80 p-4 text-sm text-slate-300">
            <p className="font-medium text-white">Plataforma detectada:</p>
            <p>{platform}</p>
            <p className="mt-3 text-sm text-slate-400">
              Este modo de sobreposição permite exibir informações e controles rápidos sem sair da tela principal.
            </p>
          </div>

          {children}

          <div className="grid gap-3 sm:grid-cols-2">
            <button
              type="button"
              onClick={onClose}
              className="inline-flex items-center justify-center rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-100"
            >
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
