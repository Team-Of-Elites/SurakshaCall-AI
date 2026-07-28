(function () {
  const DEFAULT_BASE_URL = (window.location.protocol.startsWith("http") && window.location.origin && window.location.origin !== "null") ? window.location.origin : "http://127.0.0.1:8000";
  const STORAGE_KEY = "suraksha.backendBaseUrl";
  const MAX_EVENTS = 80;

  const els = {
    backendBase: document.getElementById("backendBase"),
    saveBackend: document.getElementById("saveBackend"),
    checkHealth: document.getElementById("checkHealth"),
    healthGrid: document.getElementById("healthGrid"),
    healthSummary: document.getElementById("healthSummary"),
    connectionDot: document.getElementById("connectionDot"),
    connectionText: document.getElementById("connectionText"),
    sessionIdInput: document.getElementById("sessionIdInput"),
    loadSession: document.getElementById("loadSession"),
    createSession: document.getElementById("createSession"),
    connectSocket: document.getElementById("connectSocket"),
    startMicrophone: document.getElementById("startMicrophone"),
    analyzeNow: document.getElementById("analyzeNow"),
    resetSession: document.getElementById("resetSession"),
    endSession: document.getElementById("endSession"),
    callerNumber: document.getElementById("callerNumber"),
    direction: document.getElementById("direction"),
    displayName: document.getElementById("displayName"),
    notes: document.getElementById("notes"),
    saveCaller: document.getElementById("saveCaller"),
    riskPanel: document.getElementById("riskPanel"),
    riskLevel: document.getElementById("riskLevel"),
    riskHeadline: document.getElementById("riskHeadline"),
    riskCircle: document.getElementById("riskCircle"),
    riskScore: document.getElementById("riskScore"),
    sessionStatus: document.getElementById("sessionStatus"),
    inputMode: document.getElementById("inputMode"),
    privacyMode: document.getElementById("privacyMode"),
    llmState: document.getElementById("llmState"),
    submitState: document.getElementById("submitState"),
    transcriptText: document.getElementById("transcriptText"),
    speaker: document.getElementById("speaker"),
    language: document.getElementById("language"),
    confidence: document.getElementById("confidence"),
    submitTranscript: document.getElementById("submitTranscript"),
    insertOtpSample: document.getElementById("insertOtpSample"),
    replayState: document.getElementById("replayState"),
    replayFile: document.getElementById("replayFile"),
    replaySpeed: document.getElementById("replaySpeed"),
    startReplay: document.getElementById("startReplay"),
    pairingState: document.getElementById("pairingState"),
    pairingBox: document.getElementById("pairingBox"),
    loadPairing: document.getElementById("loadPairing"),
    copyPairing: document.getElementById("copyPairing"),
    decisionTime: document.getElementById("decisionTime"),
    decisionAction: document.getElementById("decisionAction"),
    decisionExplanation: document.getElementById("decisionExplanation"),
    transcriptCount: document.getElementById("transcriptCount"),
    transcriptList: document.getElementById("transcriptList"),
    evidenceCount: document.getElementById("evidenceCount"),
    evidenceList: document.getElementById("evidenceList"),
    eventCount: document.getElementById("eventCount"),
    eventLog: document.getElementById("eventLog"),
    toast: document.getElementById("toast")
  };

  const state = {
    baseUrl: normalizeBaseUrl(localStorage.getItem(STORAGE_KEY) || DEFAULT_BASE_URL),
    session: null,
    socket: null,
    socketState: "disconnected",
    events: [],
    transcript: [],
    evidence: [],
    risk: 0,
    level: "LOW",
    headline: "No active session.",
    decision: null,
    pairingUrl: "",
    health: null,
    heartbeatId: 0
  };

  els.backendBase.value = state.baseUrl;
  bindEvents();
  renderAll();
  checkHealth({ silent: true });

  function bindEvents() {
    els.saveBackend.addEventListener("click", saveBackendUrl);
    els.checkHealth.addEventListener("click", () => checkHealth({ silent: false }));
    els.createSession.addEventListener("click", createSession);
    els.loadSession.addEventListener("click", loadSession);
    els.connectSocket.addEventListener("click", connectDashboardSocket);
    els.startMicrophone.addEventListener("click", () => sessionAction("start-microphone", "Microphone mode started."));
    els.analyzeNow.addEventListener("click", () => sessionAction("analyze-now", "Analysis requested."));
    els.resetSession.addEventListener("click", () => sessionAction("reset", "Session reset."));
    els.endSession.addEventListener("click", () => sessionAction("end", "Session ended."));
    els.saveCaller.addEventListener("click", saveCallerMetadata);
    els.submitTranscript.addEventListener("click", submitTranscript);
    els.insertOtpSample.addEventListener("click", insertOtpSample);
    els.startReplay.addEventListener("click", startReplay);
    els.loadPairing.addEventListener("click", loadPairing);
    els.copyPairing.addEventListener("click", copyPairingUrl);
    els.sessionIdInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") loadSession();
    });
  }

  function saveBackendUrl() {
    try {
      state.baseUrl = normalizeBaseUrl(els.backendBase.value || DEFAULT_BASE_URL);
      localStorage.setItem(STORAGE_KEY, state.baseUrl);
      els.backendBase.value = state.baseUrl;
      closeSocket();
      showToast("Backend URL saved.");
      checkHealth({ silent: true });
      renderAll();
    } catch (error) {
      showError(error);
    }
  }

  async function checkHealth({ silent }) {
    try {
      const health = await request("/api/health");
      state.health = health;
      renderHealth();
      setConnection(state.socketState, health.backend === "ok" ? "Backend online" : "Backend degraded");
      if (!silent) showToast("Health refreshed.");
    } catch (error) {
      state.health = null;
      renderHealth();
      setConnection("error", "Backend unreachable");
      if (!silent) showError(error);
    }
  }

  async function createSession() {
    setButtonBusy(els.createSession, true);
    try {
      const data = await request("/api/sessions", { method: "POST" });
      applySession(data.session);
      els.sessionIdInput.value = state.session.session_id;
      showToast("Session created.");
      connectDashboardSocket();
      loadPairing();
      checkHealth({ silent: true });
    } catch (error) {
      showError(error);
    } finally {
      setButtonBusy(els.createSession, false);
    }
  }

  async function loadSession() {
    const sessionId = els.sessionIdInput.value.trim();
    if (!sessionId) {
      showToast("Enter a session ID.");
      return;
    }
    setButtonBusy(els.loadSession, true);
    try {
      const data = await request(`/api/sessions/${encodeURIComponent(sessionId)}`);
      applySession(data.session);
      showToast("Session loaded.");
      connectDashboardSocket();
      loadPairing();
    } catch (error) {
      showError(error);
    } finally {
      setButtonBusy(els.loadSession, false);
    }
  }

  async function sessionAction(action, successMessage) {
    if (!state.session) return;
    const buttonByAction = {
      "start-microphone": els.startMicrophone,
      "analyze-now": els.analyzeNow,
      reset: els.resetSession,
      end: els.endSession
    };
    const button = buttonByAction[action];
    setButtonBusy(button, true);
    try {
      const data = await request(`/api/sessions/${encodeURIComponent(state.session.session_id)}/${action}`, {
        method: "POST"
      });
      applySession(data.session);
      showToast(successMessage);
      checkHealth({ silent: true });
    } catch (error) {
      showError(error);
    } finally {
      setButtonBusy(button, false);
    }
  }

  async function saveCallerMetadata() {
    if (!state.session) return;
    setButtonBusy(els.saveCaller, true);
    try {
      const payload = {
        caller_number: nullableText(els.callerNumber.value),
        direction: els.direction.value,
        display_name: nullableText(els.displayName.value),
        notes: nullableText(els.notes.value)
      };
      const data = await request(`/api/sessions/${encodeURIComponent(state.session.session_id)}/caller-metadata`, {
        method: "POST",
        body: payload
      });
      applySession(data.session);
      showToast("Caller metadata saved.");
    } catch (error) {
      showError(error);
    } finally {
      setButtonBusy(els.saveCaller, false);
    }
  }

  async function submitTranscript() {
    if (!state.session) return;
    const text = els.transcriptText.value.trim();
    if (!text) {
      showToast("Transcript text is required.");
      return;
    }
    setButtonBusy(els.submitTranscript, true);
    els.submitState.textContent = "submitting";
    try {
      const confidenceText = els.confidence.value.trim();
      const payload = {
        text,
        speaker: els.speaker.value,
        language: nullableText(els.language.value),
        confidence: confidenceText ? Number(confidenceText) : null,
        redacted_text: null
      };
      await request(`/api/sessions/${encodeURIComponent(state.session.session_id)}/transcript-final`, {
        method: "POST",
        body: payload
      });
      els.transcriptText.value = "";
      els.submitState.textContent = "accepted";
      showToast("Transcript accepted.");
    } catch (error) {
      els.submitState.textContent = "failed";
      showError(error);
    } finally {
      setButtonBusy(els.submitTranscript, false);
    }
  }

  function insertOtpSample() {
    els.transcriptText.value = "Sir, abhi message mein jo six digit code aaya hai woh bataiye.";
    els.speaker.value = "caller";
    els.language.value = "hi-en";
    els.confidence.value = "0.94";
    els.transcriptText.focus();
  }

  async function startReplay() {
    if (!state.session) return;
    const fileName = els.replayFile.value.trim();
    if (!fileName) {
      showToast("Replay WAV file is required.");
      return;
    }
    setButtonBusy(els.startReplay, true);
    els.replayState.textContent = "starting";
    try {
      const payload = {
        file_name: fileName,
        speed: Number(els.replaySpeed.value || 1)
      };
      const data = await request(`/api/sessions/${encodeURIComponent(state.session.session_id)}/start-replay`, {
        method: "POST",
        body: payload
      });
      applySession(data.session);
      els.replayState.textContent = data.replay?.status || "started";
      showToast("Replay validated.");
    } catch (error) {
      els.replayState.textContent = "failed";
      showError(error);
    } finally {
      setButtonBusy(els.startReplay, false);
    }
  }

  async function loadPairing() {
    if (!state.session) return;
    els.pairingState.textContent = "loading";
    setButtonBusy(els.loadPairing, true);
    try {
      const data = await request(`/api/v1/sessions/${encodeURIComponent(state.session.session_id)}/qr`);
      state.pairingUrl = data.pairing_url || "";
      renderPairing(data);
      els.pairingState.textContent = "ready";
    } catch (error) {
      state.pairingUrl = "";
      renderPairing(null);
      els.pairingState.textContent = "failed";
      showError(error);
    } finally {
      setButtonBusy(els.loadPairing, false);
    }
  }

  async function copyPairingUrl() {
    if (!state.pairingUrl) return;
    try {
      await navigator.clipboard.writeText(state.pairingUrl);
      showToast("Pairing URL copied.");
    } catch {
      showToast(state.pairingUrl);
    }
  }

  function connectDashboardSocket() {
    if (!state.session) return;
    closeSocket();
    const wsUrl = `${toWsBase(state.baseUrl)}/ws/dashboard/${encodeURIComponent(state.session.session_id)}`;
    setConnection("degraded", "Connecting WebSocket");
    const socket = new WebSocket(wsUrl);
    state.socket = socket;
    state.socketState = "degraded";
    renderControls();

    socket.addEventListener("open", () => {
      state.socketState = "connected";
      setConnection("connected", "WebSocket connected");
      state.heartbeatId = window.setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "ping", sent_at: new Date().toISOString() }));
        }
      }, 20000);
      renderControls();
    });

    socket.addEventListener("close", () => {
      if (state.socket === socket) {
        state.socket = null;
        state.socketState = "disconnected";
      }
      window.clearInterval(state.heartbeatId);
      state.heartbeatId = 0;
      setConnection("degraded", "WebSocket disconnected");
      renderControls();
    });

    socket.addEventListener("error", () => {
      setConnection("error", "WebSocket error");
    });

    socket.addEventListener("message", (event) => {
      try {
        const message = JSON.parse(event.data);
        applyEvent(message);
      } catch {
        addEvent({
          type: "socket_text",
          timestamp: new Date().toISOString(),
          payload: { message: String(event.data) }
        });
      }
    });
  }

  function closeSocket() {
    window.clearInterval(state.heartbeatId);
    state.heartbeatId = 0;
    if (state.socket) {
      state.socket.close();
      state.socket = null;
    }
    state.socketState = "disconnected";
  }

  function applyEvent(event) {
    addEvent(event);
    const type = event.type;
    const payload = event.payload || {};

    if (isSessionSnapshotPayload(payload) || type === "session_snapshot" || type === "session_started" || type === "session_reset" || type === "session_ended") {
      applySession(payload);
      return;
    }

    if (type === "transcript_final") {
      addTranscript(payload);
    } else if (type === "fast_detection") {
      (payload.evidence || []).forEach(addEvidence);
    } else if (type === "tactic_detected") {
      addEvidence(payload);
    } else if (type === "risk_update" || type === "decision_update") {
      applyRiskPayload(payload);
    } else if (type === "safety_warning") {
      applyWarningPayload(payload);
    } else if (type === "identity_verified") {
      addEvidence({
        evidence_id: payload.result_id || event.event_id,
        label: `IDENTITY_${payload.status || "CHECK"}`,
        description: payload.reason || "Identity verification updated.",
        severity: payload.status === "CONTRADICTORY" ? 4 : 2,
        confidence: 1,
        source: "identity"
      });
    } else if (type === "community_match") {
      addEvidence({
        evidence_id: payload.match_id || event.event_id,
        label: payload.pattern_name || `COMMUNITY_${payload.status || "MATCH"}`,
        description: payload.reason || "Community match updated.",
        severity: payload.similarity >= 0.75 ? 4 : 2,
        confidence: payload.similarity || 0,
        source: "community"
      });
    } else if (type === "audio_status") {
      if (state.session) {
        state.session.input_mode = payload.input_mode || state.session.input_mode;
        state.session.status = payload.status === "started" ? "active" : state.session.status;
      }
      els.replayState.textContent = payload.status || "updated";
    } else if (type === "system_status" && payload.caller_metadata && state.session) {
      state.session.caller_metadata = payload.caller_metadata;
    }
    renderAll();
  }

  function applySession(session) {
    if (!session || !session.session_id) return;
    state.session = session;
    state.risk = coerceRisk(session.current_risk ?? session.risk ?? 0);
    state.level = normalizeLevel(session.risk_level || session.current_level || "LOW");
    state.transcript = dedupeById(session.recent_transcript || state.transcript, "utterance_id");
    state.evidence = dedupeById(session.evidence_events || state.evidence, "evidence_id");
    state.headline = headlineForLevel(state.level, state.risk);
    els.sessionIdInput.value = session.session_id;
    hydrateCallerForm(session);
    renderAll();
  }

  function applyRiskPayload(payload) {
    state.risk = coerceRisk(payload.risk_index ?? payload.risk ?? payload.current_risk ?? state.risk);
    state.level = normalizeLevel(payload.risk_level || payload.level || state.level);
    state.headline = payload.headline || payload.explanation || payload.reason || headlineForLevel(state.level, state.risk);
    if (payload.action || payload.explanation || payload.evidence_ids) {
      state.decision = {
        action: payload.action || payload.actions?.join(", ") || "Decision updated.",
        explanation: payload.explanation || payload.reason || state.headline,
        created_at: payload.created_at || payload.sent_at_utc || new Date().toISOString()
      };
    }
    renderAll();
  }

  function applyWarningPayload(payload) {
    state.risk = coerceRisk(payload.risk_index ?? payload.risk ?? state.risk);
    state.level = normalizeLevel(payload.risk_level || payload.level || state.level);
    state.headline = payload.headline || payload.message || headlineForLevel(state.level, state.risk);
    state.decision = {
      action: payload.message || payload.headline || "Safety warning received.",
      explanation: payload.action_code ? `Action code: ${payload.action_code}` : "Fast safety warning from backend.",
      created_at: new Date().toISOString()
    };
    renderAll();
  }

  function addTranscript(item) {
    if (!item || !item.utterance_id) return;
    state.transcript = dedupeById([...state.transcript, item], "utterance_id").slice(-24);
  }

  function addEvidence(item) {
    if (!item) return;
    const evidence = {
      evidence_id: item.evidence_id || `${item.label || "evidence"}-${Date.now()}`,
      label: item.label || "EVIDENCE",
      description: item.description || item.text || "Evidence updated.",
      severity: item.severity || 1,
      confidence: item.confidence ?? null,
      source: item.source || "backend",
      utterance_id: item.utterance_id || null,
      created_at: item.created_at || new Date().toISOString()
    };
    state.evidence = dedupeById([...state.evidence, evidence], "evidence_id").slice(-40);
  }

  function addEvent(event) {
    state.events.unshift({
      type: event.type || "unknown",
      timestamp: event.timestamp || event.sent_at_utc || new Date().toISOString(),
      sequence: event.sequence,
      payload: event.payload || {}
    });
    state.events = state.events.slice(0, MAX_EVENTS);
    renderEvents();
  }

  async function request(path, options = {}) {
    const url = `${state.baseUrl}${path}`;
    const requestOptions = {
      method: options.method || "GET",
      headers: {
        Accept: "application/json"
      }
    };
    if (options.body !== undefined) {
      requestOptions.headers["Content-Type"] = "application/json";
      requestOptions.body = JSON.stringify(options.body);
    }
    const response = await fetch(url, requestOptions);
    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json") ? await response.json() : await response.text();
    if (!response.ok) {
      const detail = typeof payload === "string" ? payload : payload.detail || JSON.stringify(payload);
      throw new Error(`${response.status} ${response.statusText}: ${detail}`);
    }
    return payload;
  }

  function renderAll() {
    renderControls();
    renderSessionSummary();
    renderRisk();
    renderTranscript();
    renderEvidence();
    renderEvents();
    renderDecision();
  }

  function renderControls() {
    const hasSession = Boolean(state.session?.session_id);
    els.connectSocket.disabled = !hasSession || state.socketState === "connected";
    els.startMicrophone.disabled = !hasSession;
    els.analyzeNow.disabled = !hasSession;
    els.resetSession.disabled = !hasSession;
    els.endSession.disabled = !hasSession;
    els.saveCaller.disabled = !hasSession;
    els.submitTranscript.disabled = !hasSession;
    els.startReplay.disabled = !hasSession;
    els.loadPairing.disabled = !hasSession;
    els.copyPairing.disabled = !state.pairingUrl;
  }

  function renderHealth() {
    const health = state.health || {};
    const values = [
      ["Backend", health.backend || "unknown"],
      ["Database", health.database || "unknown"],
      ["Whisper", health.whisper || "unknown"],
      ["LLM", health.local_llm || "unknown"],
      ["Sessions", String(health.active_sessions ?? 0)],
      ["Mode", health.mode || "unknown"]
    ];
    els.healthGrid.replaceChildren(
      ...values.map(([term, detail]) => {
        const wrapper = document.createElement("div");
        const dt = document.createElement("dt");
        const dd = document.createElement("dd");
        dt.textContent = term;
        dd.textContent = detail;
        wrapper.append(dt, dd);
        return wrapper;
      })
    );
    const clients = health.websocket_clients ? countSocketClients(health.websocket_clients) : 0;
    els.healthSummary.textContent = health.backend === "ok" ? `${health.active_sessions || 0} active, ${clients} WS clients` : "Health unknown";
  }

  function renderSessionSummary() {
    const session = state.session || {};
    els.sessionStatus.textContent = session.status || "none";
    els.inputMode.textContent = session.input_mode || "idle";
    els.privacyMode.textContent = session.privacy_status?.processing || "local";
    els.llmState.textContent = session.llm_available === true ? "available" : session.llm_available === false ? "unavailable" : "unknown";
  }

  function renderRisk() {
    const level = normalizeLevel(state.level);
    const risk = coerceRisk(state.risk);
    if (els.riskPanel) els.riskPanel.className = `risk-card level-${level.toLowerCase()}`;
    if (els.riskLevel) els.riskLevel.textContent = level;
    if (els.riskHeadline) els.riskHeadline.textContent = state.headline || headlineForLevel(level, risk);
    if (els.riskScore) els.riskScore.textContent = String(risk);
    const circumference = 314;
    if (els.riskCircle) {
      els.riskCircle.style.strokeDashoffset = String(circumference - (circumference * risk) / 100);
      els.riskCircle.style.stroke = colorForLevel(level);
    }
  }

  function renderTranscript() {
    els.transcriptCount.textContent = `${state.transcript.length} item${state.transcript.length === 1 ? "" : "s"}`;
    if (!state.transcript.length) {
      els.transcriptList.replaceChildren(emptyListItem("No transcript yet."));
      return;
    }
    els.transcriptList.replaceChildren(
      ...state.transcript.slice().reverse().map((item) => {
        const li = document.createElement("li");
        const head = document.createElement("div");
        const text = document.createElement("p");
        head.className = "item-head";
        head.append(
          pill(item.speaker || "unknown"),
          document.createTextNode(formatTime(item.created_at)),
          document.createTextNode(item.confidence != null ? `confidence ${formatPercent(item.confidence)}` : "")
        );
        text.className = "item-text";
        text.textContent = item.redacted_text || item.text || "";
        li.append(head, text);
        return li;
      })
    );
  }

  function renderEvidence() {
    els.evidenceCount.textContent = `${state.evidence.length} item${state.evidence.length === 1 ? "" : "s"}`;
    if (!state.evidence.length) {
      els.evidenceList.replaceChildren(emptyListItem("No evidence yet."));
      return;
    }
    els.evidenceList.replaceChildren(
      ...state.evidence.slice().reverse().map((item) => {
        const li = document.createElement("li");
        const head = document.createElement("div");
        const label = pill(item.label || "EVIDENCE");
        const severity = pill(`severity ${item.severity || 1}`);
        severity.classList.add(`severity-${item.severity || 1}`);
        const text = document.createElement("p");
        head.className = "item-head";
        head.append(
          label,
          severity,
          document.createTextNode(item.source || "backend"),
          document.createTextNode(item.confidence != null ? formatPercent(item.confidence) : "")
        );
        text.className = "item-text";
        text.textContent = item.description || "";
        li.append(head, text);
        return li;
      })
    );
  }

  function renderEvents() {
    els.eventCount.textContent = `${state.events.length} event${state.events.length === 1 ? "" : "s"}`;
    if (!state.events.length) {
      els.eventLog.replaceChildren(emptyListItem("No WebSocket events yet."));
      return;
    }
    els.eventLog.replaceChildren(
      ...state.events.map((event) => {
        const li = document.createElement("li");
        const type = document.createElement("div");
        const payload = document.createElement("div");
        type.className = "event-type";
        payload.className = "event-payload";
        type.textContent = `${event.sequence != null ? `#${event.sequence} ` : ""}${event.type}`;
        payload.textContent = compactJson(event.payload);
        li.append(type, payload);
        return li;
      })
    );
  }

  function renderDecision() {
    if (!state.decision) {
      els.decisionTime.textContent = "none";
      els.decisionAction.textContent = "No decision yet.";
      els.decisionExplanation.textContent = "Waiting for risk evidence.";
      return;
    }
    els.decisionTime.textContent = formatTime(state.decision.created_at);
    els.decisionAction.textContent = state.decision.action;
    els.decisionExplanation.textContent = state.decision.explanation;
  }

  function renderPairing(data) {
    els.pairingBox.replaceChildren();
    if (!data || !data.pairing_url) {
      const p = document.createElement("p");
      p.textContent = "No pairing link loaded.";
      els.pairingBox.append(p);
      els.copyPairing.disabled = true;
      return;
    }
    const link = document.createElement("a");
    link.href = data.pairing_url;
    link.target = "_blank";
    link.rel = "noreferrer";
    link.textContent = data.pairing_url;
    const ws = document.createElement("p");
    ws.textContent = data.websocket_url || "";
    els.pairingBox.append(link, ws);
    els.copyPairing.disabled = false;
  }

  function hydrateCallerForm(session) {
    const metadata = session.caller_metadata || {};
    els.callerNumber.value = metadata.caller_number || session.caller_number || "";
    els.direction.value = metadata.direction || "unknown";
    els.displayName.value = metadata.display_name || "";
    els.notes.value = metadata.notes || "";
  }

  function setConnection(kind, text) {
    state.socketState = kind === "connected" ? "connected" : state.socketState;
    els.connectionDot.className = `status-dot ${kind}`;
    els.connectionText.textContent = text;
  }

  function showToast(message) {
    els.toast.textContent = message;
    els.toast.classList.add("show");
    window.clearTimeout(showToast.timeout);
    showToast.timeout = window.setTimeout(() => {
      els.toast.classList.remove("show");
    }, 2800);
  }

  function showError(error) {
    showToast(error instanceof Error ? error.message : String(error));
  }

  function setButtonBusy(button, busy) {
    if (!button) return;
    button.disabled = busy || (!state.session && button !== els.createSession && button !== els.loadSession && button !== els.checkHealth && button !== els.saveBackend);
    button.dataset.busy = busy ? "true" : "false";
  }

  function normalizeBaseUrl(value) {
    const url = new URL(value);
    return url.origin;
  }

  function toWsBase(baseUrl) {
    return baseUrl.replace(/^http:/, "ws:").replace(/^https:/, "wss:");
  }

  function nullableText(value) {
    const text = String(value || "").trim();
    return text ? text : null;
  }

  function isSessionSnapshotPayload(payload) {
    return Boolean(payload && payload.session_id && Object.prototype.hasOwnProperty.call(payload, "current_risk"));
  }

  function coerceRisk(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) return 0;
    return Math.max(0, Math.min(100, Math.round(number)));
  }

  function normalizeLevel(value) {
    const level = String(value || "LOW").toUpperCase();
    if (level === "CAUTION") return "MEDIUM";
    if (["LOW", "MEDIUM", "HIGH", "CRITICAL"].includes(level)) return level;
    return "LOW";
  }

  function headlineForLevel(level, risk) {
    if (level === "CRITICAL") return "End the call and verify through an official channel.";
    if (level === "HIGH") return "Do not share sensitive information. Verify independently.";
    if (level === "MEDIUM") return "Risk signals detected. Continue monitoring closely.";
    return risk > 0 ? "Low risk signals detected. Continue monitoring." : "No active risk evidence.";
  }

  function colorForLevel(level) {
    if (level === "CRITICAL") return "#c53131";
    if (level === "HIGH") return "#d45b21";
    if (level === "MEDIUM") return "#b26a00";
    return "#168a4a";
  }

  function dedupeById(items, key) {
    const map = new Map();
    items.forEach((item) => {
      if (!item) return;
      const id = item[key] || JSON.stringify(item);
      map.set(id, item);
    });
    return Array.from(map.values());
  }

  function compactJson(value) {
    try {
      const json = JSON.stringify(value, null, 2);
      return json.length > 900 ? `${json.slice(0, 900)}...` : json;
    } catch {
      return String(value);
    }
  }

  function formatTime(value) {
    if (!value) return "";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "";
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }

  function formatPercent(value) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "";
    return `${Math.round(number * 100)}%`;
  }

  function countSocketClients(clientsBySession) {
    return Object.values(clientsBySession).reduce((sum, groups) => {
      return sum + Object.values(groups).reduce((inner, count) => inner + Number(count || 0), 0);
    }, 0);
  }

  function pill(text) {
    const span = document.createElement("span");
    span.className = "pill";
    span.textContent = String(text).replaceAll("_", " ");
    return span;
  }

  function emptyListItem(text) {
    const li = document.createElement("li");
    li.className = "empty-state";
    li.textContent = text;
    return li;
  }
})();
