const state = {
  clientId: null,
  tools: [],
  activeTool: null,
  busy: false,
};

function getClientId() {
  let id = localStorage.getItem("textuvia_client_id");
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem("textuvia_client_id", id);
  }
  return id;
}

async function api(path, options = {}) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

function renderTools() {
  const tabs = document.getElementById("tool-tabs");
  tabs.innerHTML = "";
  state.tools.forEach((tool) => {
    const btn = document.createElement("button");
    btn.textContent = tool.label;
    btn.dataset.tool = tool.id;
    if (tool.id === state.activeTool) btn.classList.add("active");
    btn.addEventListener("click", () => {
      state.activeTool = tool.id;
      renderTools();
      renderOptions();
    });
    tabs.appendChild(btn);
  });
}

function renderOptions() {
  const wrap = document.getElementById("options");
  wrap.innerHTML = "";
  const tool = state.tools.find((t) => t.id === state.activeTool);
  if (!tool) return;
  Object.entries(tool.options).forEach(([name, values]) => {
    const div = document.createElement("div");
    div.className = "opt";
    const label = document.createElement("label");
    label.textContent = name.charAt(0).toUpperCase() + name.slice(1);
    const select = document.createElement("select");
    select.dataset.option = name;
    values.forEach((v) => {
      const opt = document.createElement("option");
      opt.value = v;
      opt.textContent = v.charAt(0).toUpperCase() + v.slice(1);
      select.appendChild(opt);
    });
    div.appendChild(label);
    div.appendChild(select);
    wrap.appendChild(div);
  });
}

function getSelectedOptions() {
  const result = {};
  document.querySelectorAll("#options select").forEach((sel) => {
    result[sel.dataset.option] = sel.value;
  });
  return result;
}

function setOutput(text) {
  const out = document.getElementById("output");
  out.textContent = text;
  out.classList.toggle("empty", !text);
  document.getElementById("copy-btn").classList.toggle("hidden", !text);
}

function showError(message) {
  const el = document.getElementById("error");
  el.textContent = message;
  el.classList.remove("hidden");
}

function clearError() {
  document.getElementById("error").classList.add("hidden");
}

function setCredits(value) {
  document.getElementById("credits").textContent = value;
}

async function refreshCredits() {
  try {
    const data = await api(`/api/credits/${state.clientId}`);
    setCredits(data.credits_remaining);
  } catch {
    setCredits("?");
  }
}

async function refreshHistory() {
  try {
    const data = await api(`/api/history/${state.clientId}`);
    const list = document.getElementById("history");
    list.innerHTML = "";
    if (!data.items.length) {
      const li = document.createElement("li");
      li.className = "empty-history";
      li.textContent = "No history yet — generate something!";
      list.appendChild(li);
      return;
    }
    data.items.forEach((item) => {
      const li = document.createElement("li");
      const meta = document.createElement("div");
      meta.className = "meta";
      meta.textContent = `${item.tool} · ${new Date(item.created_at).toLocaleString()}`;
      const snippet = document.createElement("div");
      snippet.className = "snippet";
      snippet.textContent = item.output_text.length > 140
        ? item.output_text.slice(0, 140) + "…"
        : item.output_text;
      li.appendChild(meta);
      li.appendChild(snippet);
      list.appendChild(li);
    });
  } catch {
    /* history is non-critical */
  }
}

async function run() {
  if (state.busy) return;
  const text = document.getElementById("input-text").value.trim();
  if (!text) {
    showError("Please enter some text first.");
    return;
  }
  clearError();
  state.busy = true;
  const btn = document.getElementById("run-btn");
  btn.disabled = true;
  btn.textContent = "Generating…";
  try {
    const data = await api(`/api/tools/${state.activeTool}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        client_id: state.clientId,
        text,
        options: getSelectedOptions(),
      }),
    });
    setOutput(data.result);
    setCredits(data.credits_remaining);
    refreshHistory();
  } catch (err) {
    showError(err.message);
    if (String(err.message).includes("credits")) refreshCredits();
  } finally {
    state.busy = false;
    btn.disabled = false;
    btn.textContent = "Generate";
  }
}

async function init() {
  state.clientId = getClientId();
  try {
    const config = await api("/api/tools");
    state.tools = config.tools;
    state.activeTool = config.tools[0]?.id;
    renderTools();
    renderOptions();
    if (config.demo_mode) {
      const badge = document.getElementById("mode-badge");
      badge.textContent = "Demo mode — set an AI API key for real results";
      badge.classList.remove("hidden");
    }
  } catch (err) {
    showError(`Failed to load app: ${err.message}`);
  }
  refreshCredits();
  refreshHistory();

  document.getElementById("run-btn").addEventListener("click", run);
  document.getElementById("copy-btn").addEventListener("click", () => {
    navigator.clipboard.writeText(document.getElementById("output").textContent);
  });
  document.getElementById("refresh-history").addEventListener("click", refreshHistory);
  document.getElementById("input-text").addEventListener("input", (e) => {
    document.getElementById("char-count").textContent = e.target.value.length;
  });
}

init();
