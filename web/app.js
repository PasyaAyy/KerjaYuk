const API = "/api/v1";
const state = { jobs: [], companies: [], query: "", location: "", types: new Set(), totalJobs: null };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const numberFormat = new Intl.NumberFormat("id-ID");
const dateFormat = new Intl.DateTimeFormat("id-ID", { day: "numeric", month: "short", year: "numeric" });

async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, options);
  if (response.status === 204) return null;
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json") ? await response.json() : await response.text();
  if (!response.ok) {
    const message = typeof body === "object" && body ? body.detail : body;
    throw new Error(message || `Permintaan gagal (${response.status})`);
  }
  return body;
}

function formatType(type) {
  return ({ MAGANG: "Magang", PARUH_WAKTU: "Paruh waktu", PENUH_WAKTU: "Penuh waktu" })[type] || type;
}

function formatExpiry(value) {
  const expiry = new Date(`${value}T00:00:00`);
  return Number.isNaN(expiry.valueOf()) ? "" : `Berakhir ${dateFormat.format(expiry)}`;
}

function escapeForText(value) {
  return String(value ?? "");
}

function createElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = escapeForText(text);
  return element;
}

function currentFilters() {
  return {
    q: state.query.trim(),
    location: state.location.trim(),
    types: new Set(state.types),
  };
}

async function loadCompanies() {
  state.companies = await api("/companies");
  const select = $("#company-select");
  select.replaceChildren();
  const placeholder = new Option("Pilih perusahaan", "");
  placeholder.disabled = true;
  placeholder.selected = true;
  select.add(placeholder);
  for (const company of state.companies) select.add(new Option(company.name, String(company.id)));
  select.add(new Option("+ Buat perusahaan baru", "__new__"));
  $("#company-count").textContent = numberFormat.format(state.companies.length);
}

async function loadJobs() {
  const list = $("#job-list");
  const error = $("#load-error");
  list.setAttribute("aria-busy", "true");
  error.hidden = true;
  const filters = currentFilters();
  const params = new URLSearchParams();
  if (filters.q) params.set("q", filters.q);
  if (filters.location) params.set("location", filters.location);
  if (filters.types.size === 1) params.set("employment_type", [...filters.types][0]);
  try {
    let jobs = await api(`/jobs${params.size ? `?${params}` : ""}`);
    if (filters.types.size > 1) jobs = jobs.filter((job) => filters.types.has(job.employment_type));
    state.jobs = jobs;
    renderJobs(jobs);
    $("#result-count").textContent = `Menampilkan ${numberFormat.format(jobs.length)} lowongan`;
    if (filters.q === "" && filters.location === "" && filters.types.size === 0) state.totalJobs = jobs.length;
    $("#job-count").textContent = numberFormat.format(state.totalJobs ?? jobs.length);
  } catch (cause) {
    list.replaceChildren();
    error.hidden = false;
    error.textContent = `Lowongan belum dapat dimuat. ${cause.message}. Pastikan API dan database sudah berjalan.`;
    $("#result-count").textContent = "Data lowongan belum tersedia";
    $("#job-count").textContent = "—";
  } finally {
    list.setAttribute("aria-busy", "false");
  }
}

function renderJobs(jobs) {
  const list = $("#job-list");
  const sort = $("#sort-jobs").value;
  const sorted = [...jobs];
  if (sort === "newest") sorted.sort((a, b) => b.id - a.id);
  if (sort === "ending") sorted.sort((a, b) => a.expires_at.localeCompare(b.expires_at));
  list.replaceChildren();
  if (!sorted.length) {
    const empty = createElement("div", "empty-state");
    empty.append(createElement("h3", "", "Belum ada lowongan yang cocok"));
    empty.append(createElement("p", "", "Coba ubah kata kunci atau filter yang dipilih."));
    list.append(empty);
    return;
  }

  const companies = new Map(state.companies.map((company) => [company.id, company]));
  for (const job of sorted) {
    const company = companies.get(job.company_id);
    const card = createElement("article", "job-card");
    const mark = createElement("div", "company-mark", company?.name?.trim()?.charAt(0)?.toUpperCase() || "K");
    mark.setAttribute("aria-hidden", "true");

    const content = createElement("div", "job-card-content");
    content.append(createElement("p", "company-name", company?.name || "Perusahaan"));
    content.append(createElement("h3", "job-title", job.title));
    const meta = createElement("p", "job-meta");
    meta.append(createElement("span", "", job.location));
    meta.append(createElement("span", "dot", "•"));
    meta.append(createElement("span", "", formatType(job.employment_type)));
    content.append(meta);
    const tags = createElement("div", "job-tags");
    tags.append(createElement("span", "tag", formatType(job.employment_type)));
    if (job.expires_at) tags.append(createElement("span", "job-expiry", formatExpiry(job.expires_at)));
    content.append(tags);

    const actions = createElement("div", "job-actions");
    const save = createElement("button", "save-job", "♡");
    save.type = "button";
    save.setAttribute("aria-label", `Simpan lowongan ${job.title}`);
    const savedJobs = readSavedJobs();
    save.setAttribute("aria-pressed", String(savedJobs.has(job.id)));
    save.textContent = savedJobs.has(job.id) ? "♥" : "♡";
    save.addEventListener("click", () => {
      const saved = save.getAttribute("aria-pressed") === "true";
      const savedNow = readSavedJobs();
      if (saved) savedNow.delete(job.id);
      else savedNow.add(job.id);
      try { localStorage.setItem("kerjayuk:saved-jobs", JSON.stringify([...savedNow])); } catch { /* Storage can be disabled. */ }
      save.setAttribute("aria-pressed", String(!saved));
      save.textContent = saved ? "♡" : "♥";
      showToast(saved ? "Lowongan dihapus dari tersimpan." : "Lowongan disimpan di perangkat ini.");
    });
    const apply = createElement("button", "button button-dark apply-button", "Lamar sekarang  →");
    apply.type = "button";
    apply.addEventListener("click", () => openApplication(job, company));
    actions.append(save, apply);
    card.append(mark, content, actions);
    list.append(card);
  }
}

function readSavedJobs() {
  try {
    const saved = JSON.parse(localStorage.getItem("kerjayuk:saved-jobs") || "[]");
    return new Set(Array.isArray(saved) ? saved.map(Number) : []);
  } catch {
    return new Set();
  }
}

function updateTabs() {
  const selected = state.types.size === 1 ? [...state.types][0] : "";
  for (const tab of $$(".tab")) tab.classList.toggle("active", tab.dataset.type === selected);
  for (const checkbox of $$(".type-filter input")) checkbox.checked = state.types.has(checkbox.value);
}

function applySearchForm(event) {
  event.preventDefault();
  state.query = $("#search-query").value;
  state.location = $("#search-location").value;
  const queryType = ["MAGANG", "PARUH_WAKTU", "PENUH_WAKTU"].includes(state.query.trim().toUpperCase())
    ? state.query.trim().toUpperCase()
    : "";
  if (queryType) {
    state.types = new Set([queryType]);
    state.query = "";
    $("#search-query").value = "";
  }
  $("#filter-location").value = state.location;
  updateTabs();
  void loadJobs();
  $("#lowongan").scrollIntoView({ behavior: "smooth" });
}

function showToast(message) {
  const toast = $("#toast");
  toast.textContent = message;
  toast.classList.add("visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("visible"), 2600);
}

function openApplication(job, company) {
  const dialog = $("#apply-dialog");
  $("#apply-form").reset();
  $("#apply-message").textContent = "";
  $("#apply-message").classList.remove("success");
  $("#apply-job-title").textContent = `${job.title} · ${company?.name || "KerjaYuk"}`;
  $("#apply-form").dataset.jobId = String(job.id);
  dialog.showModal();
}

function openJobForm() {
  const dialog = $("#job-dialog");
  $("#job-form").reset();
  $("#job-message").textContent = "";
  $("#new-company-fields").hidden = true;
  const minDate = new Date();
  minDate.setDate(minDate.getDate() + 1);
  $("#job-form [name='expires_at']").min = minDate.toISOString().slice(0, 10);
  void loadCompanies().then(() => dialog.showModal()).catch((cause) => showToast(`Daftar perusahaan belum bisa dimuat: ${cause.message}`));
}

async function submitApplication(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const file = form.elements.cv.files[0];
  const message = $("#apply-message");
  const button = form.querySelector("button[type='submit']");
  message.classList.remove("success");
  if (!file) return;
  if (file.type !== "application/pdf" || !file.name.toLowerCase().endsWith(".pdf")) {
    message.textContent = "CV harus berupa file PDF.";
    return;
  }
  if (file.size > 2 * 1024 * 1024) {
    message.textContent = "Ukuran CV maksimal 2 MB.";
    return;
  }
  button.disabled = true;
  message.textContent = "Mengirim lamaran…";
  try {
    const data = new FormData(form);
    await api(`/jobs/${form.dataset.jobId}/applications`, { method: "POST", body: data });
    message.textContent = "Lamaran berhasil dikirim. Semoga sukses!";
    message.classList.add("success");
    form.reset();
  } catch (cause) {
    message.textContent = cause.message;
  } finally {
    button.disabled = false;
  }
}

async function submitJob(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const message = $("#job-message");
  const button = form.querySelector("button[type='submit']");
  button.disabled = true;
  message.textContent = "Menerbitkan lowongan…";
  try {
    let companyId = form.elements.company_id.value;
    if (companyId === "__new__") {
      const name = form.elements.company_name.value.trim();
      if (!name) throw new Error("Nama perusahaan wajib diisi.");
      const company = await api("/companies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, location: form.elements.company_location.value.trim() || null }),
      });
      companyId = String(company.id);
    }
    if (!companyId) throw new Error("Pilih atau buat perusahaan terlebih dahulu.");
    const payload = {
      company_id: Number(companyId),
      title: form.elements.title.value.trim(),
      description: form.elements.description.value.trim(),
      location: form.elements.location.value.trim(),
      employment_type: form.elements.employment_type.value,
      expires_at: form.elements.expires_at.value,
    };
    await api("/jobs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    $("#job-dialog").close();
    await loadCompanies();
    state.query = "";
    state.location = "";
    state.types.clear();
    $("#search-query").value = "";
    $("#search-location").value = "";
    $("#filter-location").value = "";
    updateTabs();
    await loadJobs();
    showToast("Lowongan berhasil diterbitkan.");
  } catch (cause) {
    message.textContent = cause.message;
  } finally {
    button.disabled = false;
  }
}

function initialize() {
  $("#search-form").addEventListener("submit", applySearchForm);
  $("#filter-location").addEventListener("input", (event) => { state.location = event.target.value; });
  $("#apply-filters").addEventListener("click", () => {
    state.location = $("#filter-location").value;
    state.types = new Set($$(".type-filter input:checked").map((checkbox) => checkbox.value));
    updateTabs();
    void loadJobs();
  });
  $("#reset-filters").addEventListener("click", () => {
    state.query = "";
    state.location = "";
    state.types.clear();
    $("#search-query").value = "";
    $("#search-location").value = "";
    $("#filter-location").value = "";
    updateTabs();
    void loadJobs();
  });
  for (const tab of $$(".tab")) {
    tab.addEventListener("click", () => {
      state.types = tab.dataset.type ? new Set([tab.dataset.type]) : new Set();
      updateTabs();
      void loadJobs();
    });
  }
  for (const quick of $$(".popular-searches button")) {
    quick.addEventListener("click", () => {
      if (quick.dataset.query) state.types = new Set([quick.dataset.query]);
      if (quick.dataset.location) {
        state.location = quick.dataset.location;
        $("#search-location").value = quick.dataset.location;
        $("#filter-location").value = quick.dataset.location;
      }
      updateTabs();
      void loadJobs();
      $("#lowongan").scrollIntoView({ behavior: "smooth" });
    });
  }
  $("#sort-jobs").addEventListener("change", () => renderJobs(state.jobs));
  $("#open-job-form").addEventListener("click", openJobForm);
  $("#nav-post-job").addEventListener("click", openJobForm);
  $("#browse-jobs").addEventListener("click", () => $("#lowongan").scrollIntoView({ behavior: "smooth" }));
  $("#apply-form").addEventListener("submit", submitApplication);
  $("#job-form").addEventListener("submit", submitJob);
  $("#company-select").addEventListener("change", (event) => {
    const isNew = event.target.value === "__new__";
    $("#new-company-fields").hidden = !isNew;
    $("#new-company-fields [name='company_name']").required = isNew;
  });
  for (const dialog of $$("dialog")) {
    dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
    dialog.querySelector("[data-close]").addEventListener("click", () => dialog.close());
  }
  $("#menu-toggle").addEventListener("click", (event) => {
    const open = $(".nav-links").classList.toggle("open");
    event.currentTarget.setAttribute("aria-expanded", String(open));
  });
  void loadCompanies().then(loadJobs).catch((cause) => {
    const error = $("#load-error");
    error.hidden = false;
    error.textContent = `Perusahaan belum dapat dimuat. ${cause.message}`;
  });
}

initialize();
