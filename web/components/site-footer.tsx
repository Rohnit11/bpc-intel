import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-[var(--border)] bg-[var(--surface-1)] mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 text-xs text-[var(--text-muted)] space-y-2">
        <p>
          South Korea × India Beauty &amp; Personal Care market intelligence — private
          research. Figures from Euromonitor Passport, Statista, and other licensed
          sources are shown here under academic fair-use for personal research only;
          do not redistribute. See{" "}
          <Link href="/methodology" className="underline hover:text-[var(--text-secondary)]">
            /methodology
          </Link>{" "}
          for the full evidence constitution.
        </p>
        <p className="flex items-center justify-between">
          <span>bpc-intel dashboard — data refreshed locally, deployed via Vercel.</span>
          <a href="/api/logout" className="underline hover:text-[var(--text-secondary)]">
            Log out
          </a>
        </p>
      </div>
    </footer>
  );
}
