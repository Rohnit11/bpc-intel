/**
 * Provider-agnostic chat completion, streamed.
 *
 * Deliberately dependency-free (plain fetch) so the provider is a one-env-var
 * decision rather than an architectural commitment:
 *
 *   CHAT_PROVIDER = groq | xai | google | anthropic   (default: groq)
 *   CHAT_API_KEY  = <key>
 *   CHAT_MODEL    = <optional model id override>
 *
 * GROQ vs GROK — two different companies, one letter apart:
 *   groq = Groq (api.groq.com), fast inference for open models (Llama etc.),
 *          has a genuinely free tier. This is the default.
 *   xai  = xAI's Grok (api.x.ai).
 * CHAT_PROVIDER="grok" is therefore ambiguous and is REJECTED with a message
 * asking you to spell out which one you meant, rather than silently billing
 * the wrong vendor.
 *
 * NOTE ON xAI FREE CREDITS: xAI's free monthly credits are reported to come
 * via a data-sharing programme, under which API traffic may be used for model
 * training. This repo's context includes licensed Euromonitor/Statista-derived
 * figures (which /methodology commits to not redistributing) and unpublished
 * strategy. If you use xAI, keep data sharing DISABLED and pay per token —
 * this corpus is small, so the cost is minimal.
 */

export type Provider = "groq" | "xai" | "google" | "anthropic";

interface ProviderConfig {
  url: string;
  model: string;
  /** Anthropic uses its own message schema; the others are OpenAI-compatible. */
  style: "openai" | "anthropic";
  headers: (key: string) => Record<string, string>;
}

const PROVIDERS: Record<Provider, ProviderConfig> = {
  groq: {
    url: "https://api.groq.com/openai/v1/chat/completions",
    model: "llama-3.3-70b-versatile",
    style: "openai",
    headers: (key) => ({ Authorization: `Bearer ${key}` }),
  },
  xai: {
    url: "https://api.x.ai/v1/chat/completions",
    model: "grok-4.1-fast",
    style: "openai",
    headers: (key) => ({ Authorization: `Bearer ${key}` }),
  },
  google: {
    url: "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    model: "gemini-2.5-flash",
    style: "openai",
    headers: (key) => ({ Authorization: `Bearer ${key}` }),
  },
  anthropic: {
    url: "https://api.anthropic.com/v1/messages",
    model: "claude-sonnet-4-5",
    style: "anthropic",
    headers: (key) => ({
      "x-api-key": key,
      "anthropic-version": "2023-06-01",
    }),
  },
};

/** Friendly names people actually type, mapped to provider keys. */
const PROVIDER_ALIASES: Record<string, Provider> = {
  "groq.com": "groq", llama: "groq",
  "x.ai": "xai", x: "xai", "grok-xai": "xai", xaigrok: "xai",
  gemini: "google", googleai: "google",
  claude: "anthropic",
};

export function activeProvider(): Provider {
  const raw = (process.env.CHAT_PROVIDER ?? "groq").trim().toLowerCase();
  // "grok" is one letter from "groq" and means a different vendor. Refuse to
  // guess — silently calling (and billing) the wrong provider is worse than
  // a clear error at startup.
  if (raw === "grok") {
    throw new Error(
      'Ambiguous CHAT_PROVIDER "grok": did you mean "groq" (Groq — api.groq.com, ' +
      'free tier, Llama models) or "xai" (xAI\'s Grok — api.x.ai)? Set one of those exactly.',
    );
  }
  const p = PROVIDER_ALIASES[raw] ?? raw;
  if (p in PROVIDERS) return p as Provider;
  throw new Error(`Unknown CHAT_PROVIDER "${raw}" (expected groq | xai | google | anthropic)`);
}

export function isConfigured(): boolean {
  return Boolean(process.env.CHAT_API_KEY);
}

/**
 * Streams the assistant reply as plain text chunks.
 * Throws on auth/transport failure so the route can surface a clean error.
 */
export async function streamCompletion(
  system: string,
  user: string,
  signal?: AbortSignal,
): Promise<ReadableStream<Uint8Array>> {
  const provider = activeProvider();
  const cfg = PROVIDERS[provider];
  const key = process.env.CHAT_API_KEY;
  if (!key) throw new Error("CHAT_API_KEY is not set");
  const model = process.env.CHAT_MODEL || cfg.model;

  const body =
    cfg.style === "anthropic"
      ? {
          model,
          max_tokens: 1500,
          system,
          messages: [{ role: "user", content: user }],
          stream: true,
        }
      : {
          model,
          max_tokens: 1500,
          temperature: 0,
          messages: [
            { role: "system", content: system },
            { role: "user", content: user },
          ],
          stream: true,
        };

  const res = await fetch(cfg.url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...cfg.headers(key) },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok || !res.body) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${provider} request failed (${res.status}): ${detail.slice(0, 300)}`);
  }

  return parseSSE(res.body, cfg.style);
}

/** Converts a provider's SSE stream into a plain-text stream. */
function parseSSE(
  upstream: ReadableStream<Uint8Array>,
  style: "openai" | "anthropic",
): ReadableStream<Uint8Array> {
  const decoder = new TextDecoder();
  const encoder = new TextEncoder();
  let buffer = "";

  return new ReadableStream({
    async start(controller) {
      const reader = upstream.getReader();
      try {
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";
          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data:")) continue;
            const payload = trimmed.slice(5).trim();
            if (!payload || payload === "[DONE]") continue;
            try {
              const json = JSON.parse(payload);
              const text =
                style === "anthropic"
                  ? json.delta?.text ?? ""
                  : json.choices?.[0]?.delta?.content ?? "";
              if (text) controller.enqueue(encoder.encode(text));
            } catch {
              // Partial/keepalive frame — safe to skip.
            }
          }
        }
      } finally {
        reader.releaseLock();
        controller.close();
      }
    },
  });
}
