import argparse
import html
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pandas as pd

from utils.data_handler import load_data, save_submission
from utils.db_setup import check_db_health


def print_banner() -> None:
    print("\n" + "=" * 60)
    print("Salary Transparency Platform")
    print("Browser-based local app")
    print("=" * 60)


def build_dashboard_html(df: pd.DataFrame, message: str | None = None) -> str:
    message_html = ""
    if message:
        message_html = f'<div class="message">{html.escape(message)}</div>'

    if df.empty:
        table_rows = '<tr><td colspan="4">No salary data yet.</td></tr>'
    else:
        preview = df.head(8).copy()
        rows = []
        for _, row in preview.iterrows():
            role = html.escape(str(row.get("Role", "")))
            location = html.escape(str(row.get("Company location", row.get("Company location (Country)", ""))))
            salary = html.escape(str(row.get("Monthly Gross Salary", "")))
            rows.append(f"<tr><td>{role}</td><td>{location}</td><td>{salary}</td></tr>")
        table_rows = "".join(rows)

    total_entries = len(df)
    salaries = pd.to_numeric(df.get("Monthly Gross Salary", pd.Series(dtype=float)), errors="coerce").dropna()
    average_salary = f"{salaries.mean():,.2f}" if not salaries.empty else "n/a"
    unique_roles = df["Role"].nunique() if "Role" in df.columns else 0
    countries = [str(value) for value in df.get("Company location", pd.Series(dtype=str)).dropna().astype(str).tolist() if str(value).strip()] if "Company location" in df.columns else []

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Salary Transparency Platform</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 2rem; background: #f5f7fb; color: #14213d; }}
    .card {{ background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); margin-bottom: 1rem; }}
    h1, h2 {{ margin-top: 0; }}
    form {{ display: grid; gap: 0.75rem; }}
    label {{ font-weight: 600; }}
    input, select {{ padding: 0.65rem; border: 1px solid #cfd8e3; border-radius: 8px; }}
    button {{ padding: 0.7rem 1rem; border: 0; border-radius: 8px; background: #2563eb; color: white; cursor: pointer; }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; }}
    .stat {{ background: #eef4ff; padding: 1rem; border-radius: 10px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 0.7rem; border-bottom: 1px solid #e5e7eb; text-align: left; }}
    .message {{ padding: 0.8rem; border-radius: 8px; background: #ecfdf3; color: #166534; margin-bottom: 1rem; }}
  </style>
</head>
<body>
  <div class=\"card\">
    <h1>Salary Transparency Platform</h1>
    <p>This local app now runs in your browser so users can submit and review salary data without using the terminal.</p>
    {message_html}
  </div>

  <div class=\"card\">
    <h2>Overview</h2>
    <div class=\"stats\">
      <div class=\"stat\"><strong>{total_entries}</strong><br />entries</div>
      <div class=\"stat\"><strong>{average_salary}</strong><br />average monthly gross salary</div>
      <div class=\"stat\"><strong>{unique_roles}</strong><br />unique roles</div>
      <div class=\"stat\"><strong>{len(set(countries))}</strong><br />locations represented</div>
    </div>
  </div>

  <div class=\"card\">
    <h2>Submit salary data</h2>
    <form action=\"/submit\" method=\"post\">
      <label>Name / role</label>
      <input name=\"Role\" placeholder=\"e.g. Software Engineer\" />
      <label>Company location</label>
      <input name=\"Company location\" placeholder=\"e.g. Lusaka\" />
      <label>Monthly Gross Salary</label>
      <input name=\"Monthly Gross Salary\" type=\"number\" step=\"0.01\" />
      <label>Salary Gross in USD</label>
      <input name=\"Salary Gross in USD\" type=\"number\" step=\"0.01\" />
      <label>Years of Experience</label>
      <input name=\"Years of Experience\" />
      <label>Degree</label>
      <input name=\"Degree\" />
      <label>Approx. No. of employees in company</label>
      <input name=\"Approx. No. of employees in company\" />
      <label>Your Country/ Location</label>
      <input name=\"Your Country/ Location\" />
      <label>Nationality</label>
      <input name=\"Nationality\" />
      <label>Industry</label>
      <input name=\"Industry\" />
      <button type=\"submit\">Save entry</button>
    </form>
  </div>

  <div class=\"card\">
    <h2>Recent entries</h2>
    <table>
      <thead><tr><th>Role</th><th>Location</th><th>Monthly Gross Salary</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
  </div>
</body>
</html>"""


class SalaryRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/health"):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"ok")
            return

        df = load_data()
        message = None
        if "?" in self.path:
            query = urllib.parse.urlsplit(self.path).query
            params = urllib.parse.parse_qs(query)
            if params.get("message"):
                message = params["message"][0]

        html_body = build_dashboard_html(df, message=message).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html_body)))
        self.end_headers()
        self.wfile.write(html_body)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/submit":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(content_length).decode("utf-8")
        form_data = urllib.parse.parse_qs(body, keep_blank_values=True)
        record = {}
        for key, values in form_data.items():
            if values:
                record[key] = values[0]

        success, message = save_submission(record)
        target = "/?message=" + urllib.parse.quote(message)
        if not success:
            target = "/?message=" + urllib.parse.quote("Submission failed: " + message)

        self.send_response(303)
        self.send_header("Location", target)
        self.end_headers()

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return


def run_cli() -> None:
    from components.filters import country_filter, industry_filter
    from components.forms import submission_form

    print_banner()

    if not check_db_health():
        print("Database health check failed. The app may be unable to read or save entries.")

    df = load_data()

    while True:
        print("\nMain menu")
        print("1. View summary")
        print("2. Show recent entries")
        print("3. Filter and view data")
        print("4. Submit a new salary entry")
        print("5. Exit")

        choice = input("Choose an option [1-5]: ").strip()

        if choice == "1":
            print_summary(df)
        elif choice == "2":
            show_entries(df)
        elif choice == "3":
            filtered = df.copy()
            selected_country = country_filter(filtered)
            if selected_country != "All":
                country_column = next(
                    (col for col in ["Company location (Country)", "Company location", "Your Country/ Location"] if col in filtered.columns),
                    None,
                )
                if country_column:
                    filtered = filtered[filtered[country_column].astype(str).str.strip() == selected_country]

            selected_industry = industry_filter(filtered)
            if selected_industry != "All Industries" and "Industry" in filtered.columns:
                filtered = filtered[filtered["Industry"].fillna("").astype(str).str.strip() == selected_industry]

            print(f"\nShowing {len(filtered)} entries for {selected_country} / {selected_industry}")
            show_entries(filtered)
        elif choice == "4":
            saved = submission_form(save_submission)
            if saved:
                df = load_data()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Please enter a valid option.")


def print_summary(df: pd.DataFrame) -> None:
    print(f"\nLoaded {len(df)} entries")
    if df.empty:
        print("No salary data available yet.")
        return

    if "Monthly Gross Salary" in df.columns:
        salaries = pd.to_numeric(df["Monthly Gross Salary"], errors="coerce").dropna()
        if not salaries.empty:
            print(f"Average salary: {salaries.mean():,.2f}")

    if "Role" in df.columns:
        print(f"Unique roles: {df['Role'].nunique()}")

    if "Company location (Country)" in df.columns:
        countries = [value for value in df["Company location (Country)"].dropna().astype(str).tolist() if value]
        print(f"Countries represented: {len(set(countries))}")


def show_entries(df: pd.DataFrame, limit: int = 20) -> None:
    if df.empty:
        print("No entries to display.")
        return

    display_columns = [
        col for col in ["Role", "Company location (Country)", "Monthly Gross Salary", "Years of Experience", "Industry"]
        if col in df.columns
    ]
    if not display_columns:
        display_columns = list(df.columns[:5])

    preview = df[display_columns].head(limit).copy()
    print(preview.to_string(index=False))


def run_browser_server(port: int = 8000) -> None:
    print_banner()
    if not check_db_health():
        print("Database health check failed. The app may be unable to read or save entries.")

    server = ThreadingHTTPServer(("0.0.0.0", port), SalaryRequestHandler)
    print(f"Open http://localhost:{port} or http://127.0.0.1:{port} in your browser")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Salary Transparency Platform")
    parser.add_argument("--cli", action="store_true", help="Run the terminal-based interface instead of the browser app")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")), help="Port for the browser app")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_browser_server(port=args.port)


if __name__ == "__main__":
    main()
