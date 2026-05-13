import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { UseQueryOptions } from "@tanstack/react-query";

const BASE = import.meta.env.BASE_URL?.replace(/\/$/, "") || "";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${BASE}/api${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `HTTP ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

// ─── Keys ────────────────────────────────────────────────────────────────────

export const getGetAiProfileQueryKey = () => ["/api/ai/profile"] as const;
export const getGetAiStatsQueryKey = () => ["/api/ai/stats"] as const;
export const getListSkillsQueryKey = (params?: { category?: string; status?: string }) =>
  params ? ["/api/skills", params] as const : ["/api/skills"] as const;
export const getListSkillCategoriesQueryKey = () => ["/api/skills/categories"] as const;
export const getListConversationsQueryKey = () => ["/api/ai/conversations"] as const;
export const getGetConversationMessagesQueryKey = (id: number) =>
  ["/api/ai/conversations", id, "messages"] as const;

// ─── Profile ─────────────────────────────────────────────────────────────────

export interface AiProfile {
  id: number;
  name: string;
  aiClass: string;
  level: number;
  xp: number;
  xpToNext: number;
  description: string;
  personality: string;
  avatar?: string | null;
  createdAt: string;
  updatedAt: string;
}

export function useGetAiProfile() {
  return useQuery<AiProfile>({
    queryKey: getGetAiProfileQueryKey(),
    queryFn: () => apiFetch<AiProfile>("/ai/profile"),
  });
}

export function useUpdateAiProfile() {
  const qc = useQueryClient();
  return useMutation<AiProfile, Error, { data: Partial<AiProfile> }>({
    mutationFn: ({ data }) =>
      apiFetch<AiProfile>("/ai/profile", { method: "PATCH", body: JSON.stringify(data) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: getGetAiProfileQueryKey() });
    },
  });
}

// ─── Stats ───────────────────────────────────────────────────────────────────

export interface AiStats {
  totalSkills: number;
  acquiredSkills: number;
  pendingSkills: number;
  fusedSkills: number;
  totalXp: number;
  level: number;
  recentActivity: string[];
}

export function useGetAiStats() {
  return useQuery<AiStats>({
    queryKey: getGetAiStatsQueryKey(),
    queryFn: () => apiFetch<AiStats>("/ai/stats"),
  });
}

// ─── Skills (Nexus) ───────────────────────────────────────────────────────────

export interface NexusSkill {
  id: number;
  name: string;
  category: string;
  description: string;
  level: number;
  status: "pending" | "acquired" | "fused";
  xpValue: number;
  icon: string;
  color: string;
  principles: string[];
  studySource?: string | null;
  parentSkillIds?: number[] | null;
  createdAt: string;
}

export interface SkillCategory {
  name: string;
  count: number;
  icon: string;
  color: string;
}

export function useListNexusSkills(params?: { category?: string; status?: string }) {
  return useQuery<NexusSkill[]>({
    queryKey: getListSkillsQueryKey(params),
    queryFn: () => {
      const qs = new URLSearchParams();
      if (params?.category) qs.set("category", params.category);
      if (params?.status) qs.set("status", params.status);
      const q = qs.toString();
      return apiFetch<NexusSkill[]>(`/skills${q ? `?${q}` : ""}`);
    },
  });
}

export function useListSkillCategories() {
  return useQuery<SkillCategory[]>({
    queryKey: getListSkillCategoriesQueryKey(),
    queryFn: () => apiFetch<SkillCategory[]>("/skills/categories"),
  });
}

export function useAcquireSkill() {
  const qc = useQueryClient();
  return useMutation<NexusSkill, Error, { id: number }>({
    mutationFn: ({ id }) => apiFetch<NexusSkill>(`/skills/${id}/acquire`, { method: "POST" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/api/skills"] });
      qc.invalidateQueries({ queryKey: getGetAiProfileQueryKey() });
      qc.invalidateQueries({ queryKey: getGetAiStatsQueryKey() });
    },
  });
}

export function useDeleteNexusSkill() {
  const qc = useQueryClient();
  return useMutation<void, Error, { id: number }>({
    mutationFn: ({ id }) => apiFetch<void>(`/skills/${id}`, { method: "DELETE" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/api/skills"] });
      qc.invalidateQueries({ queryKey: getGetAiStatsQueryKey() });
    },
  });
}

export function useStudyTopic() {
  return useMutation<{ summary: string; proposedSkills: NexusSkill[] }, Error, { data: { topic: string; filter?: string | null } }>({
    mutationFn: ({ data }) =>
      apiFetch<{ summary: string; proposedSkills: NexusSkill[] }>("/skills/study", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  });
}

export function useFuseSkills() {
  return useMutation<{ fusedSkill: NexusSkill; description: string }, Error, { data: { skillIds: number[]; fusionName?: string | null } }>({
    mutationFn: ({ data }) =>
      apiFetch<{ fusedSkill: NexusSkill; description: string }>("/skills/fuse", {
        method: "POST",
        body: JSON.stringify(data),
      }),
  });
}

// ─── Conversations ────────────────────────────────────────────────────────────

export interface Conversation {
  id: number;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface ConversationMessage {
  id: number;
  conversationId: number;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export function useListConversations() {
  return useQuery<Conversation[]>({
    queryKey: getListConversationsQueryKey(),
    queryFn: () => apiFetch<Conversation[]>("/ai/conversations"),
  });
}

export function useCreateConversation() {
  const qc = useQueryClient();
  return useMutation<Conversation, Error, { data: { title: string } }>({
    mutationFn: ({ data }) =>
      apiFetch<Conversation>("/ai/conversations", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: getListConversationsQueryKey() });
    },
  });
}

export function useGetConversationMessages(id: number, options?: { query?: UseQueryOptions<ConversationMessage[]> }) {
  return useQuery<ConversationMessage[]>({
    queryKey: getGetConversationMessagesQueryKey(id),
    queryFn: () => apiFetch<ConversationMessage[]>(`/ai/conversations/${id}/messages`),
    enabled: !!id,
    ...options?.query,
  });
}

// ─── CAOS Status Unificado ────────────────────────────────────────────────────

export interface CaosSubsystemStats {
  [key: string]: number;
}

export interface CaosSubsystem {
  label: string;
  status: "online" | "offline" | "degraded";
  stats: CaosSubsystemStats;
}

export interface CaosStatusResponse {
  caos: {
    version: string;
    timestamp: string;
    status: string;
  };
  subsystems: {
    "caos-nexus": CaosSubsystem;
    "caos-studio": CaosSubsystem;
    "caos-shell": CaosSubsystem;
  };
}

export const getCaosStatusQueryKey = () => ["/api/caos/status"] as const;

export function useCaosStatus() {
  return useQuery<CaosStatusResponse>({
    queryKey: getCaosStatusQueryKey(),
    queryFn: () => apiFetch<CaosStatusResponse>("/caos/status"),
    refetchInterval: 30_000,
    staleTime: 15_000,
  });
}
