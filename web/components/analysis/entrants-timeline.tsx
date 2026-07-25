import type { EntrantsArtifact } from "@/types/analysis";
import { formatSegmentName } from "@/lib/format";

const ACTION_COLOR: Record<string, string> = {
  acquired: "var(--status-critical)",
  invested: "var(--series-4)",
  launched: "var(--series-1)",
  entered: "var(--series-5)",
  partnered: "var(--series-7)",
};

export function EntrantsTimeline({ artifact }: { artifact: EntrantsArtifact | null }) {
  if (!artifact) {
    return <p className="text-sm text-[var(--text-muted)]">Entrants &amp; M&amp;A tracker not generated yet.</p>;
  }
  return (
    <div className="space-y-2">
      {artifact.events.map((e, i) => (
        <div
          key={i}
          className="flex gap-3 rounded-lg border border-[var(--border)] bg-[var(--surface-1)] p-3"
        >
          <div className="shrink-0 text-xs font-mono text-[var(--text-muted)] w-20">{e.date_or_period}</div>
          <div className="flex-1">
            <div className="text-sm">
              <span className="font-semibold">{e.actor}</span>{" "}
              <span
                className="rounded px-1.5 py-0.5 text-[11px] font-bold text-white"
                style={{ backgroundColor: ACTION_COLOR[e.action] ?? "var(--text-muted)" }}
              >
                {e.action}
              </span>{" "}
              {e.target && <span className="font-medium">{e.target}</span>}
              {e.corridor && (
                <span className="ml-1 rounded-full border border-[var(--series-7)] px-1.5 py-0.5 text-[10px] text-[var(--series-7)]">
                  CORRIDOR
                </span>
              )}
            </div>
            <p className="text-xs text-[var(--text-secondary)] mt-0.5">{e.what_it_signals}</p>
            <div className="text-[11px] text-[var(--text-muted)] mt-0.5">
              {e.segments.map(formatSegmentName).join(", ")} · {e.geography} · {e.source}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
