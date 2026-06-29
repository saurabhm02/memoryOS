/** Per-concept practice prompts. Client-side because the API takes (concept, score)
 * directly — scoring is the learner's self-assessment (an honest fit until a server-side
 * LLM scorer exists). One focused, realistic system-design question per concept. */
export interface Question {
  id: string;
  text: string;
}

export const QUESTION_BANK: Record<string, Question> = {
  Caching: {
    id: "cach-1",
    text: "Walk through cache invalidation for a read-heavy service. When would you pick write-through over write-back, and how do you prevent a cache stampede?",
  },
  "Database Round Trips": {
    id: "dbrt-1",
    text: "A request fans out into dozens of small queries (an N+1). How do you cut the round trips, and what are the trade-offs of batching vs. denormalizing?",
  },
  "Distributed Transactions": {
    id: "dtx-1",
    text: "Compare two-phase commit with a saga for a multi-service checkout. How does each behave when one participant fails mid-way?",
  },
  Sharding: {
    id: "shard-1",
    text: "How do you choose a shard key? Describe a key that causes hotspots and how you'd reshard without downtime.",
  },
  Replication: {
    id: "repl-1",
    text: "Synchronous vs. asynchronous replication: what does each cost you, and how do you guarantee read-your-writes when reads hit a replica?",
  },
  "Consistency Models": {
    id: "cons-1",
    text: "Explain read-your-writes vs. eventual consistency, and name a concrete scenario where each one breaks under failover.",
  },
  Indexing: {
    id: "idx-1",
    text: "When does adding an index hurt? Explain composite-index column order and when a covering index pays off.",
  },
  Partitioning: {
    id: "part-1",
    text: "Range vs. hash partitioning: what query patterns favor each, and what goes wrong when the data is skewed?",
  },
  "Concurrency Control": {
    id: "cc-1",
    text: "Optimistic vs. pessimistic locking for a seat-booking flow. Which do you choose under high contention, and why?",
  },
  "CAP Theorem": {
    id: "cap-1",
    text: "During a network partition, what does your system give up and why? Make it concrete for a specific feature.",
  },
  "Data Modeling": {
    id: "dm-1",
    text: "Design the data model for a social feed. How do access patterns drive your choice to normalize or denormalize?",
  },
  "Load Balancing": {
    id: "lb-1",
    text: "L4 vs. L7 load balancing: when do you need L7, and what does relying on sticky sessions cost you?",
  },
  "Message Queues": {
    id: "mq-1",
    text: "Your consumer gets at-least-once delivery. What does that force you to handle, and how do you preserve ordering where it matters?",
  },
  "Rate Limiting": {
    id: "rl-1",
    text: "Token bucket vs. sliding window. How do you rate-limit correctly across a fleet of stateless servers?",
  },
  Idempotency: {
    id: "idem-1",
    text: "Design an idempotent payment endpoint. Where does the idempotency key live, and how long do you retain it?",
  },
};

/** Curated order — the convergent trio first, so the root-cause pattern surfaces early. */
export const SESSION_ORDER: string[] = [
  "Caching",
  "Database Round Trips",
  "Distributed Transactions",
  "Sharding",
  "Indexing",
  "Load Balancing",
  "Replication",
  "Message Queues",
  "Rate Limiting",
  "Partitioning",
  "Concurrency Control",
  "Data Modeling",
  "CAP Theorem",
  "Consistency Models",
];

export function getQuestion(concept: string): string {
  return (
    QUESTION_BANK[concept]?.text ??
    `Explain ${concept} and describe a real scenario where it determines your design.`
  );
}
