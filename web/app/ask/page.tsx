import Link from "next/link";
import { ChatPanel } from "@/components/chat-panel";

export const metadata = { title: "Ask | bpc-intel" };

export default function AskPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-4">
        <h1 className="font-serif text-3xl font-semibold">Ask the research</h1>
        <p className="text-[var(--text-secondary)] mt-1 text-sm">
          A grounded assistant over every sourced figure and analysis artifact in this system.
          Unanswered questions become research gaps — see{" "}
          <Link href="/gaps" className="underline text-[var(--series-1)]">
            the gaps register
          </Link>{" "}
          and{" "}
          <Link href="/methodology" className="underline text-[var(--series-1)]">
            methodology
          </Link>
          .
        </p>
      </div>
      <ChatPanel />
    </div>
  );
}
