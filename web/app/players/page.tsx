import Link from "next/link";
import { getAnalysisArtifact, listAnalysisArtifacts } from "@/lib/data";
import { EntrantsTimeline } from "@/components/analysis/entrants-timeline";
import type { CompanyProfile, EntrantsArtifact } from "@/types/analysis";

export const metadata = { title: "Players | bpc-intel" };

function profileSlugs(): string[] {
  return listAnalysisArtifacts()
    .filter((id) => id.startsWith("profiles/") && !id.endsWith("_not_profiled"))
    .map((id) => id.replace("profiles/", ""));
}

export default function PlayersPage() {
  const slugs = profileSlugs();
  const profiles = slugs
    .map((s) => getAnalysisArtifact<CompanyProfile>(`profiles/${s}`))
    .filter((p): p is CompanyProfile => p !== null);
  const entrants = getAnalysisArtifact<EntrantsArtifact>("entrants_ma");

  return (
    <div className="space-y-8">
      <div>
        <h1 className="font-serif text-3xl font-semibold">Players &amp; entrants</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Company profiles and the new-entrant &amp; M&amp;A record — brand owners, platforms, and
          the deals reshaping both markets.
        </p>
      </div>

      {profiles.length > 0 ? (
        <section>
          <h2 className="font-serif text-xl font-semibold mb-3">Profiles</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {profiles.map((p) => (
              <Link
                key={p.slug}
                href={`/players/${p.slug}`}
                className="rounded-xl border border-[var(--border)] bg-[var(--surface-1)] p-4 hover:border-[var(--series-1)] transition-colors"
              >
                <div className="font-serif text-lg font-semibold">{p.name}</div>
                <div className="text-xs text-[var(--text-muted)] mb-1">{p.geography} · {p.role}</div>
                <p className="text-sm text-[var(--text-secondary)] line-clamp-3">{p.read}</p>
              </Link>
            ))}
          </div>
        </section>
      ) : (
        <p className="text-sm text-[var(--text-muted)]">
          Company profiles have not been generated yet — run <code>/entry-analysis</code>.
        </p>
      )}

      <section>
        <h2 className="font-serif text-xl font-semibold mb-3">New entrants &amp; M&amp;A</h2>
        <EntrantsTimeline artifact={entrants} />
      </section>
    </div>
  );
}
