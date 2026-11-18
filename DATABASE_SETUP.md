# Supabase Setup

The GitHub Pages website reads and submits records through Supabase. Run the
following migration in the Supabase SQL Editor:

```text
supabase/migrations/20261118000000_create_salary_entries.sql
```

The migration creates `public.salary_entries`, enables row-level security, and
allows public reads and anonymous inserts. It does not allow anonymous updates
or deletes.

In the GitHub repository, add the Supabase project's publishable (or legacy
`anon`) key under **Settings → Secrets and variables → Actions** with the name
`SUPABASE_ANON_KEY`. The project URL is configured in the Pages workflow.
Never use a `service_role` key in client-side code.

Existing SQLite or CSV data is not transferred automatically. Import rows into
`public.salary_entries` using the Supabase dashboard's table import tool. The
table's main required fields are `role`, `company_location`,
`monthly_gross_salary`, and `currency`.
