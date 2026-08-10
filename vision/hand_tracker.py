"""
hand_tracker.py
----------------
Thin, defensive wrapper around MediaPipe Hands.

Responsible for:
  * Running hand landmark detection on a BGR frame
  * Returning pixel-space landmark coordinates for the first detected hand
  * Reporting whether the required assets could be loaded at all, so the
    rest of the app can degrade gracefully instead of crashing.
"""

from __future__ import annotations

import os
import time
import urllib.request
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np

try:
    import mediapipe as mp
    _MEDIAPIPE_AVAILABLE = True
except Exception:  # pragma: no cover - only triggered when the dependency is missing
    mp = None
    _MEDIAPIPE_AVAILABLE = False

# Recent MediaPipe builds (0.10.2x/0.10.3x on many platforms/Python versions)
# no longer ship the legacy `mediapipe.solutions` API — only the newer Tasks
# API (`mediapipe.tasks.python.vision`) is available. We detect which one we
# actually have at runtime and use whichever exists, instead of assuming the
# old `mp.solutions.hands` API is present.
_LEGACY_SOLUTIONS_AVAILABLE = bool(_MEDIAPIPE_AVAILABLE) and hasattr(mp, "solutions")

_TASKS_AVAILABLE = False
if _MEDIAPIPE_AVAILABLE and not _LEGACY_SOLUTIONS_AVAILABLE:
    try:
        from mediapipe.tasks.python import vision as mp_vision
        from mediapipe.tasks.python import BaseOptions as mp_base_options
        _TASKS_AVAILABLE = True
    except Exception:  # pragma: no cover
        _TASKS_AVAILABLE = False

# Where to cache the downloadable HandLandmarker model used by the Tasks API.
_MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
_MODEL_PATH = os.path.join(_MODEL_DIR, "hand_landmarker.task")
_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)


# Landmark indices we care about (MediaPipe's 21-point hand model).
WRIST = 0
THUMB_TIP = 4
INDEX_MCP = 5
INDEX_PIP = 6
INDEX_TIP = 8
MIDDLE_MCP = 9
MIDDLE_TIP = 12
RING_MCP = 13
RING_TIP = 16
PINKY_MCP = 17
PINKY_TIP = 20


@dataclass
class HandResult:
    """Pixel-space landmarks + a couple of convenience fields for one hand."""

    landmarks: List[Tuple[int, int]]        # 21 (x, y) pixel points
    landmarks_norm: List[Tuple[float, float]]  # 21 (x, y) normalized 0..1 points
    handedness: str                          # "Left" / "Right"
    score: float


def _ensure_model_downloaded():
    """Downloads the HandLandmarker .task model on first use, if needed.

    Returns an error string on failure, or None on success.
    """
    if os.path.isfile(_MODEL_PATH) and os.path.getsize(_MODEL_PATH) > 0:
        return None

    try:
        os.makedirs(_MODEL_DIR, exist_ok=True)
        tmp_path = _MODEL_PATH + ".part"
        urllib.request.urlretrieve(_MODEL_URL, tmp_path)
        os.replace(tmp_path, _MODEL_PATH)
        return None
    except Exception as exc:  # pragma: no cover
        return (
            f"Could not download the hand-tracking model ({exc}). "
            f"Check your internet connection, or manually download it from "
            f"{_MODEL_URL} and save it to {_MODEL_PATH}."
        )


class HandTracker:
    """Runs MediaPipe hand-landmark detection with a simple, synchronous API.

    Transparently supports two different MediaPipe backends depending on
    what's actually available in the installed `mediapipe` package:

      * Legacy `mediapipe.solutions.hands` (older mediapipe builds)
      * New `mediapipe.tasks.python.vision.HandLandmarker` (current builds,
        where `mediapipe.solutions` no longer exists)
    """

    def __init__(
        self,
        max_num_hands: int = 1,
        detection_confidence: float = 0.65,
        tracking_confidence: float = 0.6,
    ) -> None:
        self.available = _MEDIAPIPE_AVAILABLE
        self._backend = None  # "legacy" | "tasks"
        self._hands = None
        self._landmarker = None
        self.init_error = None

        if not self.available:
            self.init_error = (
                "MediaPipe is not installed or failed to import. "
                "Run 'pip install -r requirements.txt' and restart the server."
            )
            return

        if _LEGACY_SOLUTIONS_AVAILABLE:
            try:
                mp_hands = mp.solutions.hands
                self._hands = mp_hands.Hands(
                    static_image_mode=False,
                    max_num_hands=max_num_hands,
                    min_detection_confidence=detection_confidence,
                    min_tracking_confidence=tracking_confidence,
                )
                self._backend = "legacy"
                return
            except Exception as exc:  # pragma: no cover
                self.available = False
                self.init_error = f"Failed to initialize MediaPipe Hands: {exc}"
                return

        if not _TASKS_AVAILABLE:
            self.available = False
            self.init_error = (
                "This installed version of mediapipe exposes neither "
                "'mediapipe.solutions' nor the Tasks API "
                "('mediapipe.tasks.python.vision'). Try "
                "'pip install --upgrade mediapipe' and restart the server."
            )
            return

        download_error = _ensure_model_downloaded()
        if download_error:
            self.available = False
            self.init_error = download_error
            return

        try:
            base_options = mp_base_options(model_asset_path=_MODEL_PATH)
            options = mp_vision.HandLandmarkerOptions(
                base_options=base_options,
                running_mode=mp_vision.RunningMode.VIDEO,
                num_hands=max_num_hands,
                min_hand_detection_confidence=detection_confidence,
                min_hand_presence_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
            )
            self._landmarker = mp_vision.HandLandmarker.create_from_options(options)
            self._backend = "tasks"
        except Exception as exc:  # pragma: no cover
            self.available = False
            self.init_error = f"Failed to initialize MediaPipe Hands: {exc}"

    def process(self, frame_bgr: np.ndarray):
        """Runs detection on a BGR frame and returns the best hand, if any."""
        if not self.available:
            return None

        h, w = frame_bgr.shape[:2]
        frame_rgb = frame_bgr[:, :, ::-1]  # BGR -> RGB, no copy needed for read-only use
        frame_rgb = np.ascontiguousarray(frame_rgb)

        if self._backend == "legacy":
            return self._process_legacy(frame_rgb, w, h)
        if self._backend == "tasks":
            return self._process_tasks(frame_rgb, w, h)
        return None

    def _process_legacy(self, frame_rgb, w, h):
        frame_rgb.flags.writeable = False
        results = self._hands.process(frame_rgb)
        if not results.multi_hand_landmarks:
            return None

        hand_landmarks = results.multi_hand_landmarks[0]
        handedness_label = "Right"
        score = 1.0
        if results.multi_handedness:
            classification = results.multi_handedness[0].classification[0]
            handedness_label = classification.label
            score = classification.score

        pts_norm = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
        pts_px = [(int(x * w), int(y * h)) for x, y in pts_norm]

        return HandResult(
            landmarks=pts_px,
            landmarks_norm=pts_norm,
            handedness=handedness_label,
            score=float(score),
        )

    def _process_tasks(self, frame_rgb, w, h):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        timestamp_ms = int(time.time() * 1000)
        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.hand_landmarks:
            return None

        hand_landmarks = result.hand_landmarks[0]
        handedness_label = "Right"
        score = 1.0
        if result.handedness:
            category = result.handedness[0][0]
            handedness_label = category.category_name or handedness_label
            score = category.score

        pts_norm = [(lm.x, lm.y) for lm in hand_landmarks]
        pts_px = [(int(x * w), int(y * h)) for x, y in pts_norm]

        return HandResult(
            landmarks=pts_px,
            landmarks_norm=pts_norm,
            handedness=handedness_label,
            score=float(score),
        )

    def close(self) -> None:
        if self._hands is not None:
            try:
                self._hands.close()
            except Exception:
                pass
        if self._landmarker is not None:
            try:
                self._landmarker.close()
            except Exception:
                pass
