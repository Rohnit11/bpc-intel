-- bpc-intel chatbot: question log (Neon Postgres)
-- Apply once against your Neon database:
--   psql "$DATABASE_URL" -f web/db/schema.sql
-- or paste into the Neon SQL editor.

CREATE TABLE IF NOT EXISTS chat_questions (
  id                  BIGSERIAL PRIMARY KEY,
  question            TEXT        NOT NULL,
  asked_at            TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- false => the corpus could not answer it; this is the harvest signal.
  answered            BOOLEAN     NOT NULL,
  refusal_reason      TEXT,

  -- Retrieval diagnostics: distinguishes "no data exists" (0 hits) from
  -- "data exists but the model still refused" (hits > 0), which are
  -- different problems — a research gap vs a retrieval/prompt gap.
  retrieved_facts     INTEGER     NOT NULL DEFAULT 0,
  retrieved_passages  INTEGER     NOT NULL DEFAULT 0,

  answer_preview      TEXT,

  -- open | researched | wont_fix
  status              TEXT        NOT NULL DEFAULT 'open',
  resolved_at         TIMESTAMPTZ,
  resolution_ref      TEXT
);

CREATE INDEX IF NOT EXISTS chat_questions_open_idx
  ON chat_questions (answered, status, asked_at);

CREATE INDEX IF NOT EXISTS chat_questions_asked_idx
  ON chat_questions (asked_at DESC);
