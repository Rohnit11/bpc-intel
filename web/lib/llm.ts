/**
 * Provider-agnostic chat completion, streamed.
 *
 * Deliberately dependency-free (plain fetch) so the provider is a one-env-var
 * decision rather than an architectural commitment:
 *
 *   CHAT_PROVIDER = xai | google | anthropic   (default: xai)
 *   CHAT_API_KEY  = <key>
 *   CHAT_MODEL    = <optional model id override>
 *
 * NOTE ON xAI FREE CREDITS: xAI's free monthly credits are reported to come
 * via a data-sharing programme, under which API traffic may be used for model
 * training. This repo's context includes licensed Euromonitor/Statista-derived
 * figures (which /methodology commits to not redistributing) and unpublished
 * strategy. If you use xAI, keep data sharing DISABLED and pay per token —
 * this corpus is small, so the cost is minimal.
 */

export type Provider = "xai" | "google" | "anthropic";

interface ProviderConfig {
  url: string;
  model: string;
  /** Anthropic uses its own message schema; the others are OpenAI-compatible. */
  style: "openai" | "anthropic";
  headers: (key: string) => Record<string, string>;
}

const PROVIDERS: Record<Provider, ProviderConfig> = {
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
  grok: "xai", "x.ai": "xai", x: "xai",
  gemini: "google", googleai: "google",
  claude: "anthropic",
};

export function activeProvider(): Provider {
  const raw = (process.env.CHAT_PROVIDER ?? "xai").trim().toLowerCase();
  const p = PROVIDER_ALIASES[raw] ?? raw;
  if (p in PROVIDERS) return p as Provider;
  throw new Error(`Unknown CHAT_PROVIDER "${raw}" (expected xai | google | anthropic)`);
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
