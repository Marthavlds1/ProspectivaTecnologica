const API_URL = "http://localhost:8000/chat";
const PROFILES_URL = "http://localhost:8000/profiles";
const PROVIDERS_URL = "http://localhost:8000/providers";

const form = document.getElementById("chatForm");
const chat = document.getElementById("chat");
const metricsGrid = document.getElementById("metricsGrid");
const profileInfo = document.getElementById("profileInfo");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const loadProfileBtn = document.getElementById("loadProfileBtn");

const messageInput = document.getElementById("message");
const systemPromptInput = document.getElementById("system_prompt");
const profileSelect = document.getElementById("copilot_profile");
const providerSelect = document.getElementById("provider");
const modelSelect = document.getElementById("model");

let profiles = {};
let providerModels = {};

async function loadProfiles() {
  try {
    const response = await fetch(PROFILES_URL);
    if (!response.ok) throw new Error("No se pudo consultar el endpoint /profiles.");
    profiles = await response.json();
    loadSelectedProfile();
  } catch (error) {
    console.error("No se pudieron cargar los perfiles:", error);
    systemPromptInput.value =
      "No se pudieron cargar los perfiles desde el backend. Verifica que FastAPI esté ejecutándose en http://localhost:8000.";
  }
}

async function loadProviders() {
  try {
    const response = await fetch(PROVIDERS_URL);
    if (!response.ok) throw new Error("No se pudo consultar el endpoint /providers.");
    providerModels = await response.json();
    renderModelOptions();
  } catch (error) {
    console.error("No se pudieron cargar los proveedores:", error);
    modelSelect.innerHTML = `<option value="">Error al cargar modelos</option>`;
  }
}

function renderModelOptions() {
  const provider = providerSelect.value;
  const models = providerModels[provider] || [];
  modelSelect.innerHTML = models
    .map((model) => `<option value="${escapeHtml(model)}">${escapeHtml(model)}</option>`)
    .join("");
}

function loadSelectedProfile() {
  const profileId = profileSelect.value;
  if (profiles[profileId]) {
    systemPromptInput.value = profiles[profileId].system_prompt;
  }
}

function getConfig() {
  return {
    provider: providerSelect.value,
    model: modelSelect.value,
    copilot_profile: profileSelect.value,
    system_prompt: systemPromptInput.value,
    temperature: Number(document.getElementById("temperature").value),
    top_p: Number(document.getElementById("top_p").value),
    max_tokens: Number(document.getElementById("max_tokens").value),
    num_ctx: Number(document.getElementById("num_ctx").value),
    repeat_penalty: Number(document.getElementById("repeat_penalty").value),
  };
}

function addMessage(role, content, type = "assistant") {
  const div = document.createElement("div");
  div.className = `message ${type}`;
  div.innerHTML = `<strong>${escapeHtml(role)}</strong>${escapeHtml(content)}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

function renderMetrics(data) {
  const metrics = data.metrics;

  profileInfo.innerHTML = `
    <strong>Proveedor:</strong> ${escapeHtml(data.provider)}&nbsp;&nbsp;
    <strong>Modelo:</strong> ${escapeHtml(data.model)}&nbsp;&nbsp;
    <strong>Perfil:</strong> ${escapeHtml(data.copilot_label)}
  `;

  const items = [
    ["Tiempo backend", `${metrics.wall_time_s.toFixed(3)} s`],
    ["Tiempo proveedor", `${metrics.provider_duration_s.toFixed(3)} s`],
    ["Tokens entrada", metrics.prompt_tokens],
    ["Tokens salida", metrics.completion_tokens],
    ["Tokens totales", metrics.total_tokens],
    ["Tokens/s aprox.", metrics.tokens_per_second.toFixed(2)],
  ];

  metricsGrid.innerHTML = items
    .map(
      ([label, value]) => `
      <div class="metric-card">
        <small>${label}</small>
        <strong>${value}</strong>
      </div>`
    )
    .join("");
}

function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) return;

  const payload = { message, ...getConfig() };

  addMessage("Usuario", message, "user");
  messageInput.value = "";
  sendBtn.disabled = true;
  sendBtn.textContent = "Generando...";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Error desconocido");

    addMessage(`Copiloto (${data.provider} / ${data.model})`, data.reply, "assistant");
    renderMetrics(data);
  } catch (error) {
    addMessage("Error", error.message, "error");
  } finally {
    sendBtn.disabled = false;
    sendBtn.textContent = "Enviar";
  }
});

clearBtn.addEventListener("click", () => {
  chat.innerHTML = "";
  profileInfo.textContent = "Sin perfil usado todavía";
  metricsGrid.innerHTML = "<span>Sin datos todavía</span>";
});

loadProfileBtn.addEventListener("click", loadSelectedProfile);
profileSelect.addEventListener("change", loadSelectedProfile);
providerSelect.addEventListener("change", renderModelOptions);

loadProfiles();
loadProviders();
