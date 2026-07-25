import type { NextRequest } from "next/server";
import { retrieve, formatContext } from "@/lib/retrieval";
import { SYSTEM_PROMPT, buildUserMessage, NO_ANSWER_MARKER } from "@/lib/prompt";
import { streamCompletion, isConfigured, activeProvider } from "@/lib/llm";
import { logQuestion } from "@/lib/questions-db";

export const maxDuration = 60;

const MAX_QUESTION_LENGTH = 1000;

export async function POST(request: NextRequest) {
  let question: string;
  try {
    const body = await request.json();
    question = String(body?.question ?? "").trim();
  } catch {
    return Response.json({ error: "Invalid request body." }, { status: 400 });
  }

  if (!question) {
    return Response.json({ error: "Ask a question first." }, { status: 400 });
  }
  if (question.length > MAX_QUESTION_LENGTH) {
    return Response.json(
      { error: `Question too long (max ${MAX_QUESTION_LENGTH} characters).` },
      { status: 400 },
    );
  }
  if (!isConfigured()) {
    return Response.json(
      {
        error:
          "The assistant is not configured on this deployment — set CHAT_API_KEY (and CHAT_PROVIDER) in the environment.",
      },
      { status: 503 },
    );
  }

  const retrieved = retrieve(question);

  // Nothing matched: refuse deterministically. Cheaper and more reliable than
  // asking the model to refuse over an empty context, and it still logs the gap.
  if (retrieved.empty) {
    await logQuestion({
      question,
      answered: false,
      retrievedFacts: 0,
      retrievedPassages: 0,
      refusalReason: "no_retrieval_match",
    });
    const msg =
      "I don't have anything in this repository that answers that.\n\n" +
      "This system only covers Beauty & Personal Care in South Korea and India, and it only " +
      "answers from figures that have been researched and sourced into it — it will not guess. " +
      "Your question has been logged as a knowledge gap for the next research pass.";
    return new Response(msg, {
      headers: { "Content-Type": "text/plain; charset=utf-8", "X-Answered": "false" },
    });
  }

  const context = formatContext(retrieved);
  const userMessage = buildUserMessage(question, context);

  let upstream: ReadableStream<Uint8Array>;
  try {
    upstream = await streamCompletion(SYSTEM_PROMPT, userMessage, request.signal);
  } catch (err) {
    console.error("[chat] provider error:", err);
    return Response.json(
      { error: `The ${activeProvider()} provider could not be reached. Check CHAT_API_KEY and quota.` },
      { status: 502 },
    );
  }

  // Tee the stream: forward to the client while accumulating for the gap log.
  const decoder = new TextDecoder();
  let full = "";
  const encoder = new TextEncoder();

  const out = new ReadableStream<Uint8Array>({
    async start(controller) {
      const reader = upstream.getReader();
      let sawMarker = false;
      let leading = "";
      let markerResolved = false;
      try {
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          const chunk = decoder.decode(value, { stream: true });
          full += chunk;

          // Strip the refusal marker from what the user sees, while still
          // recording it. Buffer only until we know whether it's present.
          if (!markerResolved) {
            leading += chunk;
            if (leading.length < NO_ANSWER_MARKER.length) continue;
            if (leading.startsWith(NO_ANSWER_MARKER)) {
              sawMarker = true;
              leading = leading.slice(NO_ANSWER_MARKER.length).trimStart();
            }
            markerResolved = true;
            if (leading) controller.enqueue(encoder.encode(leading));
            continue;
          }
          controller.enqueue(encoder.encode(chunk));
        }
        if (!markerResolved && leading) controller.enqueue(encoder.encode(leading));
      } finally {
        reader.releaseLock();
        controller.close();
        const answered = !sawMarker && !full.startsWith(NO_ANSWER_MARKER);
        await logQuestion({
          question,
          answered,
          retrievedFacts: retrieved.facts.length,
          retrievedPassages: retrieved.passages.length,
          answerPreview: full.slice(0, 500),
          refusalReason: answered ? null : "model_refused_insufficient_context",
        });
      }
    },
  });

  return new Response(out, {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
