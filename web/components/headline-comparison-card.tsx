import type { Figure } from "@/types/bundle";
import { FigureValue } from "@/components/figure-value";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

/** One metric, KR vs IN, both shown big with original unit/basis/source beneath. */
export function HeadlineComparisonCard({
  title,
  kr,
  india,
}: {
  title: string;
  kr: Figure | null | undefined;
  india: Figure | null | undefined;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-2 gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            South Korea
          </div>
          <FigureValue figure={kr} emphasis />
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)] mb-1">
            India
          </div>
          <FigureValue figure={india} emphasis />
        </div>
      </CardContent>
    </Card>
  );
}
