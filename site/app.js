import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const config = window.SUPABASE_CONFIG;
const rowsElement = document.querySelector("#salary-rows");
const loadStatus = document.querySelector("#load-status");
const entryCount = document.querySelector("#entry-count");
const form = document.querySelector("#salary-form");
const formStatus = document.querySelector("#form-status");
const submitButton = document.querySelector("#submit-button");
const formatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 2,
});

function setStatus(element, message, state = "") {
  element.textContent = message;
  element.dataset.state = state;
}

function appendCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value || "—";
  row.append(cell);
}

function renderRows(entries) {
  rowsElement.replaceChildren();

  if (entries.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.textContent = "No salary entries yet. Be the first to contribute.";
    row.append(cell);
    rowsElement.append(row);
    return;
  }

  for (const entry of entries) {
    const row = document.createElement("tr");
    appendCell(row, entry.role);
    appendCell(row, entry.company_location);
    appendCell(row, `${formatter.format(Number(entry.monthly_gross_salary))} ${entry.currency || ""}`.trim());
    rowsElement.append(row);
  }
}

async function loadEntries() {
  const { count, error: countError } = await supabase
    .from("salary_entries")
    .select("id", { count: "exact", head: true });

  if (countError) {
    throw countError;
  }

  const { data, error } = await supabase
    .from("salary_entries")
    .select("role, company_location, monthly_gross_salary, currency, submission_date")
    .order("submission_date", { ascending: false })
    .order("id", { ascending: false })
    .limit(10);

  if (error) {
    throw error;
  }

  renderRows(data);
  entryCount.textContent = `${count ?? 0} ${count === 1 ? "entry" : "entries"}`;
  setStatus(loadStatus, "");
}

let supabase;
if (!config?.url || !config?.anonKey) {
  setStatus(loadStatus, "Supabase is not configured. Add the project publishable key to GitHub Actions.", "error");
  entryCount.textContent = "Not connected";
  submitButton.disabled = true;
} else {
  supabase = createClient(config.url, config.anonKey);
  loadEntries().catch((error) => {
    console.error("Could not load salary data:", error);
    setStatus(loadStatus, "Salary data could not be loaded. Please try again later.", "error");
    entryCount.textContent = "Unavailable";
    rowsElement.replaceChildren();
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 3;
    cell.textContent = "Unable to connect to the salary database.";
    row.append(cell);
    rowsElement.append(row);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!supabase) {
    setStatus(formStatus, "The database connection is not configured.", "error");
    return;
  }

  const values = new FormData(form);
  const salary = Number(values.get("monthly_gross_salary"));
  const usdSalary = values.get("salary_gross_in_usd");
  const submission = {
    role: String(values.get("role")).trim(),
    company_location: String(values.get("company_location")).trim(),
    monthly_gross_salary: salary,
    currency: String(values.get("currency")),
    salary_gross_in_usd: usdSalary === "" ? null : Number(usdSalary),
    years_of_experience: String(values.get("years_of_experience")).trim() || null,
    industry: String(values.get("industry")).trim() || null,
    company_size: String(values.get("company_size")).trim() || null,
    degree: String(values.get("degree")).trim() || null,
    country_location: String(values.get("country_location")).trim() || null,
    nationality: String(values.get("nationality")).trim() || null,
  };

  if (!submission.role || !submission.company_location || !Number.isFinite(salary) || salary <= 0) {
    setStatus(formStatus, "Enter a role, location, and a positive monthly salary.", "error");
    return;
  }

  submitButton.disabled = true;
  setStatus(formStatus, "Submitting…");
  let error;
  try {
    ({ error } = await supabase.from("salary_entries").insert(submission));
  } catch (submitError) {
    console.error("Could not submit salary:", submitError);
    setStatus(formStatus, "Your entry could not be submitted. Please try again later.", "error");
    submitButton.disabled = false;
    return;
  }
  submitButton.disabled = false;

  if (error) {
    console.error("Could not submit salary:", error);
    setStatus(formStatus, "Your entry could not be submitted. Please try again later.", "error");
    return;
  }

  form.reset();
  setStatus(formStatus, "Thank you for contributing.", "success");
  try {
    await loadEntries();
  } catch (loadError) {
    console.error("Submission succeeded, but the list could not be refreshed:", loadError);
  }
});
