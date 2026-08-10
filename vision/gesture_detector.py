"""
gesture_detector.py
--------------------
Turns raw hand landmarks into one of four reliable gestures:

    INDEX  -> draw mode      (index finger raised, others curled)
    PALM   -> stop drawing   (all fingers extended)
    FIST   -> clear canvas   (all fingers curled, held briefly)
    PINCH  -> interaction    (thumb tip close to index tip)

Reliability over quantity: gestures are only reported once a short
confirmation window has elapsed, which avoids single noisy frames from
firing an action (especially destructive ones like CLEAR).
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import List, Tuple

from .hand_tracker import (
    INDEX_MCP,
    INDEX_PIP,
    INDEX_TIP,
    MIDDLE_MCP,
    MIDDLE_TIP,
    PINKY_MCP,
    PINKY_TIP,
    RING_MCP,
    RING_TIP,
    THUMB_TIP,
    WRIST,
)

Point = Tuple[float, float]

GESTURE_NONE = "NONE"
GESTURE_INDEX = "DRAW"
GESTURE_PALM = "STOP"
GESTURE_FIST = "CLEAR"
GESTURE_PINCH = "INTERACT"

# Debounce windows (seconds)
FIST_HOLD_SECONDS = 0.45
PINCH_HOLD_SECONDS = 0.12
GENERAL_HOLD_SECONDS = 0.05

PINCH_DISTANCE_RATIO = 0.35  # relative to palm width


def _dist(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _finger_extended(landmarks: List[Point], tip: int, pip: int, mcp: int) -> bool:
    """A finger counts as extended if its tip is farther from the wrist
    than its pip joint is (works regardless of hand rotation, unlike a
    naive y-coordinate comparison)."""
    wrist = landmarks[WRIST]
    return _dist(wrist, landmarks[tip]) > _dist(wrist, landmarks[pip]) * 1.05


def _thumb_extended(landmarks: List[Point]) -> bool:
    wrist = landmarks[WRIST]
    return _dist(wrist, landmarks[THUMB_TIP]) > _dist(wrist, landmarks[INDEX_MCP]) * 0.9


def classify_raw_gesture(landmarks: List[Point]) -> str:
    """Single-frame classification, before debouncing."""
    index_up = _finger_extended(landmarks, INDEX_TIP, INDEX_PIP, INDEX_MCP)
    middle_up = _finger_extended(landmarks, MIDDLE_TIP, INDEX_PIP, MIDDLE_MCP)
    ring_up = _finger_extended(landmarks, RING_TIP, INDEX_PIP, RING_MCP)
    pinky_up = _finger_extended(landmarks, PINKY_TIP, INDEX_PIP, PINKY_MCP)
    thumb_up = _thumb_extended(landmarks)

    palm_width = _dist(landmarks[INDEX_MCP], landmarks[PINKY_MCP]) or 1.0
    pinch_distance = _dist(landmarks[THUMB_TIP], landmarks[INDEX_TIP])

    # Pinch takes priority: thumb + index close together, other fingers curled.
    if pinch_distance < palm_width * PINCH_DISTANCE_RATIO and not middle_up:
        return GESTURE_PINCH

    if index_up and not middle_up and not ring_up and not pinky_up:
        return GESTURE_INDEX

    if index_up and middle_up and ring_up and pinky_up:
        return GESTURE_PALM

    if not index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
        return GESTURE_FIST

    return GESTURE_NONE


@dataclass
class _PendingGesture:
    label: str
    since: float


class GestureDetector:
    """Stateful classifier that debounces raw per-frame gestures."""

    def __init__(self) -> None:
        self._pending: _PendingGesture | None = None
        self._confirmed = GESTURE_NONE
        self._fist_fired_at = 0.0

    def update(self, landmarks: List[Point] | None) -> Tuple[str, bool]:
        """Feed one frame's landmarks (or None if no hand).

        Returns (gesture, clear_triggered). clear_triggered is True on the
        single frame the FIST hold-time is satisfied, so callers can react
        exactly once per fist gesture rather than every subsequent frame.
        """
        now = time.time()

        if landmarks is None:
            self._pending = None
            self._confirmed = GESTURE_NONE
            return GESTURE_NONE, False

        raw = classify_raw_gesture(landmarks)

        if self._pending is None or self._pending.label != raw:
            self._pending = _PendingGesture(label=raw, since=now)

        held_for = now - self._pending.since
        required = FIST_HOLD_SECONDS if raw == GESTURE_FIST else (
            PINCH_HOLD_SECONDS if raw == GESTURE_PINCH else GENERAL_HOLD_SECONDS
        )

        clear_triggered = False
        if held_for >= required:
            if raw != self._confirmed:
                self._confirmed = raw
                if raw == GESTURE_FIST:
                    clear_triggered = True
                    self._fist_fired_at = now
            elif raw == GESTURE_FIST and (now - self._fist_fired_at) > 1.2:
                # Allow holding the fist to clear again after a cooldown,
                # rather than only ever firing once per session.
                clear_triggered = True
                self._fist_fired_at = now

        return self._confirmed, clear_triggered
