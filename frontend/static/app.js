(function () {
  const sessionKey = "mm_session";
  const apiBaseUrl = (window.MM_CONFIG && window.MM_CONFIG.API_BASE_URL) || "http://127.0.0.1:8000";

  const qs = (id) => document.getElementById(id);
  const banner = qs("banner");
  const sessionInfo = qs("sessionInfo");
  const profileName = qs("profileName");
  const profileAvatar = qs("profileAvatar");
  const contactsList = qs("contactsList");
  const conversationList = qs("conversationList");
  const notifList = qs("notifList");
  const messageArea = qs("messageArea");
  const chatTitle = qs("chatTitle");
  const presencePill = qs("presencePill");
  const messageInput = qs("messageInput");

  const btnSendMessage = qs("btnSendMessage");
  const btnDeleteConversation = qs("btnDeleteConversation");
  const btnCopyUID = qs("btnCopyUID");
  const btnAttachFile = qs("btnAttachFile");
  const fileInput = qs("fileInput");
  const filePreview = qs("filePreview");
  const filePreviewName = qs("filePreviewName");
  const btnCancelFile = qs("btnCancelFile");
  const confirmRoot = qs("confirm-root");
  const confirmClose = qs("confirm-close");
  const confirmCancel = qs("confirm-cancel");
  const confirmDeleteAccount = qs("confirm-delete-account");

  let pendingFile = null;

  let session = null;
  let profile = null;
  let contactsById = new Map();
  let peerProfilesById = new Map();
  let conversations = [];
  let messagesByConversation = new Map();
  let activeConversation = null;
  let receiptPollTimer = null;
  const RECEIPT_POLL_MS = 2500;

  let modalMode = "private";
  const groupSelectedIds = new Set();

  function showBanner(text, ok = true) {
    banner.className = ok ? "banner ok" : "banner error";
    banner.textContent = text;
  }

  function readSession() {
    try {
      const raw = localStorage.getItem(sessionKey);
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (_) {
      return null;
    }
  }

  function saveSession(s) {
    localStorage.setItem(sessionKey, JSON.stringify(s));
  }

  function clearSession() {
    localStorage.removeItem(sessionKey);
  }

  function apiUrl(path) {
    return `${apiBaseUrl}${path}`;
  }

  async function api(path, opts = {}) {
    const headers = { "Content-Type": "application/json", ...(opts.headers || {}) };
    const res = await fetch(apiUrl(path), { ...opts, headers });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = body.detail || JSON.stringify(body) || `HTTP ${res.status}`;
      throw new Error(msg);
    }
    return body;
  }

  function requireAuth() {
    session = readSession();
    if (!session || !session.user || !session.user.id) {
      window.location.href = "/static/auth.html?oauth=need_login";
      return false;
    }
    return true;
  }

  function messageIdOf(m) {
    return m.message_id || m.id;
  }

  function recipientIdForMessage(m, conv) {
    if (m.recipient_id) return m.recipient_id;
    const members = conv?.members || [];
    return members.find((id) => id !== m.sender_id) || null;
  }

  function normalizeMessage(m, conv) {
    return {
      ...m,
      message_id: messageIdOf(m),
      recipient_id: recipientIdForMessage(m, conv),
      status: m.status || "SENT",
    };
  }

  function fileDownloadUrl(fileId) {
    return apiUrl(`/files/${encodeURIComponent(fileId)}/download`);
  }

  async function hydrateFilesForMessages(list) {
    await Promise.all(
      list
        .filter((m) => m.file_id && !m.file)
        .map(async (m) => {
          try {
            m.file = await api(`/files/${encodeURIComponent(m.file_id)}`);
          } catch (_) {
            m.file = { id: m.file_id, file_name: "Archivo adjunto" };
          }
        }),
    );
  }

  async function postDeliveredForMessage(m) {
    const uid = session.user.id;
    await api(`/presence/messages/${encodeURIComponent(messageIdOf(m))}/delivered`, {
      method: "POST",
      body: JSON.stringify({ recipient_id: uid }),
    });
  }

  async function postReadForMessage(m) {
    const uid = session.user.id;
    await api(`/presence/messages/${encodeURIComponent(messageIdOf(m))}/read`, {
      method: "POST",
      body: JSON.stringify({ recipient_id: uid }),
    });
  }

  function receiptStatusFromServerPayload(m, data, uid) {
    const receipts = data.receipts || [];
    if (m.recipient_id === uid) {
      const mine = receipts.find((r) => r.recipient_id === uid);
      return mine?.status || null;
    }
    if (m.sender_id === uid) {
      const r = receipts.find((x) => x.recipient_id === m.recipient_id);
      return r?.status || null;
    }
    return null;
  }

  async function syncReceiptStatusForConversation(convId) {
    const conv = conversations.find((c) => c.id === convId) || activeConversation;
    const list = messagesByConversation.get(convId) || [];
    const uid = session.user.id;
    let changed = false;
    for (const m of list) {
      m.recipient_id = recipientIdForMessage(m, conv);
      if (m.recipient_id !== uid && m.sender_id !== uid) continue;
      try {
        const data = await api(`/presence/messages/${encodeURIComponent(messageIdOf(m))}`);
        const next = receiptStatusFromServerPayload(m, data, uid);
        if (next && receiptStatusRank(next) > receiptStatusRank(m.status || "SENT")) {
          m.status = next;
          changed = true;
        }
      } catch (_) {}
    }
    if (changed) messagesByConversation.set(convId, list);
  }

  async function syncReceiptStatusFromServerForAllMessages() {
    let changed = false;
    const uid = session.user.id;
    for (const [convId, list] of messagesByConversation.entries()) {
      const conv = conversations.find((c) => c.id === convId);
      for (const m of list) {
        m.recipient_id = recipientIdForMessage(m, conv);
        if (m.recipient_id !== uid && m.sender_id !== uid) continue;
        try {
          const data = await api(`/presence/messages/${encodeURIComponent(messageIdOf(m))}`);
          const next = receiptStatusFromServerPayload(m, data, uid);
          if (next && receiptStatusRank(next) > receiptStatusRank(m.status || "SENT")) {
            m.status = next;
            changed = true;
          }
        } catch (_) {}
      }
    }
    if (changed) messagesByConversation = new Map(messagesByConversation);
  }

  function stopReceiptPolling() {
    if (receiptPollTimer) {
      clearInterval(receiptPollTimer);
      receiptPollTimer = null;
    }
  }

  function startReceiptPolling() {
    stopReceiptPolling();
    if (!activeConversation) return;
    const convId = activeConversation.id;
    receiptPollTimer = setInterval(async () => {
      if (!activeConversation || activeConversation.id !== convId) return;
      try {
        await syncReceiptStatusForConversation(convId);
        renderMessages();
      } catch (_) {}
    }, RECEIPT_POLL_MS);
  }

  function receiptStatusLabel(st) {
    const s = st || "SENT";
    if (s === "READ") return "Leído";
    if (s === "DELIVERED") return "Entregado";
    return "Enviado";
  }

  function receiptStatusRank(st) {
    const s = st || "SENT";
    if (s === "READ") return 3;
    if (s === "DELIVERED") return 2;
    return 1;
  }

  async function autoDeliverAllIncomingMessages() {
    let changed = false;
    const uid = session.user.id;
    for (const [convId, list] of messagesByConversation.entries()) {
      const conv = conversations.find((c) => c.id === convId);
      for (const m of list) {
        m.recipient_id = recipientIdForMessage(m, conv);
        if (m.recipient_id !== uid) continue;
        const st = m.status || "SENT";
        if (st !== "SENT") continue;
        try {
          await postDeliveredForMessage(m);
          m.status = "DELIVERED";
          changed = true;
        } catch (_) {
          m.status = "DELIVERED";
          changed = true;
        }
      }
    }
    if (changed) messagesByConversation = new Map(messagesByConversation);
  }

  async function markConversationMessagesRead(convId) {
    const conv = conversations.find((c) => c.id === convId) || activeConversation;
    const list = messagesByConversation.get(convId) || [];
    const uid = session.user.id;
    let changed = false;
    for (const m of list) {
      m.recipient_id = recipientIdForMessage(m, conv);
      if (m.recipient_id !== uid) continue;
      let st = m.status || "SENT";
      if (st === "SENT") {
        try {
          await postDeliveredForMessage(m);
          m.status = "DELIVERED";
          st = "DELIVERED";
          changed = true;
        } catch (_) {
          m.status = "DELIVERED";
          st = "DELIVERED";
          changed = true;
        }
      }
      if (st === "DELIVERED") {
        try {
          await postReadForMessage(m);
          m.status = "READ";
          changed = true;
        } catch (_) {
          m.status = "READ";
          changed = true;
        }
      }
    }
    if (changed) messagesByConversation.set(convId, list);
  }

  function unreadCountForConversation(convId) {
    const conv = conversations.find((c) => c.id === convId);
    const list = messagesByConversation.get(convId) || [];
    const uid = session.user.id;
    let n = 0;
    for (const m of list) {
      m.recipient_id = recipientIdForMessage(m, conv);
      if (m.recipient_id !== uid) continue;
      if ((m.status || "SENT") !== "READ") n++;
    }
    return n;
  }

  async function pingHeartbeat() {
    try {
      await api("/presence/heartbeat", {
        method: "POST",
        body: JSON.stringify({ user_id: session.user.id }),
      });
    } catch (_) {}
  }

  function renderSession() {
    const user = session.user;
    const name = user.full_name || user.email || "Usuario";
    if (profileName) profileName.textContent = name;
    
    // Obtener iniciales: primera letra de cada palabra, max 2
    const initials = name
      .split(/[^\p{L}\p{N}]+/u)
      .filter((word) => word.length > 0)
      .slice(0, 2)
      .map((word) => word[0])
      .join("")
      .toUpperCase() || "US";

    if (profileAvatar) profileAvatar.textContent = initials;

    if (btnCopyUID && user.unique_id) {
      btnCopyUID.hidden = false;
    }
  }

  async function loadProfile() {
    profile = await api(`/users/${session.user.id}`);
    session.user = { ...session.user, ...profile };
    saveSession(session);
    contactsById = new Map();
    await Promise.all(
      (profile.contacts || []).map(async (id) => {
        try {
          const p = await api(`/users/${id}`);
          contactsById.set(id, p);
        } catch (_) {
          contactsById.set(id, { id, full_name: id });
        }
      }),
    );
  }

  function renderContacts() {
    const ids = profile?.contacts || [];
    if (!ids.length) {
      contactsList.innerHTML = `<div class="item muted">No tienes contactos todavía.</div>`;
      return;
    }
    contactsList.innerHTML = ids
      .map((id) => {
        const c = contactsById.get(id) || { id };
        return `<div class="item">
          <div><strong>${c.full_name || "Contacto"}</strong></div>
          <div class="meta">Disponible para iniciar chat</div>
          <div class="row item-actions">
            <button class="btn btn-danger btn-small" data-del-contact="${id}">Eliminar</button>
          </div>
        </div>`;
      })
      .join("");
  }

  function getContactsForModal() {
    const ids = profile?.contacts || [];
    return ids.map((id) => {
      const c = contactsById.get(id) || {};
      return {
        id,
        full_name: c.full_name || "Sin nombre",
        email: c.email || "",
        unique_id: c.unique_id || "",
      };
    });
  }

  function filterContactsByQuery(list, q) {
    if (!q.trim()) return list;
    const s = q.trim().toLowerCase();
    return list.filter(
      (c) =>
        (c.full_name || "").toLowerCase().includes(s) ||
        (c.unique_id || "").toLowerCase().includes(s) ||
        (c.email || "").toLowerCase().includes(s),
    );
  }

  function openModal(mode) {
    modalMode = mode;
    groupSelectedIds.clear();
    const root = qs("modal-root");
    const heading = qs("modal-heading");
    const groupPanel = qs("modal-group-panel");
    const search = qs("modal-search");
    heading.textContent = mode === "private" ? "Nuevo chat privado" : "Nuevo grupo";
    groupPanel.classList.toggle("is-visible", mode === "group");
    search.value = "";
    qs("modal-group-name").value = "";
    root.classList.add("is-open");
    root.setAttribute("aria-hidden", "false");
    renderModalOptions();
    search.focus();
  }

  function closeModal() {
    const root = qs("modal-root");
    root.classList.remove("is-open");
    root.setAttribute("aria-hidden", "true");
  }

  function renderModalOptions() {
    const container = qs("modal-options");
    const q = qs("modal-search").value.trim();
    const list = filterContactsByQuery(getContactsForModal(), q);
    const uidReady = q.length > 0;

    let primaryHtml = "";
    if (modalMode === "private") {
      primaryHtml = `
        <button type="button" class="modal-option-primary" id="modal-primary-add" ${uidReady ? "" : "disabled"}>
          <strong>+ Añadir contacto</strong><br />
          <span class="meta">Usa el UID en la barra de búsqueda para añadirlo y abrir el chat.</span>
        </button>`;
    } else {
      primaryHtml = `
        <button type="button" class="modal-option-primary" id="modal-primary-add" ${uidReady ? "" : "disabled"}>
          <strong>+ Añadir contacto</strong><br />
          <span class="meta">Escribe un UID arriba para añadirlo a tus contactos y marcarlo para el grupo.</span>
        </button>`;
    }

    let body = "";
    if (modalMode === "private") {
      body = list
        .map(
          (c) => `
        <button type="button" class="modal-contact-row" data-open-private="${c.id}">
          <strong>${escapeHtml(c.full_name)}</strong>
          <small>UID: ${escapeHtml(c.unique_id || "—")}${c.email ? " · " + escapeHtml(c.email) : ""}</small>
        </button>`,
        )
        .join("");
    } else {
      body = list
        .map((c) => {
          const checked = groupSelectedIds.has(c.id) ? "checked" : "";
          return `
        <label class="modal-group-row">
          <input type="checkbox" data-group-member="${c.id}" ${checked} />
          <div>
            <strong>${escapeHtml(c.full_name)}</strong>
            <small>UID: ${escapeHtml(c.unique_id || "—")}</small>
          </div>
        </label>`;
        })
        .join("");
    }

    container.innerHTML = primaryHtml + body;

    const primaryBtn = qs("modal-primary-add");
    if (primaryBtn) {
      primaryBtn.onclick = async () => {
        const uid = qs("modal-search").value.trim();
        try {
          if (modalMode === "private") await addUidAndOpenPrivateChat(uid);
          else await addUidToContactsFromModal();
        } catch (e) {
          showBanner(String(e.message || e), false);
        }
      };
    }

    container.querySelectorAll("[data-open-private]").forEach((btn) => {
      btn.onclick = async () => {
        const id = btn.getAttribute("data-open-private");
        try {
          await openPrivateChatWithContactId(id);
        } catch (e) {
          showBanner(String(e.message || e), false);
        }
      };
    });

    container.querySelectorAll("input[data-group-member]").forEach((input) => {
      input.onchange = () => {
        const id = input.getAttribute("data-group-member");
        if (input.checked) groupSelectedIds.add(id);
        else groupSelectedIds.delete(id);
      };
    });
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  async function addUidAndOpenPrivateChat(uidRaw) {
    const uid = uidRaw.trim();
    if (!uid) throw new Error("Escribe un UID en la búsqueda.");
    const prev = new Set(profile.contacts || []);
    try {
      await api(`/users/${session.user.id}/contacts`, {
        method: "POST",
        body: JSON.stringify({ target_unique_id: uid }),
      });
    } catch (e) {
      const msg = String(e.message || e);
      if (!/already exists/i.test(msg)) throw e;
    }
    await loadProfile();
    let targetId = (profile.contacts || []).find((id) => !prev.has(id));
    if (!targetId) {
      for (const id of profile.contacts || []) {
        const c = contactsById.get(id);
        if (c && c.unique_id && String(c.unique_id).toLowerCase() === uid.toLowerCase()) {
          targetId = id;
          break;
        }
      }
    }
    if (!targetId) throw new Error("No se pudo resolver el contacto para abrir el chat.");
    const conv = await api("/conversations/private", {
      method: "POST",
      body: JSON.stringify({ created_by: session.user.id, participant_two: targetId }),
    });
    await loadConversations();
    closeModal();
    await setActiveConversation(conv.id);
    showBanner("Chat privado listo.");
  }

  async function addUidToContactsFromModal() {
    const uid = qs("modal-search").value.trim();
    if (!uid) throw new Error("Escribe un UID en la búsqueda.");
    try {
      await api(`/users/${session.user.id}/contacts`, {
        method: "POST",
        body: JSON.stringify({ target_unique_id: uid }),
      });
      await loadProfile();
      renderContacts();
      renderModalOptions();
      showBanner("Contacto añadido. Márcalo para incluirlo en el grupo.");
    } catch (e) {
      const msg = String(e.message || e);
      if (/already exists/i.test(msg)) {
        await loadProfile();
        renderContacts();
        renderModalOptions();
        showBanner("Ese contacto ya estaba en tu lista.");
        return;
      }
      throw e;
    }
  }

  async function openPrivateChatWithContactId(participantProfileId) {
    const conv = await api("/conversations/private", {
      method: "POST",
      body: JSON.stringify({ created_by: session.user.id, participant_two: participantProfileId }),
    });
    await loadConversations();
    closeModal();
    await setActiveConversation(conv.id);
    showBanner("Chat abierto.");
  }

  async function submitNewGroup() {
    const name = qs("modal-group-name").value.trim();
    if (!name) {
      showBanner("Indica un nombre para el grupo.", false);
      return;
    }
    const members = Array.from(groupSelectedIds);
    if (members.length === 0) {
      showBanner("Selecciona al menos un contacto para el grupo.", false);
      return;
    }
    await api("/conversations/", {
      method: "POST",
      body: JSON.stringify({
        type: "group",
        name,
        description: "",
        created_by: session.user.id,
        members,
      }),
    });
    await loadConversations();
    closeModal();
    renderConversations();
    showBanner("Grupo creado.");
  }

  function filterConversationsForCurrentUser(raw) {
    const uid = session?.user?.id;
    if (!uid) return [];
    return (raw || []).filter((c) => Array.isArray(c.members) && c.members.includes(uid));
  }

  function getOtherMemberId(conv) {
    const myId = session.user.id;
    const members = conv.members || [];
    return members.find((m) => m !== myId) || null;
  }

  function conversationDisplayName(c) {
    if (!c) return "";
    if (c.type === "group") {
      const n = (c.name || "").trim();
      return n || "Grupo";
    }
    const other = getOtherMemberId(c);
    if (!other) return "Chat privado";
    const fromContact = contactsById.get(other);
    const fromPeer = peerProfilesById.get(other);
    const name = fromContact?.full_name || fromPeer?.full_name;
    if (name && String(name).trim()) return String(name).trim();
    return "Chat privado";
  }

  async function hydratePeerProfilesForConversations() {
    const pending = new Set();
    for (const c of conversations) {
      if (c.type !== "private") continue;
      const other = getOtherMemberId(c);
      if (!other || contactsById.has(other) || peerProfilesById.has(other)) continue;
      pending.add(other);
    }
    await Promise.all(
      [...pending].map(async (id) => {
        try {
          const p = await api(`/users/${id}`);
          peerProfilesById.set(id, p);
        } catch (_) {
          peerProfilesById.set(id, { id, full_name: null });
        }
      }),
    );
  }

  async function loadConversations() {
    const raw = await api("/conversations/");
    conversations = filterConversationsForCurrentUser(raw);
    await hydratePeerProfilesForConversations();
  }

  async function loadMessagesForConversation(convId) {
    if (!convId) return [];
    const conv = conversations.find((c) => c.id === convId) || activeConversation;
    const data = await api(`/conversations/${encodeURIComponent(convId)}/messages?limit=100`);
    const list = (data.messages || []).map((m) => normalizeMessage(m, conv));
    await hydrateFilesForMessages(list);
    messagesByConversation.set(convId, list);
    return list;
  }

  function renderConversations() {
    if (!conversations.length) {
      conversationList.innerHTML = `<div class="item muted">No hay conversaciones en las que participes.</div>`;
      return;
    }
    conversationList.innerHTML = conversations
      .map((c) => {
        const active = activeConversation?.id === c.id ? "active" : "";
        const t = c.type === "group" ? "Grupo" : "Privado";
        const membersCount = (c.members || []).length;
        const unread = unreadCountForConversation(c.id);
        const unreadClass = unread > 0 ? " has-unread" : "";
        const badge = unread > 0 ? `<span class="unread-badge" title="Sin leer">${unread}</span>` : "";
        const title = escapeHtml(conversationDisplayName(c));
        return `<div class="item ${active}${unreadClass}" data-conversation="${c.id}">
          <div class="row conv-head">
            <strong>${title}</strong>
            ${badge}
          </div>
          <div class="meta">${t} · Miembros: ${membersCount}</div>
        </div>`;
      })
      .join("");
  }

  async function loadNotifications() {
    const rows = await api(`/notifications/${session.user.id}`);
    notifList.innerHTML = rows.length
      ? rows
          .map(
            (n) => `<div class="item">
              <div><strong>${n.type}</strong></div>
              <div class="meta">${n.content}</div>
              <div class="row item-actions">
                <button class="btn btn-small" data-read-notif="${n.id}">Marcar leída</button>
              </div>
            </div>`,
          )
          .join("")
      : `<div class="item muted">Sin notificaciones.</div>`;
  }

  async function refreshPresence() {
    if (!activeConversation) return;
    const other = (activeConversation.members || []).find((m) => m !== session.user.id);
    if (!other) {
      presencePill.className = "pill offline";
      presencePill.textContent = "n/a";
      return;
    }
    try {
      const p = await api(`/presence/users/${other}`);
      const online = p.activity_status === "online";
      presencePill.className = online ? "pill online" : "pill offline";
      presencePill.textContent = online ? "online" : "offline";
    } catch (_) {
      presencePill.className = "pill offline";
      presencePill.textContent = "unknown";
    }
  }

  function renderMessages() {
    if (!activeConversation) {
      messageArea.className = "message-area muted flex-grow";
      messageArea.innerHTML = `<div class="empty-state">
        <div class="empty-mark">MM</div>
        <strong>Selecciona una conversación</strong>
        <span>Cuando abras un chat, los mensajes aparecerán aquí.</span>
      </div>`;
      return;
    }
    const list = messagesByConversation.get(activeConversation.id) || [];
    if (!list.length) {
      messageArea.className = "message-area muted flex-grow";
      messageArea.innerHTML = `<div class="empty-state">
        <div class="empty-mark">...</div>
        <strong>Sin mensajes aún</strong>
        <span>Escribe abajo para empezar la conversación.</span>
      </div>`;
      return;
    }
    const uid = String(session.user.id || "").trim().toLowerCase();
    messageArea.className = "message-area flex-grow";
    messageArea.innerHTML = list
      .map((m) => {
        const out = String(m.sender_id || "").trim().toLowerCase() === uid;
        const st = m.status || "SENT";
        const stLabel = receiptStatusLabel(st);
        const meta = out ? stLabel : `Recibido · ${stLabel}`;
        const rowClass = out ? "bubble-row bubble-row--out" : "bubble-row bubble-row--in";
        const bubbleClass = out ? "bubble bubble--out" : "bubble bubble--in";
        const content = escapeHtml(m.content || "(sin contenido)");
        const fileName = m.file?.file_name || "Archivo adjunto";
        const fileHtml = m.file_id
          ? `<a class="bubble-attachment" href="${fileDownloadUrl(m.file_id)}" target="_blank" rel="noopener">📎 ${escapeHtml(fileName)}</a>`
          : "";
        return `<div class="${rowClass}">
          <div class="${bubbleClass}">
          <div>${content}</div>
          ${fileHtml}
          <div class="muted msg-status" data-msg-status="${st}">
            ${meta}
          </div>
          </div>
        </div>`;
      })
      .join("");
  }

  async function setActiveConversation(id) {
    stopReceiptPolling();
    activeConversation = conversations.find((c) => c.id === id) || null;
    chatTitle.textContent = activeConversation ? conversationDisplayName(activeConversation) : "Selecciona una conversación";
    const canDelete = !!activeConversation && activeConversation.type === "group";
    btnDeleteConversation.disabled = !canDelete;
    btnSendMessage.disabled = !activeConversation;
    if (btnAttachFile) btnAttachFile.disabled = !activeConversation;
    renderConversations();
    renderMessages();
    await refreshPresence();
    if (activeConversation) {
      await loadMessagesForConversation(activeConversation.id);
      await markConversationMessagesRead(activeConversation.id);
      await syncReceiptStatusForConversation(activeConversation.id);
      renderMessages();
      renderConversations();
      startReceiptPolling();
    }
  }

  async function deleteContact(targetId) {
    await api(`/users/${session.user.id}/contacts/${targetId}`, { method: "DELETE" });
    await loadProfile();
    renderContacts();
    showBanner("Contacto eliminado.");
  }

  async function deleteConversation() {
    if (!activeConversation) return;
    await api(`/conversations/${activeConversation.id}`, {
      method: "DELETE",
      body: JSON.stringify({ actor_id: session.user.id }),
    });
    showBanner("Conversación eliminada.");
    await loadConversations();
    await setActiveConversation(null);
  }

  async function uploadFile(file, messageId) {
    const formData = new FormData();
    formData.append("file", file);
    const params = new URLSearchParams({
      file_type: "document",
      uploader_id: session.user.id,
      message_id: messageId,
    });
    const res = await fetch(apiUrl(`/files/upload?${params.toString()}`), {
      method: "POST",
      body: formData,
    });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(body.detail || `Error subiendo archivo: HTTP ${res.status}`);
    }
    return body;
  }

  function clearPendingFile() {
    pendingFile = null;
    if (fileInput) fileInput.value = "";
    if (filePreview) filePreview.hidden = true;
    if (filePreviewName) filePreviewName.textContent = "";
  }

  async function sendMessageToApi() {
    if (!activeConversation) return;
    const content = messageInput.value.trim();
    if (!content && !pendingFile) return;

    let fileInfo = null;
    let created = null;
    if (pendingFile) {
      try {
        fileInfo = await uploadFile(pendingFile, crypto.randomUUID());
      } catch (e) {
        showBanner("Error subiendo archivo: " + (e.message || e), false);
        return;
      }
      created = await api("/messages/file", {
        method: "POST",
        body: JSON.stringify({
          conversation_id: activeConversation.id,
          sender_id: session.user.id,
          file_id: fileInfo.id,
          content: content || "Archivo adjunto",
        }),
      });
    } else {
      created = await api("/messages/", {
        method: "POST",
        body: JSON.stringify({
          conversation_id: activeConversation.id,
          sender_id: session.user.id,
          content,
        }),
      });
    }

    const saved = normalizeMessage(created.message, activeConversation);
    if (fileInfo) saved.file = fileInfo;
    const list = messagesByConversation.get(activeConversation.id) || [];
    messagesByConversation.set(activeConversation.id, [...list, saved]);
    try {
      await syncReceiptStatusForConversation(activeConversation.id);
    } catch (_) {}

    messageInput.value = "";
    clearPendingFile();
    renderMessages();
    renderConversations();
    showBanner(fileInfo ? "Mensaje con archivo enviado." : "Mensaje enviado.");
  }

  async function createNotification() {
    await api("/notifications/", {
      method: "POST",
      body: JSON.stringify({
        user_id: session.user.id,
        type: "INFO",
        content: "Notificación de prueba desde frontend",
      }),
    });
    await loadNotifications();
    showBanner("Notificación creada.");
  }

  async function markNotificationRead(id) {
    await api(`/notifications/${id}/read`, { method: "PATCH" });
    await loadNotifications();
    showBanner("Notificación marcada como leída.");
  }

  function openDeleteAccountConfirm() {
    confirmRoot.classList.add("is-open");
    confirmRoot.setAttribute("aria-hidden", "false");
    confirmDeleteAccount.focus();
  }

  function closeDeleteAccountConfirm() {
    confirmRoot.classList.remove("is-open");
    confirmRoot.setAttribute("aria-hidden", "true");
  }

  async function deleteAccount() {
    await api(`/users/${session.user.id}`, { method: "DELETE" });
    closeDeleteAccountConfirm();
    clearSession();
    showBanner("Cuenta eliminada. Redirigiendo...");
    setTimeout(() => {
      window.location.href = "/static/auth.html";
    }, 1200);
  }

  async function fullRefresh() {
    await loadProfile();
    renderSession();
    renderContacts();
    await loadConversations();
    if (activeConversation && !conversations.some((c) => c.id === activeConversation.id)) {
      activeConversation = null;
    }
    if (activeConversation) {
      await loadMessagesForConversation(activeConversation.id);
    }
    await syncReceiptStatusFromServerForAllMessages();
    await autoDeliverAllIncomingMessages();
    await pingHeartbeat();
    await loadNotifications();
    if (activeConversation) {
      await setActiveConversation(activeConversation.id);
    } else {
      renderConversations();
    }
  }

  function bindEvents() {
    qs("btnLogout").onclick = () => {
      clearSession();
      window.location.href = "/static/auth.html";
    };
    if (btnCopyUID) {
      btnCopyUID.onclick = async () => {
        if (!session || !session.user || !session.user.unique_id) return;
        try {
          await navigator.clipboard.writeText(session.user.unique_id);
          showBanner("UID copiado al portapapeles.");
        } catch (err) {
          showBanner("Tu UID es: " + session.user.unique_id);
        }
      };
    }
    qs("btnRefreshAll").onclick = async () => {
      try {
        await fullRefresh();
        showBanner("Datos actualizados.");
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
    qs("btnCreateGroup").onclick = () => openModal("group");
    qs("btnCreatePrivate").onclick = () => openModal("private");
    qs("modal-close").onclick = () => closeModal();
    qs("modal-search").oninput = () => renderModalOptions();
    qs("modal-group-submit").onclick = async () => {
      try {
        await submitNewGroup();
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
    qs("modal-root").onclick = (ev) => {
      if (ev.target === qs("modal-root")) closeModal();
    };
    document.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape" && qs("modal-root").classList.contains("is-open")) closeModal();
      if (ev.key === "Escape" && confirmRoot.classList.contains("is-open")) closeDeleteAccountConfirm();
    });
    document.addEventListener("visibilitychange", async () => {
      if (document.visibilityState !== "visible" || !activeConversation) return;
      try {
        await syncReceiptStatusForConversation(activeConversation.id);
        renderMessages();
      } catch (_) {}
    });
    qs("btnDeleteConversation").onclick = async () => {
      try {
        await deleteConversation();
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
    qs("btnSendMessage").onclick = async () => {
      try {
        await sendMessageToApi();
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
    if (btnAttachFile) {
      btnAttachFile.onclick = () => fileInput && fileInput.click();
    }
    if (fileInput) {
      fileInput.onchange = () => {
        const file = fileInput.files && fileInput.files[0];
        if (file) {
          pendingFile = file;
          if (filePreviewName) filePreviewName.textContent = "📎 " + file.name;
          if (filePreview) filePreview.hidden = false;
        }
      };
    }
    if (btnCancelFile) {
      btnCancelFile.onclick = () => clearPendingFile();
    }
    qs("btnCreateNotif").onclick = async () => {
      try {
        await createNotification();
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
    qs("btnLoadNotif").onclick = loadNotifications;
    confirmClose.onclick = closeDeleteAccountConfirm;
    confirmCancel.onclick = closeDeleteAccountConfirm;
    confirmRoot.onclick = (ev) => {
      if (ev.target === confirmRoot) closeDeleteAccountConfirm();
    };
    confirmDeleteAccount.onclick = async () => {
      try {
        await deleteAccount();
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
    qs("btnDeleteAccount").onclick = openDeleteAccountConfirm;

    contactsList.onclick = async (ev) => {
      const btn = ev.target.closest("[data-del-contact]");
      if (!btn) return;
      const targetId = btn.getAttribute("data-del-contact");
      try {
        await deleteContact(targetId);
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };

    conversationList.onclick = async (ev) => {
      const it = ev.target.closest("[data-conversation]");
      if (!it) return;
      await setActiveConversation(it.getAttribute("data-conversation"));
    };

    notifList.onclick = async (ev) => {
      const btn = ev.target.closest("[data-read-notif]");
      if (!btn) return;
      const id = btn.getAttribute("data-read-notif");
      try {
        await markNotificationRead(id);
      } catch (e) {
        showBanner(String(e.message || e), false);
      }
    };
  }

  async function init() {
    if (!requireAuth()) return;
    renderSession(); // <-- Mostrar el nombre del localStorage inmediatamente
    bindEvents();
    try {
      await fullRefresh();
      showBanner(
        "Conectado. Los estados de tus mensajes (Enviado -> Entregado -> Leído) se actualizan solos cada pocos segundos con el chat abierto.",
      );
    } catch (e) {
      if (/user profile not found/i.test(String(e.message || e))) {
        clearSession();
        window.location.href = "/static/auth.html?session=expired";
        return;
      }
      showBanner(String(e.message || e), false);
    }
  }

  init();
})();
