import { getSources } from "@/lib/data";
import { SourcesTable } from "@/components/sources-table";

export const metadata = { title: "Sources | bpc-intel" };

export default function SourcesPage() {
  const rows = getSources();
  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-serif text-3xl font-semibold">Sources ledger</h1>
        <p className="text-[var(--text-secondary)] mt-1">
          Every quantitative claim in this system, one row per data/sources.csv entry.
        </p>
      </div>
      <SourcesTable rows={rows} />
    </div>
  );
}
