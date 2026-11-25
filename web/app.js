const state = {
  mode: "sample",
  sample: null,
  authMode: "login"
};

const byId = (id) => document.getElementById(id);

async function loadSample() {
  const response = await fetch("/api/sample");
  if (!response.ok) throw new Error("Could not load the sample scenario.");
  state.sample = await response.json();
  byId("jsonInput").value = JSON.stringify(state.sample, null, 2);
}

function showWorkspace(email) {
  byId("authScreen").classList.add("hidden");
  byId("appShell").classList.remove("hidden");
  byId("userEmail").textContent = email || "";
  byId("userEmail").title = email || "";
  loadSample().catch((error) => showError(error.message));
}

function setAuthMode(mode) {
  state.authMode = mode;
  const registering = mode === "register";
  byId("authTitle").textContent = registering ? "Create your account" : "Welcome back";
  byId("authSubtitle").textContent = registering
    ? "Set up your private planning workspace."
    : "Sign in to continue to your workspace.";
  byId("authSubmit").innerHTML = registering ? 'Create account <span>→</span>' : 'Sign in <span>→</span>';
  byId("authSwitchText").textContent = registering ? "Already have an account?" : "New to Routewise?";
  byId("authModeButton").textContent = registering ? "Sign in" : "Create an account";
  byId("authPassword").autocomplete = registering ? "new-password" : "current-password";
  byId("authPassword").value = "";
  byId("authError").classList.add("hidden");
}

byId("authModeButton").addEventListener("click", () => {
  setAuthMode(state.authMode === "login" ? "register" : "login");
});

byId("authForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = byId("authSubmit");
  const errorBox = byId("authError");
  const password = byId("authPassword").value;
  errorBox.classList.add("hidden");
  if (state.authMode === "register" && password.length < 8) {
    errorBox.textContent = "Use a password with at least 8 characters.";
    errorBox.classList.remove("hidden");
    return;
  }

  button.disabled = true;
  button.textContent = state.authMode === "register" ? "Creating account…" : "Signing in…";
  try {
    const response = await fetch(`/api/${state.authMode === "register" ? "register" : "login"}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: byId("authEmail").value, password })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to authenticate.");
    byId("authPassword").value = "";
    showWorkspace(result.email);
  } catch (error) {
    errorBox.textContent = error.message;
    errorBox.classList.remove("hidden");
  } finally {
    button.disabled = false;
    button.innerHTML = state.authMode === "register" ? 'Create account <span>→</span>' : 'Sign in <span>→</span>';
  }
});

byId("logoutButton").addEventListener("click", async () => {
  await fetch("/api/logout", { method: "POST" });
  byId("appShell").classList.add("hidden");
  byId("authScreen").classList.remove("hidden");
  byId("authEmail").value = "";
  setAuthMode("login");
});

async function restoreSession() {
  const response = await fetch("/api/session");
  const session = await response.json();
  if (session.authenticated) showWorkspace(session.email);
}

function setMode(mode) {
  state.mode = mode;
  document.querySelectorAll(".mode").forEach((button) => {
    const active = button.dataset.mode === mode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll(".mode-content").forEach((content) => {
    content.classList.toggle("hidden", content.id !== `${mode}Mode`);
  });
}

document.querySelectorAll(".mode").forEach((button) => {
  button.addEventListener("click", () => setMode(button.dataset.mode));
});

byId("sampleButton").addEventListener("click", async () => {
  try {
    await loadSample();
    setMode("sample");
    byId("error").classList.add("hidden");
  } catch (error) {
    showError(error.message);
  }
});

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&#39;"
  })[character]);
}

function detail(label, value) {
  return `<div class="trip-detail"><strong>${label}</strong>${value}</div>`;
}

function renderPlan(data) {
  const result = data.result;
  const trips = result.trips.map((trip) => `
    <article class="trip">
      <div class="trip-head">
        <div class="trip-title"><span class="trip-index">${String(trip.trip).padStart(2, "0")}</span><h3>Delivery trip ${trip.trip}</h3></div>
        <div class="trip-title"><span class="trip-meta">${trip.weight} / ${result.capacity} kg</span><span class="trip-method">${escapeHtml(trip.method)}</span></div>
      </div>
      <div class="trip-details">
        ${detail("Parcels", trip.parcels.map(escapeHtml).join(", "))}
        ${detail("Optimized stop order", trip.route.map(escapeHtml).join(" → "))}
        ${detail("Road-by-road path", trip.road_path.map(escapeHtml).join(" → "))}
        ${detail("Loading order · last parcel loaded first", trip.pack_order_LIFO.map(escapeHtml).join(" → "))}
        ${detail("Route distance", `${trip.distance} <span>(priority order: ${trip.baseline_distance})</span>`)}
      </div>
    </article>`).join("");

  const warnings = [];
  if (result.too_heavy.length) {
    warnings.push(`Over vehicle capacity: ${result.too_heavy.map(escapeHtml).join(", ")}`);
  }
  if (result.undeliverable.length) {
    warnings.push(`Unreachable destinations: ${result.undeliverable.map(escapeHtml).join(", ")}`);
  }

  byId("results").innerHTML = `
    <div class="results-heading">
      <div><div class="eyebrow"><span class="eyebrow-line"></span> OPTIMIZATION SUMMARY</div><h2>Your delivery plan</h2></div>
      <p>Parcel priority, vehicle capacity, and road distance considered</p>
    </div>
    <div class="metrics">
      <div class="metric"><span>Delivery trips</span><strong>${result.trips.length}</strong></div>
      <div class="metric"><span>Total route distance</span><strong>${result.total_distance}</strong><small>Across all planned trips</small></div>
      <div class="metric"><span>Distance reduced</span><strong>${result.saving_pct}%</strong><small>Compared with priority order</small></div>
      <div class="metric"><span>FFD bins / lower bound</span><strong>${result.bin_packing.ffd_bins} / ${result.bin_packing.lower_bound}</strong><small>Capacity planning reference</small></div>
    </div>
    ${warnings.length ? `<div class="alerts"><strong>Scenario notes</strong><br>${warnings.join("<br>")}</div>` : ""}
    <div class="trip-list">${trips || '<div class="empty-state">No deliverable parcels were found in this scenario.</div>'}</div>`;
  byId("results").classList.remove("hidden");
  byId("results").scrollIntoView({ behavior: "smooth", block: "start" });
}

function showError(message) {
  const error = byId("error");
  error.textContent = message;
  error.classList.remove("hidden");
}

byId("planButton").addEventListener("click", async () => {
  const button = byId("planButton");
  byId("error").classList.add("hidden");
  button.classList.add("loading");
  button.disabled = true;
  button.innerHTML = "Building your plan…";

  try {
    let path = "/api/plan";
    let payload = { exact_limit: Number(byId("exactLimit").value) };

    if (state.mode === "sample") {
      if (!state.sample) await loadSample();
      payload.data = state.sample;
    } else if (state.mode === "json") {
      payload.data = JSON.parse(byId("jsonInput").value);
    } else {
      path = "/api/generate";
      payload = {
        ...payload,
        parcels: Number(byId("parcelCount").value),
        nodes: Number(byId("nodeCount").value),
        capacity: Number(byId("capacity").value),
        seed: Number(byId("seed").value)
      };
    }

    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Unable to generate the delivery plan.");
    renderPlan(result);
  } catch (error) {
    showError(error.message);
  } finally {
    button.classList.remove("loading");
    button.disabled = false;
    button.innerHTML = 'Generate delivery plan <span>→</span>';
  }
});

restoreSession().catch(() => {});
