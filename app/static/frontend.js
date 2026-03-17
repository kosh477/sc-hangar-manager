const state = {
  token: localStorage.getItem("authToken") || "",
  userId: Number(localStorage.getItem("userId")) || null,
};

const byId = (id) => document.getElementById(id);

const authStatus = byId("auth-status");
const myData = byId("my-data");
const publicData = byId("public-data");

function updateAuthStatus() {
  authStatus.textContent = state.token
    ? `Авторизован как user #${state.userId}`
    : "Не авторизован";
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
  } catch (error) {
    authStatus.textContent = `Ошибка входа: ${error.message}`;
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
  } catch (error) {
    authStatus.textContent = `Ошибка регистрации: ${error.message}`;
  }
});

byId("load-ships-btn").addEventListener("click", async () => {
  if (!state.userId) {
    authStatus.textContent = "Сначала выполните вход";
    return;
  }
  try {
    const ships = await api(`/user/${state.userId}/ships`);
    renderList(myData, ships, (ship) => `${ship.vendor} ${ship.model} (${ship.name})`);
  } catch (error) {
    authStatus.textContent = `Ошибка загрузки кораблей: ${error.message}`;
  }
});

byId("load-parts-btn").addEventListener("click", async () => {
  if (!state.userId) {
    authStatus.textContent = "Сначала выполните вход";
    return;
  }
  try {
    const parts = await api(`/user/${state.userId}/parts`);
    renderList(
      myData,
      parts,
      (part) => `${part.vendor} ${part.model} | ${part.class} | size ${part.size} | ${part.partType.type}`,
    );
  } catch (error) {
    authStatus.textContent = `Ошибка загрузки компонентов: ${error.message}`;
  }
});

byId("load-all-ships-btn").addEventListener("click", async () => {
  if (!state.userId) {
    authStatus.textContent = "Сначала выполните вход";
    return;
  }
  try {
    const ships = await api("/ships");
    renderList(publicData, ships, (ship) => `${ship.vendor} ${ship.model} (${ship.name})`);
  } catch (error) {
    authStatus.textContent = `Ошибка загрузки каталога: ${error.message}`;
  }
});

byId("load-all-parts-btn").addEventListener("click", async () => {
  if (!state.userId) {
    authStatus.textContent = "Сначала выполните вход";
    return;
  }
  try {
    const parts = await api("/parts");
    renderList(
      publicData,
      parts,
      (part) => `${part.vendor} ${part.model} | ${part.class} | size ${part.size} | ${part.partType.type}`,
    );
  } catch (error) {
    authStatus.textContent = `Ошибка загрузки каталога: ${error.message}`;
  }
});

updateAuthStatus();
