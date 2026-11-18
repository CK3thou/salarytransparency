import { createClient } from "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

const config = window.SUPABASE_CONFIG;
const rowsElement = document.querySelector("#salary-rows");
const loadStatus = document.querySelector("#load-status");
const entryCount = document.querySelector("#entry-count");
const form = document.querySelector("#salary-form");
const formStatus = document.querySelector("#form-status");
const submitButton = document.querySelector("#submit-button");
const filtersForm = document.querySelector("#filters-form");
const clearFiltersButton = document.querySelector("#clear-filters");
const recentViewButton = document.querySelector("#recent-view");
const allViewButton = document.querySelector("#all-view");
const overviewTitle = document.querySelector("#overview-title");
const pagination = document.querySelector("#pagination");
const previousPageButton = document.querySelector("#previous-page");
const nextPageButton = document.querySelector("#next-page");
const pageStatus = document.querySelector("#page-status");
const analyticsStatus = document.querySelector("#analytics-status");
const analyticsEmpty = document.querySelector("#analytics-empty");
const chartsGrid = document.querySelector("#charts-grid");
const numberFormatter = new Intl.NumberFormat(undefined, {
  maximumFractionDigits: 2,
});
const tablePageSize = 25;
const analyticsPageSize = 500;
const chartColors = ["#176b70", "#667eea", "#e27d60", "#8e6cbe", "#d4a72c", "#438a63", "#cc6688"];

let supabase;
let viewMode = "recent";
let currentPage = 0;
let filters = { role: "", location: "", industry: "", currency: "" };
let entryRequestId = 0;
let analyticsRequestId = 0;
let chartLibraryPromise;
let charts = {};

function setStatus(element, message, state = "") {
  element.textContent = message;
  element.dataset.state = state;
}

function escapeLikeValue(value) {
  return value.replace(/[\\%_]/g, "\\$&");
}

function applyFilters(query, activeFilters) {
  if (activeFilters.role) {
    query = query.ilike("role", `%${escapeLikeValue(activeFilters.role)}%`);
  }
  if (activeFilters.location) {
    query = query.ilike("company_location", `%${escapeLikeValue(activeFilters.location)}%`);
  }
  if (activeFilters.industry) {
    query = query.ilike("industry", `%${escapeLikeValue(activeFilters.industry)}%`);
  }
  if (activeFilters.currency) {
    query = query.eq("currency", activeFilters.currency);
  }
  return query;
}

function appendCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value === null || value === undefined || value === "" ? "—" : String(value);
  row.append(cell);
}

function formatSalary(value, currency) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return "—";
  }
  if (currency) {
    try {
      return new Intl.NumberFormat(undefined, {
        style: "currency",
        currency,
        maximumFractionDigits: 2,
      }).format(amount);
    } catch {
      return `${numberFormatter.format(amount)} ${currency}`;
    }
  }
  return numberFormatter.format(amount);
}

function formatDate(value) {
  if (!value) {
    return "—";
  }
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(date);
}

function renderRows(entries) {
  rowsElement.replaceChildren();

  if (entries.length === 0) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 7;
    cell.textContent = filters.role || filters.location || filters.industry || filters.currency
      ? "No entries match these filters."
      : "No salary entries yet. Be the first to contribute.";
    row.append(cell);
    rowsElement.append(row);
    return;
  }

  for (const entry of entries) {
    const row = document.createElement("tr");
    appendCell(row, entry.role);
    appendCell(row, entry.company_location);
    appendCell(row, formatSalary(entry.monthly_gross_salary, entry.currency));
    appendCell(row, entry.years_of_experience);
    appendCell(row, entry.industry);
    appendCell(row, entry.degree);
    appendCell(row, formatDate(entry.submission_date));
    rowsElement.append(row);
  }
}

function updatePagination(count, pageSize) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  pagination.hidden = viewMode !== "all";
  previousPageButton.disabled = currentPage === 0;
  nextPageButton.disabled = currentPage >= totalPages - 1;
  pageStatus.textContent = `Page ${currentPage + 1} of ${totalPages}`;
}

async function loadEntries() {
  const requestId = ++entryRequestId;
  const pageSize = viewMode === "all" ? tablePageSize : 10;
  const firstRow = currentPage * pageSize;
  setStatus(loadStatus, "Loading salary entries…");

  let query = supabase
    .from("salary_entries")
    .select(
      "id, role, company_location, monthly_gross_salary, currency, years_of_experience, industry, degree, submission_date",
      { count: "exact" },
    );
  query = applyFilters(query, filters)
    .order("submission_date", { ascending: false })
    .order("id", { ascending: false })
    .range(firstRow, firstRow + pageSize - 1);

  const { data, error, count } = await query;
  if (requestId !== entryRequestId) {
    return;
  }
  if (error) {
    throw error;
  }

  const matchingCount = count ?? 0;
  const visibleCount = Math.min(pageSize, Math.max(0, matchingCount - firstRow));
  renderRows(data ?? []);
  entryCount.textContent = `${matchingCount} ${matchingCount === 1 ? "entry" : "entries"}`;
  if (viewMode === "all") {
    const firstVisible = matchingCount === 0 ? 0 : firstRow + 1;
    setStatus(loadStatus, `Showing ${firstVisible}-${firstRow + visibleCount} of ${matchingCount} matching entries.`);
  } else {
    setStatus(loadStatus, `Showing ${visibleCount} most recent of ${matchingCount} matching entries.`);
  }
  updatePagination(matchingCount, pageSize);
}

function loadChartLibrary() {
  if (window.Chart) {
    return Promise.resolve(window.Chart);
  }
  if (!chartLibraryPromise) {
    chartLibraryPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js";
      script.onload = () => window.Chart ? resolve(window.Chart) : reject(new Error("Chart.js did not initialize."));
      script.onerror = () => reject(new Error("Chart.js could not be loaded."));
      document.head.append(script);
    });
  }
  return chartLibraryPromise;
}

function destroyCharts() {
  for (const chart of Object.values(charts)) {
    chart.destroy();
  }
  charts = {};
}

async function fetchAnalyticsRows(activeFilters, requestId) {
  const entries = [];
  let firstRow = 0;

  while (requestId === analyticsRequestId) {
    let query = supabase
      .from("salary_entries")
      .select("id, role, monthly_gross_salary, currency, years_of_experience, industry, degree");
    query = applyFilters(query, activeFilters)
      .order("id", { ascending: true })
      .range(firstRow, firstRow + analyticsPageSize - 1);

    const { data, error } = await query;
    if (error) {
      throw error;
    }
    if (requestId !== analyticsRequestId) {
      return null;
    }

    entries.push(...(data ?? []));
    if (!data || data.length < analyticsPageSize) {
      break;
    }
    firstRow += analyticsPageSize;
  }

  return entries;
}

function summarizeCategories(entries, field) {
  const counts = new Map();
  for (const entry of entries) {
    const label = String(entry[field] ?? "").trim() || "Not specified";
    counts.set(label, (counts.get(label) ?? 0) + 1);
  }
  const ranked = [...counts.entries()].sort((left, right) => right[1] - left[1]);
  const top = ranked.slice(0, 8);
  if (ranked.length > top.length) {
    top.push(["Other", ranked.slice(8).reduce((sum, item) => sum + item[1], 0)]);
  }
  return top;
}

function renderAnalytics(entries, Chart) {
  destroyCharts();
  if (entries.length === 0) {
    chartsGrid.classList.add("is-hidden");
    analyticsEmpty.hidden = false;
    analyticsEmpty.textContent = "No entries match the current filters.";
    return;
  }

  analyticsEmpty.hidden = true;
  chartsGrid.classList.remove("is-hidden");

  const roleStats = new Map();
  const currencyNames = new Set();
  const roleCounts = new Map();
  for (const entry of entries) {
    const role = String(entry.role ?? "").trim() || "Not specified";
    const currency = String(entry.currency ?? "").trim() || "Unknown";
    const salary = Number(entry.monthly_gross_salary);
    if (!Number.isFinite(salary)) {
      continue;
    }
    const key = `${role}\u0000${currency}`;
    const summary = roleStats.get(key) ?? { role, currency, sum: 0, count: 0 };
    summary.sum += salary;
    summary.count += 1;
    roleStats.set(key, summary);
    roleCounts.set(role, (roleCounts.get(role) ?? 0) + 1);
    currencyNames.add(currency);
  }

  const roles = [...roleCounts.entries()]
    .sort((left, right) => right[1] - left[1])
    .slice(0, 10)
    .map(([role]) => role);
  const currencies = [...currencyNames].sort();
  charts.roleSalary = new Chart(document.querySelector("#role-salary-chart"), {
    type: "bar",
    data: {
      labels: roles,
      datasets: currencies.map((currency, index) => ({
        label: currency,
        data: roles.map((role) => {
          const summary = roleStats.get(`${role}\u0000${currency}`);
          return summary ? summary.sum / summary.count : null;
        }),
        backgroundColor: chartColors[index % chartColors.length],
        borderRadius: 5,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: { y: { beginAtZero: true, ticks: { callback: (value) => numberFormatter.format(value) } } },
    },
  });

  const industries = summarizeCategories(entries, "industry");
  charts.industry = new Chart(document.querySelector("#industry-chart"), {
    type: "doughnut",
    data: {
      labels: industries.map(([label]) => label),
      datasets: [{
        data: industries.map(([, count]) => count),
        backgroundColor: chartColors,
        borderWidth: 2,
        borderColor: "#fff",
      }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
  });

  const experienceData = new Map();
  for (const entry of entries) {
    const experienceMatch = String(entry.years_of_experience ?? "").match(/\d+(?:\.\d+)?/);
    const salary = Number(entry.monthly_gross_salary);
    if (!experienceMatch || !Number.isFinite(salary)) {
      continue;
    }
    const currency = String(entry.currency ?? "").trim() || "Unknown";
    const points = experienceData.get(currency) ?? [];
    points.push({ x: Number(experienceMatch[0]), y: salary });
    experienceData.set(currency, points);
  }
  charts.experience = new Chart(document.querySelector("#experience-chart"), {
    type: "scatter",
    data: {
      datasets: [...experienceData.entries()].map(([currency, points], index) => ({
        label: currency,
        data: points,
        backgroundColor: chartColors[index % chartColors.length],
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: {
        x: { title: { display: true, text: "Years of experience" }, beginAtZero: true },
        y: { title: { display: true, text: "Monthly gross salary" }, beginAtZero: true },
      },
    },
  });

  const degrees = summarizeCategories(entries, "degree");
  charts.degree = new Chart(document.querySelector("#degree-chart"), {
    type: "doughnut",
    data: {
      labels: degrees.map(([label]) => label),
      datasets: [{
        data: degrees.map(([, count]) => count),
        backgroundColor: chartColors,
        borderWidth: 2,
        borderColor: "#fff",
      }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "bottom" } } },
  });
}

async function loadAnalytics() {
  const requestId = ++analyticsRequestId;
  const activeFilters = { ...filters };
  setStatus(analyticsStatus, "Calculating analytics…");

  try {
    const entries = await fetchAnalyticsRows(activeFilters, requestId);
    if (!entries || requestId !== analyticsRequestId) {
      return;
    }
    const Chart = await loadChartLibrary();
    if (requestId !== analyticsRequestId) {
      return;
    }
    renderAnalytics(entries, Chart);
    setStatus(analyticsStatus, `Analytics based on ${entries.length} matching ${entries.length === 1 ? "entry" : "entries"}.`);
  } catch (error) {
    if (requestId !== analyticsRequestId) {
      return;
    }
    console.error("Could not load salary analytics:", error);
    destroyCharts();
    chartsGrid.classList.add("is-hidden");
    analyticsEmpty.hidden = false;
    analyticsEmpty.textContent = "Analytics could not be loaded. Please try again later.";
    setStatus(analyticsStatus, "Analytics unavailable.", "error");
  }
}

function showLoadError(error) {
  console.error("Could not load salary data:", error);
  setStatus(loadStatus, "Salary data could not be loaded. Please try again later.", "error");
  entryCount.textContent = "Unavailable";
  rowsElement.replaceChildren();
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = 7;
  cell.textContent = "Unable to connect to the salary database.";
  row.append(cell);
  rowsElement.append(row);
}

function refreshData() {
  loadEntries().catch(showLoadError);
  loadAnalytics();
}

function setViewMode(mode) {
  viewMode = mode;
  currentPage = 0;
  const showRecent = mode === "recent";
  recentViewButton.classList.toggle("is-active", showRecent);
  recentViewButton.setAttribute("aria-pressed", String(showRecent));
  allViewButton.classList.toggle("is-active", !showRecent);
  allViewButton.setAttribute("aria-pressed", String(!showRecent));
  overviewTitle.textContent = showRecent ? "Recent salaries" : "All salary entries";
  loadEntries().catch(showLoadError);
}

filtersForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const values = new FormData(filtersForm);
  filters = {
    role: String(values.get("role") ?? "").trim(),
    location: String(values.get("location") ?? "").trim(),
    industry: String(values.get("industry") ?? "").trim(),
    currency: String(values.get("currency") ?? "").trim(),
  };
  currentPage = 0;
  refreshData();
});

clearFiltersButton.addEventListener("click", () => {
  filtersForm.reset();
  filters = { role: "", location: "", industry: "", currency: "" };
  currentPage = 0;
  refreshData();
});

recentViewButton.addEventListener("click", () => setViewMode("recent"));
allViewButton.addEventListener("click", () => setViewMode("all"));

previousPageButton.addEventListener("click", () => {
  if (currentPage > 0) {
    currentPage -= 1;
    loadEntries().catch(showLoadError);
  }
});

nextPageButton.addEventListener("click", () => {
  currentPage += 1;
  loadEntries().catch(showLoadError);
});

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
  currentPage = 0;
  refreshData();
});

if (!config?.url || !config?.anonKey) {
  setStatus(loadStatus, "Supabase is not configured. Add the project publishable key to GitHub Actions.", "error");
  entryCount.textContent = "Not connected";
  submitButton.disabled = true;
  setStatus(analyticsStatus, "Supabase is not configured.", "error");
  chartsGrid.classList.add("is-hidden");
} else {
  supabase = createClient(config.url, config.anonKey);
  refreshData();
}
