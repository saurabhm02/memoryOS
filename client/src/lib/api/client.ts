import axios, { type AxiosRequestConfig } from "axios";

import { authService } from "../auth/AuthService";
import {
  answerAssessmentSchema,
  competencyGraphSchema,
  diagnosisSchema,
  forgetResultSchema,
  memifyDeltaSchema,
  observationResultSchema,
  type Scope,
} from "./schemas";

const baseURL =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

/** Cognee writes (observe/improve) can take ~20–40s; allow generous headroom. */
export const http = axios.create({ baseURL, timeout: 120_000 });

// Identity is the verified bearer token — derived from the session, never a header the
// client sets by hand. getAccessToken() returns a freshly-refreshed token.
http.interceptors.request.use(async (config) => {
  const token = await authService.getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// A 401 means the session is gone or invalid → sign out, which flips the AuthProvider to
// "unauthenticated" and routes the user back to the landing/login screen.
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error?.response?.status === 401) {
      await authService.signOut().catch(() => {});
    }
    return Promise.reject(error);
  },
);

function withScope(scope: Scope, config: AxiosRequestConfig = {}): AxiosRequestConfig {
  // The learner is derived from the token server-side; only the ontology selector
  // travels as a query param.
  return { ...config, params: { domain: scope.domain, ...config.params } };
}

export const api = {
  health: () => http.get("/health").then((r) => r.data as { status: string }),

  me: () =>
    http
      .get("/api/v1/me")
      .then(
        (r) =>
          r.data as { subject: string; email: string | null; tenant_id: string | null },
      ),

  graph: (scope: Scope) =>
    http
      .get("/api/v1/graph", withScope(scope))
      .then((r) => competencyGraphSchema.parse(r.data)),

  diagnosis: (scope: Scope) =>
    http
      .get("/api/v1/diagnosis", withScope(scope))
      .then((r) => diagnosisSchema.parse(r.data)),

  provision: (scope: Scope) =>
    http.post("/api/v1/provision", null, withScope(scope)).then((r) => r.data),

  observe: (scope: Scope, body: { concept: string; score: number }) =>
    http
      .post("/api/v1/observations", body, withScope(scope))
      .then((r) => observationResultSchema.parse(r.data)),

  scoreAnswer: (
    scope: Scope,
    body: { concept: string; question: string; answer: string },
  ) =>
    http
      .post("/api/v1/answers", body, withScope(scope))
      .then((r) => answerAssessmentSchema.parse(r.data)),

  improve: (scope: Scope) =>
    http
      .post("/api/v1/improve", null, withScope(scope))
      .then((r) => memifyDeltaSchema.parse(r.data)),

  forget: (scope: Scope, concept: string) =>
    http
      .post("/api/v1/forget", { concept }, withScope(scope))
      .then((r) => forgetResultSchema.parse(r.data)),
};
