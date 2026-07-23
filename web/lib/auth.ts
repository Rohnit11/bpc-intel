import { createHmac, timingSafeEqual } from "node:crypto";

export const AUTH_COOKIE = "bpc_auth";
const PAYLOAD = "bpc-intel:authenticated:v1";

function secret(): string {
  const s = process.env.AUTH_SECRET;
  if (!s) throw new Error("AUTH_SECRET env var is not set");
  return s;
}

function sign(payload: string): string {
  return createHmac("sha256", secret()).update(payload).digest("hex");
}

/** The signed cookie value to set after a correct password submission. */
export function makeAuthCookieValue(): string {
  return `${PAYLOAD}.${sign(PAYLOAD)}`;
}

/** Verifies a cookie value against the pinned payload + HMAC — no user input
 * is trusted, so this only ever checks the fixed session payload's signature. */
export function verifyAuthCookieValue(value: string | undefined): boolean {
  if (!value) return false;
  const [payload, signature] = value.split(".");
  if (payload !== PAYLOAD || !signature) return false;
  const expected = sign(PAYLOAD);
  const a = Buffer.from(signature, "hex");
  const b = Buffer.from(expected, "hex");
  return a.length === b.length && timingSafeEqual(a, b);
}

export function checkPassword(candidate: string): boolean {
  const expected = process.env.SITE_PASSWORD;
  if (!expected) throw new Error("SITE_PASSWORD env var is not set");
  const a = Buffer.from(candidate);
  const b = Buffer.from(expected);
  return a.length === b.length && timingSafeEqual(a, b);
}
