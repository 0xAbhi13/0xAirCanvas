"""
drawing_engine.py
------------------
Turns (fingertip position, gesture) pairs coming from every processed
camera frame into a smooth, low-noise stream of stroke events that the
browser's <canvas> can render directly:

    {"type": "start", "x": 0.42, "y": 0.31}
    {"type": "move",  "x": 0.43, "y": 0.30}
    {"type": "end"}

Two smoothing stages keep the line from looking shaky:
  1. An exponential moving average (EMA) filter on the raw fingertip point.
  2. A minimum-travel-distance gate so sub-pixel jitter never emits a
     "move" event at all.

This module holds no OpenCV/MediaPipe knowledge — it only knows about
normalized (0..1) points and gesture labels — so it is easy to unit test.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Optional, Tuple

from .gesture_detector import GESTURE_INDEX

Point = Tuple[float, float]


class _EmaSmoother:
    """Simple exponential moving average smoother for a 2D point."""

    def __init__(self, alpha: float = 0.35) -> None:
        self.alpha = alpha
        self._value: Optional[Point] = None

    def reset(self) -> None:
        self._value = None

    def update(self, point: Point) -> Point:
        if self._value is None:
            self._value = point
        else:
            ax = self.alpha * point[0] + (1 - self.alpha) * self._value[0]
            ay = self.alpha * point[1] + (1 - self.alpha) * self._value[1]
            self._value = (ax, ay)
        return self._value


@dataclass
class FpsCounter:
    """Rolling FPS estimate over the last N frame timestamps."""

    window: int = 30
    _timestamps: Deque[float] = field(default_factory=deque)

    def tick(self) -> float:
        now = time.time()
        self._timestamps.append(now)
        while len(self._timestamps) > self.window:
            self._timestamps.popleft()
        if len(self._timestamps) < 2:
            return 0.0
        span = self._timestamps[-1] - self._timestamps[0]
        if span <= 0:
            return 0.0
        return round((len(self._timestamps) - 1) / span, 1)


class DrawingEngine:
    """Stateful per-session engine: smooths points and emits stroke events."""

    MIN_MOVE_DISTANCE = 0.0025  # normalized units; filters sub-pixel jitter

    def __init__(self) -> None:
        self._smoother = _EmaSmoother()
        self._last_emitted: Optional[Point] = None
        self._is_drawing = False
        self.fps = FpsCounter()

    def reset_stroke(self) -> None:
        self._smoother.reset()
        self._last_emitted = None
        self._is_drawing = False

    def process(self, gesture: str, fingertip_norm: Optional[Point]) -> List[Dict]:
        """Given this frame's gesture + fingertip, return 0..N stroke events."""
        events: List[Dict] = []

        if gesture != GESTURE_INDEX or fingertip_norm is None:
            if self._is_drawing:
                events.append({"type": "end"})
            self.reset_stroke()
            return events

        smoothed = self._smoother.update(fingertip_norm)

        if not self._is_drawing:
            self._is_drawing = True
            self._last_emitted = smoothed
            events.append({"type": "start", "x": smoothed[0], "y": smoothed[1]})
            return events

        assert self._last_emitted is not None
        dx = smoothed[0] - self._last_emitted[0]
        dy = smoothed[1] - self._last_emitted[1]
        if (dx * dx + dy * dy) ** 0.5 >= self.MIN_MOVE_DISTANCE:
            self._last_emitted = smoothed
            events.append({"type": "move", "x": smoothed[0], "y": smoothed[1]})

        return events
