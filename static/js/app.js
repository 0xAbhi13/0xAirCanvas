/* ==========================================================================
   0xAirCanvas — frontend
   Renders stroke events pushed from the Python hand-tracking pipeline onto
   an HTML5 canvas overlaid on the live camera feed, and drives the tool
   panel, keyboard shortcuts, toasts, and error states.
   ========================================================================== */

(() => {
  "use strict";

  // ---- DOM refs -----------------------------------------------------------
  const canvas = document.getElementById("drawCanvas");
  const ctx = canvas.getContext("2d");
  const cameraFrame = document.getElementById("cameraFrame");
  const videoFeed = document.getElementById("videoFeed");
  const cameraError = document.getElementById("cameraError");
  const cameraErrorMessage = document.getElementById("cameraErrorMessage");
  const cameraRetryBtn = document.getElementById("cameraRetryBtn");
  const cameraSelect = document.getElementById("cameraSelect");
  const cameraScanBtn = document.getElementById("cameraScanBtn");

  const fpsTag = document.getElementById("fpsTag");
  const handTag = document.getElementById("handTag");
  const gestureTag = document.getElementById("gestureTag");
  const gestureToast = document.getElementById("gestureToast");

  const systemDot = document.getElementById("systemDot");
  const systemPillText = document.getElementById("systemPillText");

  const brushToolBtn = document.getElementById("brushToolBtn");
  const eraserToolBtn = document.getElementById("eraserToolBtn");
  const brushSizeInput = document.getElementById("brushSize");
  const brushSizeLabel = document.getElementById("brushSizeLabel");
  const colorRow = document.getElementById("colorRow");

  const undoBtn = document.getElementById("undoBtn");
  const redoBtn = document.getElementById("redoBtn");
  const clearBtn = document.getElementById("clearBtn");
  const newCanvasBtn = document.getElementById("newCanvasBtn");
  const saveBtn = document.getElementById("saveBtn");

  const statCamera = document.getElementById("statCamera");
  const statHand = document.getElementById("statHand");
  const statGesture = document.getElementById("statGesture");
  const statFps = document.getElementById("statFps");
  const statBrush = document.getElementById("statBrush");

  const helpBtn = document.getElementById("helpBtn");
  const closeHelpBtn = document.getElementById("closeHelpBtn");
  const helpModal = document.getElementById("helpModal");

  const toastContainer = document.getElementById("toastContainer");

  // ---- Drawing state --------------------------------------------------------
  // History is a flat list of completed actions, replayed in order to
  // render the canvas. This makes undo/redo trivial: move a pointer and
  // replay everything up to it.
  let history = [];        // {type:'stroke', tool, color, size, points:[[nx,ny], ...]} | {type:'clear'}
  let historyPointer = -1; // index of the last applied entry
  let activeStroke = null; // in-progress stroke, pushed to history on "end"

  let currentTool = "brush";
  let currentColor = "#00e5ff";
  let currentSize = 8;

  let lastGesture = "NONE";

  function resizeCanvas() {
    const rect = cameraFrame.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.round(rect.width * dpr);
    canvas.height = Math.round(rect.height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    redraw();
  }

  window.addEventListener("resize", resizeCanvas);
  new ResizeObserver(resizeCanvas).observe(cameraFrame);

  function toPixels(nx, ny) {
    const rect = cameraFrame.getBoundingClientRect();
    return [nx * rect.width, ny * rect.height];
  }

  function drawPath(entry, uptoIndex = null) {
    if (entry.points.length === 0) return;
    ctx.save();
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.lineWidth = entry.size;
    if (entry.tool === "eraser") {
      ctx.globalCompositeOperation = "destination-out";
      ctx.strokeStyle = "rgba(0,0,0,1)";
    } else {
      ctx.globalCompositeOperation = "source-over";
      ctx.strokeStyle = entry.color;
      ctx.shadowColor = entry.color;
      ctx.shadowBlur = Math.max(4, entry.size * 0.6);
    }
    ctx.beginPath();
    const pts = uptoIndex === null ? entry.points : entry.points.slice(0, uptoIndex);
    const [sx, sy] = toPixels(pts[0][0], pts[0][1]);
    ctx.moveTo(sx, sy);
    for (let i = 1; i < pts.length; i++) {
      const [x, y] = toPixels(pts[i][0], pts[i][1]);
      ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();
  }

  function redraw() {
    const rect = cameraFrame.getBoundingClientRect();
    ctx.clearRect(0, 0, rect.width, rect.height);
    for (let i = 0; i <= historyPointer; i++) {
      const entry = history[i];
      if (entry.type === "clear") {
        ctx.clearRect(0, 0, rect.width, rect.height);
      } else if (entry.type === "stroke") {
        drawPath(entry);
      }
    }
    if (activeStroke) drawPath(activeStroke);
  }

  function pushHistory(entry) {
    history = history.slice(0, historyPointer + 1);
    history.push(entry);
    historyPointer = history.length - 1;
  }

  function startStroke(nx, ny) {
    activeStroke = { type: "stroke", tool: currentTool, color: currentColor, size: currentSize, points: [[nx, ny]] };
    redraw();
  }

  function extendStroke(nx, ny) {
    if (!activeStroke) { startStroke(nx, ny); return; }
    activeStroke.points.push([nx, ny]);
    redraw();
  }

  function endStroke() {
    if (activeStroke && activeStroke.points.length > 1) {
      pushHistory(activeStroke);
    }
    activeStroke = null;
    redraw();
  }

  function clearCanvas(showToastMsg = true) {
    pushHistory({ type: "clear" });
    redraw();
    if (showToastMsg) showToast("Canvas cleared", "success");
  }

  function newCanvas() {
    history = [];
    historyPointer = -1;
    activeStroke = null;
    redraw();
    showToast("New canvas ready", "success");
  }

  function undo() {
    if (historyPointer < 0) return;
    historyPointer -= 1;
    redraw();
  }

  function redo() {
    if (historyPointer >= history.length - 1) return;
    historyPointer += 1;
    redraw();
  }

  function saveArtwork() {
    const rect = cameraFrame.getBoundingClientRect();
    const out = document.createElement("canvas");
    out.width = rect.width;
    out.height = rect.height;
    const octx = out.getContext("2d");
    octx.fillStyle = "#05070a";
    octx.fillRect(0, 0, out.width, out.height);
    octx.drawImage(canvas, 0, 0, out.width, out.height);

    out.toBlob((blob) => {
      if (!blob) { showToast("Could not export the drawing", "error"); return; }
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `0xAirCanvas-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      showToast("Drawing saved", "success");
    }, "image/png");
  }

  // ---- Tools / colors ---------------------------------------------------

  function setTool(tool) {
    currentTool = tool;
    brushToolBtn.classList.toggle("active", tool === "brush");
    eraserToolBtn.classList.toggle("active", tool === "eraser");
    showToast(tool === "brush" ? "Brush selected" : "Eraser enabled", "success");
  }

  brushToolBtn.addEventListener("click", () => setTool("brush"));
  eraserToolBtn.addEventListener("click", () => setTool("eraser"));

  brushSizeInput.addEventListener("input", () => {
    currentSize = Number(brushSizeInput.value);
    brushSizeLabel.textContent = `${currentSize}px`;
    statBrush.textContent = `${currentSize} px`;
  });

  colorRow.addEventListener("click", (e) => {
    const swatch = e.target.closest(".swatch");
    if (!swatch) return;
    currentColor = swatch.dataset.color;
    [...colorRow.children].forEach((c) => c.classList.remove("active"));
    swatch.classList.add("active");
  });

  undoBtn.addEventListener("click", undo);
  redoBtn.addEventListener("click", redo);
  clearBtn.addEventListener("click", () => clearCanvas(true));
  newCanvasBtn.addEventListener("click", newCanvas);
  saveBtn.addEventListener("click", saveArtwork);

  // ---- Keyboard shortcuts -------------------------------------------------

  window.addEventListener("keydown", (e) => {
    if (e.target && ["INPUT", "TEXTAREA"].includes(e.target.tagName)) return;
    const key = e.key.toLowerCase();

    if (key === "escape") { closeHelp(); return; }
    if (!helpModal.classList.contains("hidden") && key !== "h") return;

    switch (key) {
      case "b": setTool("brush"); break;
      case "e": setTool("eraser"); break;
      case "c": clearCanvas(true); break;
      case "z": undo(); break;
      case "y": redo(); break;
      case "s": saveArtwork(); break;
      case "h": toggleHelp(); break;
      default: return;
    }
  });

  // ---- Help modal -----------------------------------------------------------

  function openHelp() { helpModal.classList.remove("hidden"); }
  function closeHelp() { helpModal.classList.add("hidden"); }
  function toggleHelp() { helpModal.classList.toggle("hidden"); }

  helpBtn.addEventListener("click", openHelp);
  closeHelpBtn.addEventListener("click", closeHelp);
  helpModal.addEventListener("click", (e) => { if (e.target === helpModal) closeHelp(); });

  // ---- Toasts -----------------------------------------------------------

  function showToast(message, type = "success") {
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    const icon = type === "success" ? "✓" : type === "warn" ? "⚠" : "✕";
    el.innerHTML = `<span>${icon}</span><span>${message}</span>`;
    toastContainer.appendChild(el);
    setTimeout(() => {
      el.classList.add("leaving");
      setTimeout(() => el.remove(), 240);
    }, 2600);
  }

  function flashGesture(label) {
    gestureToast.textContent = label;
    gestureToast.classList.add("show");
    clearTimeout(flashGesture._t);
    flashGesture._t = setTimeout(() => gestureToast.classList.remove("show"), 700);
  }

  // ---- Camera error handling ---------------------------------------------

  function showCameraError(message) {
    cameraErrorMessage.textContent = message || "Allow camera permission to start AirCanvas.";
    cameraError.classList.remove("hidden");
    systemDot.className = "dot dot-error";
    systemPillText.textContent = "SYSTEM ERROR";
  }

  function hideCameraError() {
    cameraError.classList.add("hidden");
    systemDot.className = "dot pulse";
    systemPillText.textContent = "SYSTEM ONLINE";
  }

  cameraRetryBtn.addEventListener("click", () => {
    videoFeed.src = `/video_feed?retry=${Date.now()}`;
    fetchStatusOnce();
  });

  videoFeed.addEventListener("error", () => {
    showCameraError("Could not reach the camera stream. Make sure the server is running.");
  });

  // ---- Camera selection ----------------------------------------------------

  let currentCameraIndex = null;
  let switchingCamera = false;

  function populateCameraSelect(cameras, current) {
    cameraSelect.innerHTML = "";
    cameras.forEach((cam) => {
      const opt = document.createElement("option");
      opt.value = String(cam.index);
      opt.textContent = cam.active ? `${cam.name} (active)` : cam.name;
      if (cam.index === current) opt.selected = true;
      cameraSelect.appendChild(opt);
    });
    currentCameraIndex = current;
  }

  async function loadCameras() {
    cameraScanBtn.classList.add("spinning");
    try {
      const res = await fetch("/api/cameras");
      const data = await res.json();
      if (Array.isArray(data.cameras) && data.cameras.length) {
        populateCameraSelect(data.cameras, data.current);
      }
    } catch (err) {
      // Leave whatever options are already there; not fatal.
    } finally {
      cameraScanBtn.classList.remove("spinning");
    }
  }

  cameraSelect.addEventListener("change", async () => {
    const index = parseInt(cameraSelect.value, 10);
    if (Number.isNaN(index) || index === currentCameraIndex) return;
    switchingCamera = true;
    cameraSelect.disabled = true;
    systemPillText.textContent = "SWITCHING CAMERA…";
    try {
      const res = await fetch("/api/camera", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ index }),
      });
      if (!res.ok) throw new Error("switch failed");
    } catch (err) {
      showCameraError("Could not switch to that camera.");
    } finally {
      cameraSelect.disabled = false;
      switchingCamera = false;
    }
  });

  cameraScanBtn.addEventListener("click", loadCameras);

  // ---- Status polling (fallback) + SSE stream -----------------------------

  function applyStatus(status) {
    const camState = status.camera || "UNKNOWN";
    statCamera.textContent = camState;
    statCamera.className = camState === "ONLINE" ? "ok" : (camState === "ERROR" ? "err" : "");

    statHand.textContent = status.hand_detected ? "DETECTED" : "NOT FOUND";
    statHand.className = status.hand_detected ? "ok" : "";

    const gesture = status.gesture || "NONE";
    statGesture.textContent = gesture;
    statGesture.className = "accent";

    if (typeof status.fps === "number") {
      statFps.textContent = status.fps.toFixed(0);
      fpsTag.textContent = `${status.fps.toFixed(0)} FPS`;
    }

    handTag.textContent = `HAND: ${status.hand_detected ? "DETECTED" : "--"}`;
    gestureTag.textContent = `GESTURE: ${gesture}`;

    if (gesture !== lastGesture) {
      if (gesture !== "NONE") flashGesture(gesture);
      if (gesture === "INTERACT" && lastGesture !== "INTERACT") {
        setTool(currentTool === "brush" ? "eraser" : "brush");
      }
      lastGesture = gesture;
    }

    if (camState === "ERROR") {
      showCameraError(status.error);
    } else if (camState === "ONLINE") {
      hideCameraError();
    }

    if (
      typeof status.camera_index === "number" &&
      status.camera_index !== currentCameraIndex &&
      !switchingCamera
    ) {
      currentCameraIndex = status.camera_index;
      if (cameraSelect.querySelector(`option[value="${status.camera_index}"]`)) {
        cameraSelect.value = String(status.camera_index);
      } else {
        loadCameras();
      }
    }
  }

  async function fetchStatusOnce() {
    try {
      const res = await fetch("/api/status");
      const data = await res.json();
      applyStatus(data);
    } catch (err) {
      showCameraError("Lost connection to the 0xAirCanvas server.");
    }
  }

  function applyStrokeEvent(evt) {
    if (evt.type === "start") startStroke(evt.x, evt.y);
    else if (evt.type === "move") extendStroke(evt.x, evt.y);
    else if (evt.type === "end") endStroke();
    else if (evt.type === "clear") clearCanvas(true);
  }

  function connectEventStream() {
    const source = new EventSource("/api/events");

    source.addEventListener("status", (e) => {
      try { applyStatus(JSON.parse(e.data)); } catch (err) { /* ignore malformed frame */ }
    });

    source.addEventListener("stroke", (e) => {
      try { applyStrokeEvent(JSON.parse(e.data)); } catch (err) { /* ignore malformed frame */ }
    });

    source.onerror = () => {
      // EventSource auto-reconnects; just fall back to polling meanwhile.
      fetchStatusOnce();
    };
  }

  // ---- Init ---------------------------------------------------------------

  function init() {
    resizeCanvas();
    fetchStatusOnce();
    loadCameras();
    connectEventStream();
    setInterval(fetchStatusOnce, 5000); // periodic reconciliation, cheap safety net
  }

  document.addEventListener("DOMContentLoaded", init);
})();
