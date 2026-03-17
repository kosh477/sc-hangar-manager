const state = {
  token: localStorage.getItem("authToken") || "",
  userId: Number(localStorage.getItem("userId")) || null,
};

const byId = (id) => document.getElementById(id);

const authStatus = byId("auth-status");
const myData = byId("my-data");

const screens = {
  auth: byId("auth-screen"),
  register: byId("register-screen"),
  ships: byId("ships-screen"),
};

function setScreen(screenName) {
  Object.entries(screens).forEach(([name, el]) => {
    el.classList.toggle("hidden", name !== screenName);
  });
}

function updateAuthStatus(message = "") {
  authStatus.textContent = message || (state.token
    ? `Авторизован как user #${state.userId}`
    : "Не авторизован");
}

function renderList(el, items, formatter) {
  el.innerHTML = "";
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = "Нет данных";
    el.append(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = formatter(item);
    el.append(li);
  });
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) {
    headers.Authorization = `Bearer ${state.token}`;
  }
  const response = await fetch(path, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Request failed");
  }
  return payload;
}

async function openShipsCatalog() {
  if (!state.userId || !state.token) {
    setScreen("auth");
    updateAuthStatus();
    return;
  }

  try {
    const ships = await api(`/user/${state.userId}/ships`);
    renderList(myData, ships, (ship) => `${ship.vendor} ${ship.model} (${ship.name})`);
    setScreen("ships");
  } catch (error) {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userId");
    state.token = "";
    state.userId = null;
    updateAuthStatus(`Сессия недействительна: ${error.message}`);
    setScreen("auth");
  }
}

byId("open-register-link").addEventListener("click", (event) => {
  event.preventDefault();
  setScreen("register");
});

byId("open-login-link").addEventListener("click", (event) => {
  event.preventDefault();
  setScreen("auth");
});

byId("login-btn").addEventListener("click", async () => {
  try {
    const login = byId("login").value.trim();
    const password = byId("password").value;
    const data = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ login, password }),
    });
    state.token = data.accessToken;
    state.userId = data.user.id;
    localStorage.setItem("authToken", state.token);
    localStorage.setItem("userId", String(state.userId));
    updateAuthStatus();
    await openShipsCatalog();
  } catch (error) {
    updateAuthStatus(`Ошибка входа: ${error.message}`);
  }
});

byId("register-btn").addEventListener("click", async () => {
  try {
    const payload = {
      name: byId("reg-name").value.trim(),
      email: byId("reg-email").value.trim(),
      login: byId("reg-login").value.trim(),
      password: byId("reg-password").value,
    };
    const data = await api("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    state.token = data.accessToken;
    state.userId = data.user.id;
    localStorage.setItem("authToken", state.token);
    localStorage.setItem("userId", String(state.userId));
    updateAuthStatus();
    await openShipsCatalog();
  } catch (error) {
    updateAuthStatus(`Ошибка регистрации: ${error.message}`);
  }
});

byId("reload-ships-btn").addEventListener("click", async () => {
  await openShipsCatalog();
});

byId("logout-btn").addEventListener("click", () => {
  localStorage.removeItem("authToken");
  localStorage.removeItem("userId");
  state.token = "";
  state.userId = null;
  myData.innerHTML = "";
  updateAuthStatus();
  setScreen("auth");
});

updateAuthStatus();
openShipsCatalog();
