import Link from "next/link";

const LINKS = [
  { href: "/", label: "Overview" },
  { href: "/ask", label: "Ask" },
  { href: "/entry", label: "Market entry" },
  { href: "/korea", label: "Korea" },
  { href: "/india", label: "India" },
  { href: "/india/value-chain", label: "India value chain" },
  { href: "/corridor", label: "Corridor" },
  { href: "/players", label: "Players" },
  { href: "/sources", label: "Sources" },
  { href: "/gaps", label: "Gaps" },
  { href: "/methodology", label: "Methodology" },
];

export function NavBar() {
  return (
    <header className="border-b border-[var(--border)] bg-[var(--surface-1)]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-wrap items-center gap-x-6 gap-y-2 py-4">
        <Link href="/" className="font-serif text-lg font-semibold shrink-0">
          bpc-intel
        </Link>
        <nav className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
          {LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
