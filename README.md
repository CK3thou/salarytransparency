# Salary Transparency Platform

The public website is a static app in `site/`, hosted on GitHub Pages and backed by
Supabase. The Python browser app in `main.py` remains available for local use and
stores data in SQLite; it is not the GitHub Pages server.

## Supabase setup

1. In the Supabase SQL Editor for the project, run
   `supabase/migrations/20261118000000_create_salary_entries.sql`.
2. In the repository's **Settings → Secrets and variables → Actions**, add the
   project publishable (or legacy `anon`) key as `SUPABASE_ANON_KEY`. Never use
   the `service_role` key in a browser app or GitHub Actions build for this site.
3. If this project has existing salary data, import it into `public.salary_entries`
   through the Supabase dashboard. The legacy SQLite database is not migrated
   automatically.

The migration enables public reads and anonymous inserts for the salary-entry
table. Do not include names or other identifying information in salary submissions.

## GitHub Pages deployment

The `Deploy static site to GitHub Pages` workflow builds the files in `site/`,
injects the Supabase URL and public key at build time, then deploys to
`https://ck3thou.github.io/salarytransparency/`. It runs on pushes to `main` and
can also be started manually from the Actions tab. The Pages source is already
configured to use GitHub Actions.

## Run locally

Install the requirements and start the local Python app:

```sh
pip install -r requirements.txt
python main.py
```

Open `http://127.0.0.1:8000`. To use the terminal interface, run
`python main.py --cli`.
