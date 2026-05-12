# Aura Sphere

A personal AI assistant web app with local-first data, voice interaction, and a 3D particle sphere UI.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 8080)
- `pnpm --filter @workspace/aura-sphere run dev` — run the frontend (port assigned by workflow)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- Frontend: React 19.1.7 + Vite 7 + Tailwind CSS v3 + shadcn/ui
- API: Express 5 (artifacts/api-server)
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- Build: esbuild (server), Vite (frontend)

## Where things live

- `artifacts/aura-sphere/` — frontend React app
- `artifacts/api-server/` — Express API backend
- `lib/db/src/schema/aura-sphere.ts` — DB schema (profiles + chat_messages tables)
- `artifacts/aura-sphere/src/integrations/supabase/client.ts` — Supabase stub (no-op)
- `artifacts/aura-sphere/src/lib/api.ts` — API base URL helper (points to /api)
- `artifacts/aura-sphere/src/index.css` — theme CSS variables (monochrome dark theme)

## Architecture decisions

- Supabase replaced with Replit PostgreSQL + Express API backend.
- **Auth: intentionally local-only** (localStorage via `useLocalAuth`). The user explicitly
  requested NO Clerk, NO Supabase, NO Lovable connections. Clerk was also tested and found
  to crash the app (blank screen) with React 19.1.7 + Vite 7 due to incompatibility.
  A local user is auto-created on first visit — no login screen required.
- Supabase stub (`client.ts`) keeps all import sites working without rewriting every call site.
- App is primarily local-first: data stored in localStorage, sync to backend is optional.
- Chat.tsx and useSyncService use `/api/chat-messages` and `/api/profiles` endpoints.

## Product

- Personal AI assistant with a 3D animated particle sphere
- Multiple AI modes (Chat, Código, Projetos, Memória, Imagem, Voz, Automação, Dev Mode)
- Voice input/output support (Web Speech API)
- Local-first: works offline, syncs when online
- Portuguese (Brazilian) UI

## User preferences

- **NO entry/login screen** — app goes directly into the AI chat on load.
- **NO Clerk, Supabase, or Lovable** — local-only auth via localStorage.
- **Minimal loading** — no artificial delays or splash screens.
- Particle sphere: particles should move individually in/out of sphere boundaries.

## Gotchas

- Tailwind v3 (not v4) — uses `@tailwind base/components/utilities` in index.css and postcss.config.js
- App uses react-router-dom (not wouter) for routing
- Vite config drops `@tailwindcss/vite` plugin — uses postcss instead for Tailwind v3 compatibility
- `@capacitor/core` removed — stubbed out in platform.ts for web-only build
- `@supabase/supabase-js` and `@lovable.dev/cloud-auth-js` not installed — stubbed
- `@clerk/react` removed — incompatible with React 19.1.7 + Vite 7 (causes blank screen crash)
- useLocalAuth uses lazy useState init to read localStorage synchronously (no flash on returning visits)
- All functions returned from useLocalAuth are wrapped in useCallback to prevent infinite re-render
  loops in hooks like useOfflineChat that include them in useEffect dependency arrays

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
