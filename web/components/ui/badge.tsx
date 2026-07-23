import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium whitespace-nowrap",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-[var(--text-primary)] text-[var(--page-plane)]",
        outline: "border-[var(--border)] text-[var(--text-secondary)]",
      },
    },
    defaultVariants: { variant: "default" },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {
  style?: React.CSSProperties;
}

export function Badge({ className, variant, style, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} style={style} {...props} />
  );
}
