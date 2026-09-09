const DEMO_AUTH_KEY = "synapse_demo_auth";
const ROLE_LABELS = { admin: "Admin", qa: "Quality Assurance", maintenance: "Maintenance", ops: "Operations" };

function readDemoAuth() {
  try {
    const saved = JSON.parse(localStorage.getItem(DEMO_AUTH_KEY) || "null");
    if (saved?.name && ROLE_LABELS[saved.role]) return saved;
  } catch (_) {}
  return { name: "Demo User", role: "maintenance", label: ROLE_LABELS.maintenance };
}

window.synapseSupabase = null;
window.synapseGetAccessToken = async () => "";
window.synapseRefreshAccessToken = async () => "";
window.synapseSignOut = async () => {
  localStorage.removeItem(DEMO_AUTH_KEY);
  localStorage.removeItem("synapse_user");
  location.replace("/login");
};

function publishDemoAuth() {
  const identity = readDemoAuth();
  window.synapseAuth = { session: null, email: "demo@synapse.local", ...identity };
  document.body.classList.remove("auth-loading");
  const emailNode = document.getElementById("auth-email");
  if (emailNode) emailNode.textContent = "Demo mode";
  window.dispatchEvent(new CustomEvent("synapse-auth-ready", { detail: window.synapseAuth }));
}

function setupAuthPage() {
  const form = document.getElementById("auth-form");
  if (!form) return;
  const shell = document.getElementById("auth-shell");
  const status = document.getElementById("auth-status");
  const submit = document.getElementById("auth-submit");
  const loginTab = document.getElementById("auth-tab-login");
  const registerTab = document.getElementById("auth-tab-register");
  const swipe = document.getElementById("auth-swipe");
  const swipeHandle = document.getElementById("swipe-handle");
  const swipeLabel = document.getElementById("swipe-label");
  let mode = "signin";

  const resetSwipe = () => {
    swipe.classList.remove("dragging", "complete", "loading");
    swipe.style.setProperty("--swipe-x", "0px");
  };
  const render = () => {
    const signup = mode === "signup";
    shell.classList.toggle("signup", signup);
    document.getElementById("auth-title").textContent = signup ? "Create demo profile" : "Enter the demo";
    document.getElementById("auth-copy").textContent = "Use any name, password, and plant role to continue.";
    document.getElementById("visual-title").textContent = signup ? "Let’s set up your workspace." : "Welcome to the demo.";
    document.getElementById("visual-copy").textContent = "No account, email confirmation, or password service is required.";
    swipeLabel.textContent = signup ? "Swipe to enter demo" : "Swipe to log in";
    swipeHandle.setAttribute("aria-label", swipeLabel.textContent);
    loginTab.classList.toggle("active", !signup);
    registerTab.classList.toggle("active", signup);
    loginTab.setAttribute("aria-selected", String(!signup));
    registerTab.setAttribute("aria-selected", String(signup));
    resetSwipe();
  };
  render();
  loginTab.onclick = () => { mode = "signin"; status.textContent = ""; render(); };
  registerTab.onclick = () => { mode = "signup"; status.textContent = ""; render(); };

  const submitDemo = () => {
    if (swipe.classList.contains("loading")) return;
    const name = form.full_name.value.trim() || "Demo User";
    const role = ROLE_LABELS[form.role.value] ? form.role.value : "maintenance";
    localStorage.setItem(DEMO_AUTH_KEY, JSON.stringify({ name, role, label: ROLE_LABELS[role] }));
    submit.disabled = false;
    location.replace(new URLSearchParams(location.search).get("next") || "/app");
  };
  const finishDrag = event => {
    if (!swipe.classList.contains("dragging")) return;
    const max = Math.max(1, swipe.clientWidth - swipeHandle.offsetWidth - 10);
    const x = Math.max(0, Math.min(max, event.clientX - Number(swipe.dataset.startX)));
    swipe.classList.remove("dragging");
    if (x >= max * .72) submitDemo(); else resetSwipe();
  };
  swipeHandle.addEventListener("pointerdown", event => {
    swipe.dataset.startX = event.clientX;
    swipe.classList.add("dragging");
    swipeHandle.setPointerCapture(event.pointerId);
  });
  swipeHandle.addEventListener("pointermove", event => {
    if (!swipe.classList.contains("dragging")) return;
    const max = Math.max(1, swipe.clientWidth - swipeHandle.offsetWidth - 10);
    const x = Math.max(0, Math.min(max, event.clientX - Number(swipe.dataset.startX)));
    swipe.style.setProperty("--swipe-x", `${x}px`);
  });
  swipeHandle.addEventListener("pointerup", finishDrag);
  swipeHandle.addEventListener("pointercancel", resetSwipe);
  swipeHandle.addEventListener("keydown", event => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); submitDemo(); }
  });
  form.addEventListener("invalid", resetSwipe, true);
  form.onsubmit = event => { event.preventDefault(); submitDemo(); };
}

document.addEventListener("DOMContentLoaded", () => {
  setupAuthPage();
  if (document.body.dataset.authRequired === "true") publishDemoAuth();
  if (document.body.dataset.authPage === "true" && localStorage.getItem(DEMO_AUTH_KEY)) location.replace("/app");
});
