"use client";

import { useRef, useState } from "react";
import { Send, ShieldCheck, Loader2 } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  error?: boolean;
}

const STARTERS = [
  "How big is India's sunscreen market, and how confident is that figure?",
  "Which segment should we enter first, and why?",
  "What does the data say about K-beauty dermocosmetics in India?",
  "What are the CDSCO requirements for importing cosmetics into India?",
  "Compare Korea and India men's grooming.",
];

export function ChatPanel() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  function scrollToBottom() {
    requestAnimationFrame(() => {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    });
  }

  async function ask(question: string) {
    const q = question.trim();
    if (!q || busy) return;

    setInput("");
    setBusy(true);
    setMessages((m) => [...m, { role: "user", content: q }, { role: "assistant", content: "" }]);
    scrollToBottom();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        const { error } = await res.json().catch(() => ({ error: "Request failed." }));
        setMessages((m) => {
          const next = [...m];
          next[next.length - 1] = { role: "assistant", content: error, error: true };
          return next;
        });
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) return;
      const decoder = new TextDecoder();
      let acc = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        setMessages((m) => {
          const next = [...m];
          next[next.length - 1] = { role: "assistant", content: acc };
          return next;
        });
        scrollToBottom();
      }
    } catch {
      setMessages((m) => {
        const next = [...m];
        next[next.length - 1] = {
          role: "assistant",
          content: "Network error — the assistant could not be reached.",
          error: true,
        };
        return next;
      });
    } finally {
      setBusy(false);
      scrollToBottom();
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-16rem)] min-h-[28rem]">
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-4 pr-1"
        aria-live="polite"
      >
        {messages.length === 0 && (
          <div className="space-y-4">
            <div className="rounded-xl border border-dashed border-[var(--series-2)]/50 bg-[color-mix(in_oklab,var(--series-2)_6%,var(--surface-1))] p-4">
              <div className="flex items-center gap-2 text-sm font-semibold mb-1">
                <ShieldCheck className="h-4 w-4 text-[var(--series-2)]" aria-hidden />
                Grounded in this repository only
              </div>
              <p className="text-sm text-[var(--text-secondary)]">
                Every figure comes from the sourced DataPoints in this system, quoted with its
                period, value basis, confidence and source. If the data doesn&apos;t cover your
                question, the assistant will say so and log it as a research gap —{" "}
                <span className="font-medium text-[var(--text-primary)]">it will not guess</span>.
              </p>
            </div>
            <div>
              <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-2">
                Try
              </div>
              <div className="flex flex-col gap-1.5 items-start">
                {STARTERS.map((s) => (
                  <button
                    key={s}
                    onClick={() => ask(s)}
                    className="text-left text-sm text-[var(--series-1)] hover:underline"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div
            key={i}
            className={
              m.role === "user"
                ? "ml-auto max-w-[85%] rounded-xl bg-[var(--text-primary)] text-[var(--page-plane)] px-4 py-2.5 text-sm"
                : `max-w-[95%] rounded-xl border px-4 py-3 text-sm whitespace-pre-wrap ${
                    m.error
                      ? "border-[var(--status-critical)] bg-[color-mix(in_oklab,var(--status-critical)_8%,var(--surface-1))]"
                      : "border-[var(--border)] bg-[var(--surface-1)]"
                  }`
            }
          >
            {m.content ||
              (busy && i === messages.length - 1 ? (
                <span className="inline-flex items-center gap-2 text-[var(--text-muted)]">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden />
                  Searching the repository…
                </span>
              ) : null)}
          </div>
        ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        className="mt-4 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about market size, competitors, entry routes, regulation…"
          disabled={busy}
          className="flex-1 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-sm disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--text-primary)] px-4 py-2 text-sm font-medium text-[var(--page-plane)] disabled:opacity-40"
        >
          <Send className="h-4 w-4" aria-hidden />
          Ask
        </button>
      </form>
    </div>
  );
}
