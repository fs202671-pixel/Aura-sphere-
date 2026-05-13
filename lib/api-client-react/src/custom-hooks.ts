import { useMutation, useQueryClient } from "@tanstack/react-query";
import { customFetch } from "./custom-fetch";
import type { Item } from "./generated/api.schemas";

// ── Fusão de Artefatos ─────────────────────────────────────────────────────

export interface FusaoRequest {
  itemAId: number;
  itemBId: number;
}

export type FusaoResult = Item;

export const fusaoArtefatos = async (body: FusaoRequest): Promise<FusaoResult> =>
  customFetch<FusaoResult>("/api/items/fusao", {
    method: "POST",
    body: JSON.stringify(body),
  });

export const useFusaoArtefatos = () => {
  const qc = useQueryClient();
  return useMutation<FusaoResult, Error, FusaoRequest>({
    mutationFn: fusaoArtefatos,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/api/items"] });
    },
  });
};

// ── Status dos Lobos (segurança) ───────────────────────────────────────────

export interface LobosBlockedIp {
  ip: string;
  blockUntil: number;
  offenses: number;
  retryInSec: number;
}

export interface LobosStatus {
  blockedIps: LobosBlockedIp[];
  trackedIps: number;
  trackedUsers: number;
}

export const getLobosStatus = async (): Promise<LobosStatus> =>
  customFetch<LobosStatus>("/api/security/lobos/status");
