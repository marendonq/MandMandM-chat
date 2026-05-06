import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const appJs = fs.readFileSync(path.join(rootDir, "frontend/static/app.js"), "utf8");

class ClassList {
  constructor(element) {
    this.element = element;
    this.set = new Set();
  }

  add(name) {
    this.set.add(name);
    this.element.className = [...this.set].join(" ");
  }

  remove(name) {
    this.set.delete(name);
    this.element.className = [...this.set].join(" ");
  }

  contains(name) {
    return this.set.has(name);
  }

  toggle(name, force) {
    const shouldAdd = force === undefined ? !this.set.has(name) : Boolean(force);
    if (shouldAdd) this.add(name);
    else this.remove(name);
  }
}

class ElementStub {
  constructor(id = "") {
    this.id = id;
    this.attributes = new Map();
    this.className = "";
    this.classList = new ClassList(this);
    this.disabled = false;
    this.hidden = false;
    this.value = "";
    this.textContent = "";
    this.innerHTML = "";
    this.onclick = null;
    this.oninput = null;
  }

  setAttribute(name, value) {
    this.attributes.set(name, String(value));
  }

  getAttribute(name) {
    return this.attributes.get(name) || null;
  }

  focus() {
    this.focused = true;
  }

  querySelectorAll() {
    return [];
  }
}

function makeResponse(body, ok = true, status = ok ? 200 : 500) {
  return {
    ok,
    status,
    async json() {
      return body;
    },
  };
}

function makeHarness() {
  const ids = [
    "banner",
    "sessionInfo",
    "profileName",
    "profileAvatar",
    "contactsList",
    "conversationList",
    "notifList",
    "messageArea",
    "chatTitle",
    "presencePill",
    "messageInput",
    "btnSendMessage",
    "btnDeleteConversation",
    "btnCopyUID",
    "confirm-root",
    "confirm-close",
    "confirm-cancel",
    "confirm-delete-account",
    "btnLogout",
    "btnRefreshAll",
    "btnCreateGroup",
    "btnCreatePrivate",
    "modal-close",
    "modal-search",
    "modal-root",
    "modal-heading",
    "modal-group-panel",
    "modal-group-name",
    "modal-group-submit",
    "modal-options",
    "btnCreateNotif",
    "btnLoadNotif",
    "btnDeleteAccount",
  ];
  const elements = new Map(ids.map((id) => [id, new ElementStub(id)]));
  elements.get("messageArea").innerHTML = `
    <div class="empty-state">
      <div class="empty-mark">MM</div>
      <strong>Selecciona una conversación</strong>
      <span>Cuando abras un chat, los mensajes aparecerán aquí.</span>
    </div>`;
  const storage = new Map();
  const calls = [];
  const timers = [];

  storage.set(
    "mm_session",
    JSON.stringify({
      access_token: "token",
      user: { id: "me", full_name: "María Mesa", unique_id: "300123" },
    }),
  );
  storage.set(
    "mm_fake_messages",
    JSON.stringify({
      c1: [
        {
          message_id: "m1",
          sender_id: "me",
          recipient_id: "peer",
          content: "Hola equipo",
          status: "SENT",
        },
        {
          message_id: "m2",
          sender_id: "peer",
          recipient_id: "me",
          content: "Recibido claro",
          status: "DELIVERED",
        },
      ],
    }),
  );

  const document = {
    getElementById(id) {
      if (!elements.has(id)) elements.set(id, new ElementStub(id));
      return elements.get(id);
    },
    addEventListener() {},
  };

  const window = {
    MM_CONFIG: { API_BASE_URL: "http://api.test" },
    location: { href: "" },
    localStorage: {
      getItem(key) {
        return storage.has(key) ? storage.get(key) : null;
      },
      setItem(key, value) {
        storage.set(key, String(value));
      },
      removeItem(key) {
        storage.delete(key);
      },
    },
  };

  async function fetch(url, opts = {}) {
    calls.push({ url, opts });
    const route = String(url).replace("http://api.test", "");
    if (route === "/users/me") {
      return makeResponse({
        id: "me",
        full_name: "María Mesa",
        unique_id: "300123",
        contacts: ["peer"],
      });
    }
    if (route === "/users/peer") {
      return makeResponse({
        id: "peer",
        full_name: "Juan Pérez",
        unique_id: "301999",
        email: "juan@example.com",
      });
    }
    if (route === "/conversations/") {
      return makeResponse([
        { id: "c1", type: "private", members: ["me", "peer"] },
        { id: "c2", type: "group", name: "Proyecto", members: ["me", "peer"] },
      ]);
    }
    if (route === "/notifications/me") return makeResponse([]);
    if (route === "/presence/heartbeat") return makeResponse({});
    if (route === "/presence/users/peer") return makeResponse({ activity_status: "online" });
    if (route.endsWith("/delivered") || route.endsWith("/read")) return makeResponse({});
    if (route === "/presence/messages/m1") {
      return makeResponse({ receipts: [{ recipient_id: "peer", status: "SENT" }] });
    }
    if (route === "/presence/messages/m2") {
      return makeResponse({ receipts: [{ recipient_id: "me", status: "DELIVERED" }] });
    }
    if (route === "/users/me" && opts.method === "DELETE") return makeResponse({});
    return makeResponse({ detail: `Unexpected route ${route}` }, false, 404);
  }

  const context = {
    window,
    document,
    localStorage: window.localStorage,
    fetch,
    setInterval(fn, ms) {
      timers.push({ fn, ms });
      return timers.length;
    },
    clearInterval() {},
    setTimeout(fn) {
      fn();
      return 1;
    },
    crypto: { randomUUID: () => "uuid-1" },
    console,
  };
  context.globalThis = context;

  vm.runInNewContext(appJs, context, { filename: "app.js" });

  return { elements, storage, calls, window };
}

async function settle() {
  await Promise.resolve();
  await Promise.resolve();
  await new Promise((resolve) => setTimeout(resolve, 0));
}

const h = makeHarness();
await settle();

assert.equal(h.elements.get("profileName").textContent, "María Mesa");
assert.equal(h.elements.get("profileAvatar").textContent, "MM");
assert.equal(h.elements.get("btnCopyUID").hidden, false);
assert.match(h.elements.get("contactsList").innerHTML, /Juan Pérez/);
assert.match(h.elements.get("conversationList").innerHTML, /Juan Pérez/);
assert.match(h.elements.get("conversationList").innerHTML, /unread-badge/);
assert.match(h.elements.get("messageArea").innerHTML, /Selecciona una conversación/);

await h.elements.get("conversationList").onclick({
  target: {
    closest(selector) {
      assert.equal(selector, "[data-conversation]");
      return { getAttribute: () => "c1" };
    },
  },
});
await settle();

assert.equal(h.elements.get("chatTitle").textContent, "Juan Pérez");
assert.equal(h.elements.get("presencePill").textContent, "online");
assert.equal(h.elements.get("btnSendMessage").disabled, false);
assert.match(h.elements.get("messageArea").innerHTML, /bubble--out/);
assert.match(h.elements.get("messageArea").innerHTML, /bubble--in/);
assert.match(h.elements.get("messageArea").innerHTML, /Hola equipo/);
assert.match(h.elements.get("messageArea").innerHTML, /Recibido claro/);
assert.match(h.elements.get("messageArea").innerHTML, /Enviado/);
assert.match(h.elements.get("messageArea").innerHTML, /Recibido · Leído/);

h.elements.get("btnDeleteAccount").onclick();
assert.equal(h.elements.get("confirm-root").classList.contains("is-open"), true);
h.elements.get("confirm-cancel").onclick();
assert.equal(h.elements.get("confirm-root").classList.contains("is-open"), false);

console.log("frontend app render tests passed");
