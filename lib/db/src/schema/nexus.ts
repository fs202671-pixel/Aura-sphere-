import { pgTable, text, serial, integer, timestamp, json } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const aiProfiles = pgTable("ai_profiles", {
  id: serial("id").primaryKey(),
  name: text("name").notNull().default("NEXUS"),
  level: integer("level").notNull().default(1),
  xp: integer("xp").notNull().default(0),
  xpToNext: integer("xp_to_next").notNull().default(100),
  aiClass: text("ai_class").notNull().default("Iniciante"),
  description: text("description").notNull().default("Uma IA recém-nascida, ansiosa para aprender e evoluir."),
  personality: text("personality").notNull().default("Curioso, analítico e sempre disposto a aprender."),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertAiProfileSchema = createInsertSchema(aiProfiles).omit({ id: true, createdAt: true });
export type InsertAiProfile = z.infer<typeof insertAiProfileSchema>;
export type AiProfile = typeof aiProfiles.$inferSelect;

export const nexusSkills = pgTable("nexus_skills", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  category: text("category").notNull(),
  description: text("description").notNull(),
  level: integer("level").notNull().default(1),
  status: text("status").notNull().default("pending"),
  xpValue: integer("xp_value").notNull().default(50),
  icon: text("icon").notNull().default("Zap"),
  color: text("color").notNull().default("#6366f1"),
  principles: json("principles").$type<string[]>().notNull().default([]),
  parentSkillIds: json("parent_skill_ids").$type<number[] | null>().default(null),
  studySource: text("study_source"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertNexusSkillSchema = createInsertSchema(nexusSkills).omit({ id: true, createdAt: true });
export type InsertNexusSkill = z.infer<typeof insertNexusSkillSchema>;
export type NexusSkill = typeof nexusSkills.$inferSelect;

export const nexusConversations = pgTable("nexus_conversations", {
  id: serial("id").primaryKey(),
  title: text("title").notNull().default("Nova Conversa"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertNexusConversationSchema = createInsertSchema(nexusConversations).omit({ id: true, createdAt: true, updatedAt: true });
export type InsertNexusConversation = z.infer<typeof insertNexusConversationSchema>;
export type NexusConversation = typeof nexusConversations.$inferSelect;

export const nexusMessages = pgTable("nexus_messages", {
  id: serial("id").primaryKey(),
  conversationId: integer("conversation_id").notNull().references(() => nexusConversations.id),
  role: text("role").notNull(),
  content: text("content").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertNexusMessageSchema = createInsertSchema(nexusMessages).omit({ id: true, createdAt: true });
export type InsertNexusMessage = z.infer<typeof insertNexusMessageSchema>;
export type NexusMessage = typeof nexusMessages.$inferSelect;

export const nexusActivityLog = pgTable("nexus_activity_log", {
  id: serial("id").primaryKey(),
  action: text("action").notNull(),
  details: text("details"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertNexusActivityLogSchema = createInsertSchema(nexusActivityLog).omit({ id: true, createdAt: true });
export type InsertNexusActivityLog = z.infer<typeof insertNexusActivityLogSchema>;
export type NexusActivityLog = typeof nexusActivityLog.$inferSelect;
