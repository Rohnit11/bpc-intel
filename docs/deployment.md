# Deploying bpc-intel

The dashboard lives in `web/` and deploys to Vercel from `main`.

## Vercel project settings

- **Root Directory: `web`** (this is a monorepo — the Python analysis layer is
  the repo root, the Next.js app is a subdirectory).
- Framework preset: Next.js (auto-detected).

## Environment variables

Set these in Vercel → Settings → Environment Variables, ticking all three
environments (Production, Preview, Development):

| Variable | Required | Notes |
|---|---|---|
| `SITE_PASSWORD` | yes | Shared password for the whole dashboard (`proxy.ts`). |
| `AUTH_SECRET` | yes | Any long random string; signs the auth cookie. |
| `CHAT_PROVIDER` | no | `groq` (default) \| `xai` \| `google` \| `anthropic`. |
| `CHAT_API_KEY` | no | Enables `/ask`. Without it the route returns a clean 503 and the rest of the site is unaffected. |
| `DATABASE_URL` | no | Neon Postgres. Enables question logging + the weekly knowledge-gap harvest. |

Vercel does **not** interpolate one env var inside another — `DATABASE_URL`
must contain the password inline, not a `$VAR` reference.

For `DATABASE_URL` use Neon's **pooled** connection string (the host contains
`-pooler`). The app uses `@neondatabase/serverless`, which is built for that
endpoint; `channel_binding=require` in the string is fine.

Apply `web/db/schema.sql` once against the database before first use.

## Groq is not Grok

Two different vendors, one letter apart:

- **`groq`** — Groq, `api.groq.com`. Fast inference for open models (Llama).
  Genuinely free tier with no data-sharing requirement. This is the default.
- **`xai`** — xAI's Grok, `api.x.ai`.

`CHAT_PROVIDER=grok` is deliberately **rejected** with an error naming both,
rather than guessing and silently sending traffic to (and billing you at) the
wrong vendor.

Prefer a provider whose free tier does not train on your traffic: this repo's
context includes licensed Euromonitor/Statista-derived figures that
`/methodology` commits to not redistributing, plus unpublished strategy.

## Deployments are blocked for unrecognised commit authors

**Land changes through a GitHub pull request, not a direct push to `main`.**

Vercel blocks builds whose git commit author is not linked to a Vercel seat
(`seatBlock`, `blockCode: COMMIT_AUTHOR_REQUIRED`). Such deployments appear in
the dashboard in state `BLOCKED` with **no build logs at all** — the build
never starts, and production silently keeps serving the previous build, so it
is easy to mistake for "the deploy worked".

Merge commits created by GitHub when a PR is merged are authored by the
GitHub account and deploy normally. A commit pushed straight to `main` from a
local machine whose `user.email` differs from that identity will be blocked.

If a deployment is stuck in `BLOCKED`:

1. Check the author: `git log -1 --format='%an <%ae>'`.
2. Either open a PR and merge it on GitHub, or align local git identity with
   the account that owns the Vercel project
   (`git config user.email "<that address>"`).

## Refresh cycle

Data changes flow through Python, never edited in the web app:

```bash
python -m lib.fetchers.refresh      # optional: re-fetch sources
python -m lib.web_export            # rebuild web/public/data/*.json
python -m lib.chat_index            # rebuild the /ask retrieval index
```

Commit the regenerated bundle and open a PR. Vercel redeploys on merge.
