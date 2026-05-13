import { pgTable, text, serial, integer, timestamp, json, boolean } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const caosAuditLog = pgTable("caos_audit_log", {
  id: serial("id").primaryKey(),
  action: text("action").notNull(),
  ip: text("ip").notNull().default("unknown"),
  userId: text("user_id"),
  route: text("route"),
  method: text("method"),
  severity: text("severity").notNull().default("low"),
  pattern: text("pattern"),
  details: json("details").$type<Record<string, unknown>>(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertCaosAuditLogSchema = createInsertSchema(caosAuditLog).omit({ id: true, createdAt: true });
export type InsertCaosAuditLog = z.infer<typeof insertCaosAuditLogSchema>;
export type CaosAuditLog = typeof caosAuditLog.$inferSelect;

export const caosSecurityIssues = pgTable("caos_security_issues", {
  id: serial("id").primaryKey(),
  type: text("type").notNull().default("info"),
  title: text("title").notNull(),
  description: text("description").notNull(),
  severity: text("severity").notNull().default("low"),
  ip: text("ip"),
  pattern: text("pattern"),
  resolved: boolean("resolved").notNull().default(false),
  resolvedAt: timestamp("resolved_at"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertCaosSecurityIssueSchema = createInsertSchema(caosSecurityIssues).omit({ id: true, createdAt: true });
export type InsertCaosSecurityIssue = z.infer<typeof insertCaosSecurityIssueSchema>;
export type CaosSecurityIssue = typeof caosSecurityIssues.$inferSelect;

export const caosMemory = pgTable("caos_memory", {
  id: serial("id").primaryKey(),
  userId: text("user_id"),
  key: text("key").notNull(),
  content: text("content").notNull(),
  tags: json("tags").$type<string[]>().notNull().default([]),
  source: text("source").notNull().default("manual"),
  importance: integer("importance").notNull().default(1),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertCaosMemorySchema = createInsertSchema(caosMemory).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertCaosMemory = z.infer<typeof insertCaosMemorySchema>;
export type CaosMemory = typeof caosMemory.$inferSelect;

export const caosApiCosts = pgTable("caos_api_costs", {
  id: serial("id").primaryKey(),
  provider: text("provider").notNull().default("openai"),
  model: text("model").notNull(),
  inputTokens: integer("input_tokens").notNull().default(0),
  outputTokens: integer("output_tokens").notNull().default(0),
  costUsd: text("cost_usd").notNull().default("0.00"),
  route: text("route"),
  userId: text("user_id"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertCaosApiCostSchema = createInsertSchema(caosApiCosts).omit({ id: true, createdAt: true });
export type InsertCaosApiCost = z.infer<typeof insertCaosApiCostSchema>;
export type CaosApiCost = typeof caosApiCosts.$inferSelect;
