import { z } from "zod";

/** Runtime schemas for the RecallOS API. Types are inferred from these (single source
 * of truth), and responses are parsed so a contract drift fails loud, not silently. */

export const competencyStateSchema = z.enum(["unvisited", "weak", "medium", "mastered"]);

export const graphNodeSchema = z.object({
  concept: z.string(),
  state: competencyStateSchema,
  score: z.number().nullable(),
});

export const graphEdgeSchema = z.object({
  source: z.string(),
  target: z.string(),
});

export const rootCauseSchema = z.object({
  concept: z.string(),
  resolves: z.array(z.string()),
});

export const competencyGraphSchema = z.object({
  nodes: z.array(graphNodeSchema),
  edges: z.array(graphEdgeSchema),
  root_cause: rootCauseSchema.nullable(),
});

export const diagnosisSchema = z.object({
  weak: z.array(z.string()),
  root_cause: rootCauseSchema.nullable(),
  narration: z.string().nullable(),
});

export const observationResultSchema = z.object({
  concept: z.string(),
  score: z.number(),
  memory_written: z.boolean(),
});

export const memifyDeltaSchema = z.object({
  nodes_before: z.number(),
  nodes_after: z.number(),
  edges_before: z.number(),
  edges_after: z.number(),
  derived_patterns: z.array(z.string()),
});

export const forgetResultSchema = z.object({ forgotten: z.string() });

export const answerAssessmentSchema = z.object({
  concept: z.string(),
  score: z.number(),
  rationale: z.string(),
  demonstrated: z.array(z.string()),
  missed: z.array(z.string()),
  memory_written: z.boolean(),
});

export type CompetencyState = z.infer<typeof competencyStateSchema>;
export type GraphNode = z.infer<typeof graphNodeSchema>;
export type GraphEdge = z.infer<typeof graphEdgeSchema>;
export type RootCause = z.infer<typeof rootCauseSchema>;
export type CompetencyGraph = z.infer<typeof competencyGraphSchema>;
export type Diagnosis = z.infer<typeof diagnosisSchema>;
export type ObservationResult = z.infer<typeof observationResultSchema>;
export type MemifyDelta = z.infer<typeof memifyDeltaSchema>;
export type ForgetResult = z.infer<typeof forgetResultSchema>;
export type AnswerAssessment = z.infer<typeof answerAssessmentSchema>;

/** Identifies the learner + domain for every request (auth stub + ontology selector). */
export interface Scope {
  userId: string;
  domain: string;
}
