# undercurrent

A private thought journal. Write down what's on your mind, tag it with a feeling, and decide whether to keep it or let it go. Browse and search past entries, and see patterns in your feelings over time.

## Features

- **Write** — capture a thought, tag it with a feeling (or a custom one), and mark whether you like it
- **Keep it or let it go** — save a thought permanently, or release it without saving
- **Browse** — search past thoughts and filter by feeling or liked status
- **Patterns** — see how often each feeling comes up, plus a quick view of your recent emotional flow
- **Export** — download everything as a CSV at any time

## Tech

A single self-contained page (`index.html`) — no build step, no framework. Data lives in [Supabase](https://supabase.com) (Postgres + Auth), so thoughts sync across devices and are scoped to your account with Row Level Security.

## Setup

1. Create a free project at [supabase.com](https://supabase.com).
2. In the SQL Editor, run:

   ```sql
   create extension if not exists "pgcrypto";

   create table thoughts (
     id uuid primary key default gen_random_uuid(),
     user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
     text text not null,
     feeling text not null,
     liked boolean not null default false,
     created_at timestamptz not null default now()
   );

   alter table thoughts enable row level security;

   create policy "individuals manage own thoughts"
   on thoughts for all
   using (auth.uid() = user_id)
   with check (auth.uid() = user_id);
   ```

3. In **Project Settings → API Keys**, copy your Project URL and publishable (or anon) key.
4. Open `index.html` and set `SUPABASE_URL` and `SUPABASE_ANON_KEY` near the top of the `<script>` tag.

## Running locally

No build step needed — open `index.html` directly in a browser, or serve the folder with any static file server.

## Deploying

Push this repo to GitHub and connect it to Cloudflare Pages (or Workers static assets). Cloudflare just needs `index.html` at the repo root.

## Signing in

Create an account with an email and password. Supabase emails a confirmation link — click it, then log in. Logging in with the same account from any device shows the same thoughts.

## Project structure

Everything currently lives in one `index.html` (HTML, CSS, and JS inline). A split into separate HTML/CSS/JS files is planned.



