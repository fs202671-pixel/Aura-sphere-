import { pgTable, text, serial, integer, timestamp, json } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

// ─── ITEMS ────────────────────────────────────────────────────────
export const hubItems = pgTable("caos_hub_items", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  type: text("type").notNull(), // design | theme | agent | skill | project | component
  rarity: text("rarity").notNull().default("Common"), // Common | Rare | Epic | Legendary
  tags: json("tags").$type<string[]>().notNull().default([]),
  previewUrl: text("preview_url"),
  description: text("description"),
  metadata: json("metadata").$type<Record<string, unknown>>(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertHubItemSchema = createInsertSchema(hubItems).omit({ id: true, createdAt: true });
export type InsertHubItem = z.infer<typeof insertHubItemSchema>;
export type HubItem = typeof hubItems.$inferSelect;

// ─── THEMES ───────────────────────────────────────────────────────
export const hubThemes = pgTable("caos_hub_themes", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  rarity: text("rarity").notNull().default("Common"),
  colors: json("colors").$type<string[]>().notNull().default([]),
  fonts: json("fonts").$type<string[]>().notNull().default([]),
  layoutStyle: text("layout_style").notNull().default("grid"),
  spacing: text("spacing"),
  borderRadius: text("border_radius"),
  previewUrl: text("preview_url"),
  sourceImageUrl: text("source_image_url"),
  tags: json("tags").$type<string[]>().notNull().default([]),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertHubThemeSchema = createInsertSchema(hubThemes).omit({ id: true, createdAt: true });
export type InsertHubTheme = z.infer<typeof insertHubThemeSchema>;
export type HubTheme = typeof hubThemes.$inferSelect;

// ─── AGENTS ───────────────────────────────────────────────────────
export const hubAgents = pgTable("caos_hub_agents", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  behavior: text("behavior").notNull(),
  rarity: text("rarity").notNull().default("Common"),
  promptBase: text("prompt_base").notNull().default(""),
  description: text("description"),
  avatar: text("avatar"),
  pluggedSkillIds: json("plugged_skill_ids").$type<number[]>().notNull().default([]),
  runCount: integer("run_count").notNull().default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertHubAgentSchema = createInsertSchema(hubAgents).omit({ id: true, createdAt: true });
export type InsertHubAgent = z.infer<typeof insertHubAgentSchema>;
export type HubAgent = typeof hubAgents.$inferSelect;

// ─── SKILLS ───────────────────────────────────────────────────────
export const hubSkills = pgTable("caos_hub_skills", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  category: text("category").notNull(),
  description: text("description").notNull(),
  rarity: text("rarity").notNull().default("Common"),
  icon: text("icon"),
  behavior: text("behavior"),
  pluggedCount: integer("plugged_count").notNull().default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertHubSkillSchema = createInsertSchema(hubSkills).omit({ id: true, createdAt: true });
export type InsertHubSkill = z.infer<typeof insertHubSkillSchema>;
export type HubSkill = typeof hubSkills.$inferSelect;

// ─── PROJECTS ─────────────────────────────────────────────────────
export const hubProjects = pgTable("caos_hub_projects", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description"),
  rarity: text("rarity").notNull().default("Common"),
  status: text("status").notNull().default("draft"), // draft | building | complete | archived
  themeId: integer("theme_id"),
  agentIds: json("agent_ids").$type<number[]>().notNull().default([]),
  skillIds: json("skill_ids").$type<number[]>().notNull().default([]),
  previewUrl: text("preview_url"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertHubProjectSchema = createInsertSchema(hubProjects).omit({ id: true, createdAt: true });
export type InsertHubProject = z.infer<typeof insertHubProjectSchema>;
export type HubProject = typeof hubProjects.$inferSelect;
