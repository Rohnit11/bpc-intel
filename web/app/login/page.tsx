export const metadata = { title: "Log in | bpc-intel" };

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ from?: string; error?: string }>;
}) {
  const { from = "/", error } = await searchParams;

  return (
    <div className="max-w-sm mx-auto mt-16">
      <h1 className="font-serif text-2xl font-semibold mb-2">bpc-intel</h1>
      <p className="text-sm text-[var(--text-secondary)] mb-6">
        Private research dashboard — enter the shared password to continue.
      </p>
      <form method="POST" action="/api/login" className="space-y-3">
        <input type="hidden" name="from" value={from} />
        <input
          type="password"
          name="password"
          placeholder="Password"
          autoFocus
          required
          className="w-full rounded-md border border-[var(--border)] bg-[var(--surface-1)] px-3 py-2 text-sm"
        />
        {error && (
          <p className="text-sm text-[var(--status-critical)]">Incorrect password. Try again.</p>
        )}
        <button
          type="submit"
          className="w-full rounded-md bg-[var(--text-primary)] text-[var(--page-plane)] px-3 py-2 text-sm font-medium"
        >
          Enter
        </button>
      </form>
    </div>
  );
}
