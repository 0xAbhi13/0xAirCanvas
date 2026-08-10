"""
0xAirCanvas — Flask application entry point.

Runs a background camera thread that performs hand tracking + gesture
classification on every frame, streams an annotated MJPEG feed to the
browser, and pushes drawing events (start / move / end / clear) to the
frontend over Server-Sent Events so the browser <canvas> can render the
actual air-writing strokes.

Created by Abhishek Jadhav (@0xAbhi13)
"""

from __future__ import annotations

import json
import os
import queue
import threading
import time
from typing import Dict, List, Optional

import cv2
import numpy as np
from flask import Flask, Response, jsonify, render_template, request

from vision.drawing_engine import DrawingEngine
from vision.gesture_detector import GESTURE_NONE, GestureDetector
from vision.hand_tracker import INDEX_TIP, HandTracker

app = Flask(__name__)

CAMERA_INDEX = 0
CAMERA_SCAN_LIMIT = 6  # how many device indices to probe when listing cameras
FRAME_WIDTH = 960
FRAME_HEIGHT = 720
JPEG_QUALITY = 85

# ---- Palette (kept in sync with static/css/style.css) ----------------------
CYAN = (255, 214, 0)     # BGR: cyan-ish accent used for HUD elements
PURPLE = (255, 90, 168)  # BGR: purple-ish accent
WHITE = (255, 255, 255)
DIM = (140, 140, 140)


class EventBroadcaster:
    """Fan-out of drawing/status events to every connected SSE client."""

    def __init__(self) -> None:
        self._subscribers: List["queue.Queue[str]"] = []
        self._lock = threading.Lock()

    def subscribe(self) -> "queue.Queue[str]":
        q: "queue.Queue[str]" = queue.Queue(maxsize=200)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: "queue.Queue[str]") -> None:
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    def publish(self, event_type: str, payload: Dict) -> None:
        message = f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"
        with self._lock:
            targets = list(self._subscribers)
        for q in targets:
            try:
                q.put_nowait(message)
            except queue.Full:
                pass  # slow client — drop the frame of data, keep the stream alive


class CameraSession:
    """Owns the webcam, the CV pipeline, and the latest annotated JPEG."""

    def __init__(self, broadcaster: EventBroadcaster) -> None:
        self._broadcaster = broadcaster
        self._lock = threading.Lock()
        self._latest_jpeg: Optional[bytes] = None
        self._status: Dict = {
            "camera": "STARTING",
            "camera_index": CAMERA_INDEX,
            "hand_detected": False,
            "gesture": GESTURE_NONE,
            "fps": 0.0,
            "error": None,
        }
        self._stop_event = threading.Event()
        self._switch_requested = threading.Event()
        self._camera_index = CAMERA_INDEX
        self._cap: Optional[cv2.VideoCapture] = None
        self._tracker = HandTracker()
        self._gestures = GestureDetector()
        self._engine = DrawingEngine()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._cap is not None:
            self._cap.release()

    def get_status(self) -> Dict:
        with self._lock:
            return dict(self._status)

    def get_jpeg(self) -> Optional[bytes]:
        with self._lock:
            return self._latest_jpeg

    def set_camera_index(self, index: int) -> None:
        """Requests a hot-swap to a different camera device, without
        tearing down the whole background thread or the hand tracker."""
        with self._lock:
            if index == self._camera_index and self._status.get("camera") == "ONLINE":
                return
            self._camera_index = index
            self._status["camera_index"] = index
            self._status["camera"] = "STARTING"
            self._status["error"] = None
        self._switch_requested.set()

    def get_camera_index(self) -> int:
        with self._lock:
            return self._camera_index

    # -- internals ------------------------------------------------------

    def _set_status(self, **kwargs) -> None:
        with self._lock:
            self._status.update(kwargs)

    def _open_camera(self) -> bool:
        index = self.get_camera_index()
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if _is_windows() else cv2.VideoCapture(index)
            if not cap.isOpened():
                cap = cv2.VideoCapture(index)
            if not cap.isOpened():
                self._set_status(
                    camera="ERROR",
                    error=f"Could not access camera {index}. Check permissions or that no other app is using it.",
                )
                return False
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
            self._cap = cap
            return True
        except Exception as exc:  # pragma: no cover
            self._set_status(camera="ERROR", error=f"Camera initialization failed: {exc}")
            return False

    def _run(self) -> None:
        if not self._tracker.available:
            self._set_status(camera="ERROR", error=self._tracker.init_error)
            self._emit_placeholder_frame(self._tracker.init_error or "MediaPipe unavailable")
            return

        # Outer loop: (re)opens the camera. A camera switch request breaks the
        # inner read loop and comes back around to open the newly selected
        # device, without restarting the tracker or the whole thread.
        while not self._stop_event.is_set():
            self._switch_requested.clear()

            if self._cap is not None:
                try:
                    self._cap.release()
                except Exception:
                    pass
                self._cap = None

            if not self._open_camera():
                self._emit_placeholder_frame(self.get_status().get("error") or "Camera unavailable")
                # Wait here until either a different camera is requested or
                # we're told to stop, instead of busy-looping on a dead device.
                while not self._stop_event.is_set() and not self._switch_requested.is_set():
                    time.sleep(0.2)
                continue

            self._set_status(camera="ONLINE", error=None, camera_index=self.get_camera_index())
            consecutive_failures = 0

            while not self._stop_event.is_set() and not self._switch_requested.is_set():
                ok, frame = self._cap.read()
                if not ok or frame is None:
                    consecutive_failures += 1
                    if consecutive_failures > 30:
                        self._set_status(camera="ERROR", error="Lost connection to the webcam.")
                        self._emit_placeholder_frame("Webcam disconnected")
                        break
                    time.sleep(0.03)
                    continue
                consecutive_failures = 0

                frame = cv2.flip(frame, 1)  # mirror for natural "write in the air" motion
                hand = self._tracker.process(frame)

                fingertip_norm = None
                if hand is not None:
                    fingertip_norm = hand.landmarks_norm[INDEX_TIP]

                gesture, clear_triggered = self._gestures.update(
                    hand.landmarks_norm if hand is not None else None
                )
                events = self._engine.process(gesture, fingertip_norm)
                if clear_triggered:
                    events.append({"type": "clear"})

                for evt in events:
                    self._broadcaster.publish("stroke", evt)

                fps = self._engine.fps.tick()
                self._set_status(
                    camera="ONLINE",
                    hand_detected=hand is not None,
                    gesture=gesture,
                    fps=fps,
                    error=None,
                )
                self._broadcaster.publish(
                    "status",
                    {
                        "camera": "ONLINE",
                        "camera_index": self.get_camera_index(),
                        "hand_detected": hand is not None,
                        "gesture": gesture,
                        "fps": fps,
                    },
                )

                annotated = self._annotate(frame, hand, gesture, fps)
                ok, buf = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
                if ok:
                    with self._lock:
                        self._latest_jpeg = buf.tobytes()

            # Inner loop ended because of stop, switch request, or a dead
            # camera. If it wasn't a clean stop, loop back around: either to
            # reopen the same device (after too many failed reads) or to open
            # the newly requested one.

        if self._cap is not None:
            try:
                self._cap.release()
            except Exception:
                pass
        self._tracker.close()

    def _annotate(self, frame: np.ndarray, hand, gesture: str, fps: float) -> np.ndarray:
        h, w = frame.shape[:2]
        overlay = frame.copy()

        # Soft corner brackets (futuristic HUD framing)
        bracket_len = 34
        margin = 18
        color = CYAN
        for (x, y, dx, dy) in [
            (margin, margin, 1, 1),
            (w - margin, margin, -1, 1),
            (margin, h - margin, 1, -1),
            (w - margin, h - margin, -1, -1),
        ]:
            cv2.line(overlay, (x, y), (x + dx * bracket_len, y), color, 2, cv2.LINE_AA)
            cv2.line(overlay, (x, y), (x, y + dy * bracket_len), color, 2, cv2.LINE_AA)

        # Faint scanning line, position derived from time for a subtle animated feel
        scan_y = int((time.time() * 60) % h)
        cv2.line(overlay, (0, scan_y), (w, scan_y), (80, 60, 0), 1, cv2.LINE_AA)

        if hand is not None:
            for (x, y) in hand.landmarks:
                cv2.circle(overlay, (x, y), 2, DIM, -1, cv2.LINE_AA)
            tip = hand.landmarks[INDEX_TIP]
            ring_color = CYAN if gesture == "DRAW" else (PURPLE if gesture == "INTERACT" else WHITE)
            cv2.circle(overlay, tip, 14, ring_color, 2, cv2.LINE_AA)
            cv2.circle(overlay, tip, 3, ring_color, -1, cv2.LINE_AA)

        frame = cv2.addWeighted(overlay, 0.85, frame, 0.15, 0)

        label = f"HAND: {'DETECTED' if hand is not None else 'NOT FOUND'}   GESTURE: {gesture}   {fps:.0f} FPS"
        cv2.putText(frame, label, (margin, h - margin // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1, cv2.LINE_AA)
        return frame

    def _emit_placeholder_frame(self, message: str) -> None:
        canvas = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
        canvas[:] = (26, 18, 10)  # deep charcoal, BGR
        cv2.putText(canvas, "CAMERA UNAVAILABLE", (60, FRAME_HEIGHT // 2 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, WHITE, 2, cv2.LINE_AA)
        wrapped = _wrap_text(message, 46)
        for i, line in enumerate(wrapped):
            cv2.putText(canvas, line, (60, FRAME_HEIGHT // 2 + 10 + i * 28),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, DIM, 1, cv2.LINE_AA)
        ok, buf = cv2.imencode(".jpg", canvas, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_QUALITY])
        if ok:
            with self._lock:
                self._latest_jpeg = buf.tobytes()
        self._broadcaster.publish("status", self.get_status())


def _wrap_text(text: str, width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _is_windows() -> bool:
    import platform
    return platform.system().lower() == "windows"


def _camera_display_name(index: int) -> str:
    """Best-effort human-readable camera name. Falls back to a generic
    label on platforms/setups where we can't look one up."""
    try:
        name_path = f"/sys/class/video4linux/video{index}/name"
        if os.path.isfile(name_path):
            with open(name_path, "r", encoding="utf-8", errors="ignore") as fh:
                name = fh.read().strip()
            if name:
                return name
    except Exception:
        pass
    return f"Camera {index}"


def _list_available_cameras(scan_limit: int, active_index: Optional[int]) -> List[Dict]:
    """Probes device indices for working cameras.

    The currently active index is reported as available without being
    re-opened, since it's already held open by the background camera
    thread (opening it a second time can fail or steal frames on many
    platforms).
    """
    cameras: List[Dict] = []
    for index in range(scan_limit):
        if active_index is not None and index == active_index:
            cameras.append({"index": index, "name": _camera_display_name(index), "active": True})
            continue

        cap = None
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW) if _is_windows() else cv2.VideoCapture(index)
            if not cap.isOpened():
                continue
            ok, _frame = cap.read()
            if ok:
                cameras.append({"index": index, "name": _camera_display_name(index), "active": False})
        except Exception:
            continue
        finally:
            if cap is not None:
                cap.release()
    return cameras


broadcaster = EventBroadcaster()
camera_session = CameraSession(broadcaster)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    def generate():
        boundary = b"--frame\r\n"
        while True:
            jpeg = camera_session.get_jpeg()
            if jpeg is None:
                time.sleep(0.05)
                continue
            yield boundary + b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
            time.sleep(1 / 60)

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/status")
def api_status():
    return jsonify(camera_session.get_status())


@app.route("/api/cameras")
def api_cameras():
    active_index = camera_session.get_camera_index()
    cameras = _list_available_cameras(CAMERA_SCAN_LIMIT, active_index)
    # Always include the active camera even if a fresh probe would have
    # skipped/missed it, so the dropdown never loses the current selection.
    if not any(c["index"] == active_index for c in cameras):
        cameras.insert(0, {"index": active_index, "name": _camera_display_name(active_index), "active": True})
    return jsonify({"cameras": cameras, "current": active_index})


@app.route("/api/camera", methods=["POST"])
def api_camera_select():
    data = request.get_json(silent=True) or {}
    index = data.get("index")
    if not isinstance(index, int) or index < 0:
        return jsonify({"error": "Invalid camera index"}), 400
    camera_session.set_camera_index(index)
    return jsonify({"ok": True, "index": index})


@app.route("/api/events")
def api_events():
    def generate():
        q = broadcaster.subscribe()
        try:
            # Send an immediate status snapshot so the UI doesn't wait for the next frame.
            yield f"event: status\ndata: {json.dumps(camera_session.get_status())}\n\n"
            while True:
                try:
                    message = q.get(timeout=15)
                    yield message
                except queue.Empty:
                    yield ": keep-alive\n\n"
        except GeneratorExit:
            pass
        finally:
            broadcaster.unsubscribe(q)

    return Response(generate(), mimetype="text/event-stream")


@app.errorhandler(404)
def not_found(_err):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(_err):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    camera_session.start()
    try:
        app.run(host="127.0.0.1", port=5000, threaded=True, debug=False)
    finally:
        camera_session.stop()
