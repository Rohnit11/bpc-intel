import { neon } from "@neondatabase/serverless";

/**
 * Question log — the input to the knowledge-gap loop.
 *
 * EVERY question is logged with whether the corpus could answer it. The
 * unanswered ones are harvested weekly (see .github/workflows/harvest-questions.yml)
 * and fed into the governed research pipeline, so the assistant's blind spots
 * become the research backlog rather than silent failures.
 *
 * Logging is best-effort by design: a database outage must never break the
 * chat, and DATABASE_URL being unset simply disables the loop.
 */

export interface QuestionLog {
  question: string;
  answered: boolean;
  retrievedFacts: number;
  retrievedPassages: number;
  answerPreview?: string | null;
  refusalReason?: string | null;
}

export function isDbConfigured(): boolean {
  return Boolean(process.env.DATABASE_URL);
}

export async function logQuestion(entry: QuestionLog): Promise<void> {
  const url = process.env.DATABASE_URL;
  if (!url) return; // Loop disabled — not an error.
  try {
    const sql = neon(url);
    await sql`
      INSERT INTO chat_questions
        (question, answered, retrieved_facts, retrieved_passages, answer_preview, refusal_reason)
      VALUES (
        ${entry.question},
        ${entry.answered},
        ${entry.retrievedFacts},
        ${entry.retrievedPassages},
        ${entry.answerPreview ?? null},
        ${entry.refusalReason ?? null}
      )`;
  } catch (err) {
    // Never surface a logging failure to the user mid-conversation.
    console.error("[questions-db] log failed:", err);
  }
}

export interface OpenQuestion {
  id: number;
  question: string;
  asked_at: string;
  retrieved_facts: number;
  retrieved_passages: number;
  refusal_reason: string | null;
}

/** Unanswered, still-open questions for the weekly harvest. */
export async function fetchOpenGaps(limit = 200): Promise<OpenQuestion[]> {
  const url = process.env.DATABASE_URL;
  if (!url) return [];
  const sql = neon(url);
  const rows = await sql`
    SELECT id, question, asked_at, retrieved_facts, retrieved_passages, refusal_reason
    FROM chat_questions
    WHERE answered = false AND status = 'open'
    ORDER BY asked_at ASC
    LIMIT ${limit}`;
  return rows as OpenQuestion[];
}

export async function markResolved(ids: number[], ref: string): Promise<void> {
  const url = process.env.DATABASE_URL;
  if (!url || ids.length === 0) return;
  const sql = neon(url);
  await sql`
    UPDATE chat_questions
    SET status = 'researched', resolved_at = now(), resolution_ref = ${ref}
    WHERE id = ANY(${ids})`;
}
