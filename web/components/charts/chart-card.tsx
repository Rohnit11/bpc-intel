import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import type { ReactNode } from "react";

export function ChartCard({
  title,
  description,
  children,
  caption,
}: {
  title: string;
  description?: string;
  children: ReactNode;
  caption?: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        {children}
        {caption && <p className="mt-3 text-xs text-[var(--text-muted)] italic">{caption}</p>}
      </CardContent>
    </Card>
  );
}
