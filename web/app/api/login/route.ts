import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { AUTH_COOKIE, checkPassword, makeAuthCookieValue } from "@/lib/auth";

export async function POST(request: NextRequest) {
  const form = await request.formData();
  const password = String(form.get("password") ?? "");
  const from = String(form.get("from") ?? "/");
  const safeFrom = from.startsWith("/") ? from : "/";

  if (!checkPassword(password)) {
    const url = new URL("/login", request.url);
    url.searchParams.set("error", "1");
    url.searchParams.set("from", safeFrom);
    return NextResponse.redirect(url, { status: 303 });
  }

  const response = NextResponse.redirect(new URL(safeFrom, request.url), { status: 303 });
  response.cookies.set(AUTH_COOKIE, makeAuthCookieValue(), {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
  return response;
}
