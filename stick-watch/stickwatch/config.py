"""Configuration model and crash-safe persistence.

Deliberately free of Qt and pygame imports so it can be exercised headlessly.

Durability contract: every change the user makes is on disk within a fraction of
a second, written atomically. `save()` writes a temp file in the destination
directory, fsyncs it, then `os.replace()`s it over the real file -- a rename
within one filesystem, so a crash leaves either the whole old file or the whole
new one, never a truncated mix. A second copy (`config.prev.json`) is written
after the replace succeeds, giving a known-good fallback if the live file is
somehow unreadable. There is no write-on-close anywhere in this program.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1

# Fallback scale, overridden by the ruler calibration in the settings window.
# 24" 16:9 at 2560x1440 -> 122.4 px/in -> 4.82 px/mm.
DEFAULT_PX_PER_MM = 4.82

KIND_JOYSTICK = "joystick"
KIND_RUDDER = "rudder"
KIND_THROTTLE = "throttle"
KINDS = (KIND_JOYSTICK, KIND_RUDDER, KIND_THROTTLE)

SUBKINDS = {
    KIND_JOYSTICK: (),              # the two axes are the sub-selection
    KIND_RUDDER: (),
    KIND_THROTTLE: ("plane", "heli"),
}

SLOT_PITCH = "pitch"
SLOT_ROLL = "roll"
SLOT_MAIN = "main"


def config_dir() -> Path:
    """Per-user config directory, overridable for testing."""
    override = os.environ.get("STICKWATCH_CONFIG_DIR")
    if override:
        return Path(override)
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / "stick-watch"
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "stick-watch"


def config_path() -> Path:
    return config_dir() / "config.json"


def prev_path() -> Path:
    return config_dir() / "config.prev.json"


def _clamp(v: float, lo: float, hi: float) -> float:
    return lo if v < lo else hi if v > hi else v


@dataclass
class AxisRef:
    """Points at one axis of one physical device.

    Devices are identified by SDL GUID (stable across reboots and USB ports)
    plus an ordinal to disambiguate two identical sticks. `name` is kept only so
    the settings window can say what is missing when a device is unplugged.
    """

    guid: str = ""
    ordinal: int = 0
    name: str = ""
    axis: int = -1
    invert: bool = False

    @property
    def assigned(self) -> bool:
        return bool(self.guid) and self.axis >= 0

    def describe(self) -> str:
        if not self.assigned:
            return "unassigned"
        suffix = f" #{self.ordinal + 1}" if self.ordinal else ""
        inv = "  (inverted)" if self.invert else ""
        return f"{self.name or self.guid[:8]}{suffix}  axis {self.axis}{inv}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "guid": self.guid,
            "ordinal": self.ordinal,
            "name": self.name,
            "axis": self.axis,
            "invert": self.invert,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any] | None) -> "AxisRef":
        d = d or {}
        return cls(
            guid=str(d.get("guid", "")),
            ordinal=int(d.get("ordinal", 0)),
            name=str(d.get("name", "")),
            axis=int(d.get("axis", -1)),
            invert=bool(d.get("invert", False)),
        )


@dataclass
class WidgetConfig:
    """One readout on the overlay. Every dimension is in millimetres."""

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    kind: str = KIND_RUDDER
    subkind: str = ""
    label: str = ""
    x: int = 40
    y: int = 40
    deadzone: float = 0.05          # fraction of full travel

    # The travelling dot on the rudder slider and the heli collective.
    dot_mm: float = 9.5
    dot_max_mm: float = 30.0
    track_mm: float = 110.0         # rudder slider length, centre to centre

    # Joystick field.
    boxes: int = 4
    box_step_mm: float = 10.0       # centre to the edge of box 1, then 2x, 3x...
    centre_dot_mm: float = 3.0
    cursor_mm: float = 10.0

    # Plane throttle bar.
    bar_h_mm: float = 80.0
    bar_w_mm: float = 22.0

    pitch: AxisRef = field(default_factory=AxisRef)   # joystick vertical
    roll: AxisRef = field(default_factory=AxisRef)    # joystick horizontal
    main: AxisRef = field(default_factory=AxisRef)    # rudder / throttle

    def default_label(self) -> str:
        if self.kind == KIND_THROTTLE:
            return "Collective" if self.subkind == "heli" else "Throttle (plane)"
        return self.kind.capitalize()

    def display_label(self) -> str:
        return self.label or self.default_label()

    def refs(self) -> list[tuple[str, AxisRef]]:
        if self.kind == KIND_JOYSTICK:
            return [(SLOT_PITCH, self.pitch), (SLOT_ROLL, self.roll)]
        return [(SLOT_MAIN, self.main)]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "subkind": self.subkind,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "deadzone": self.deadzone,
            "dot_mm": self.dot_mm,
            "dot_max_mm": self.dot_max_mm,
            "track_mm": self.track_mm,
            "boxes": self.boxes,
            "box_step_mm": self.box_step_mm,
            "centre_dot_mm": self.centre_dot_mm,
            "cursor_mm": self.cursor_mm,
            "bar_h_mm": self.bar_h_mm,
            "bar_w_mm": self.bar_w_mm,
            "pitch": self.pitch.to_dict(),
            "roll": self.roll.to_dict(),
            "main": self.main.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "WidgetConfig":
        w = cls(id=str(d.get("id") or uuid.uuid4().hex[:8]))
        kind = str(d.get("kind", KIND_RUDDER))
        w.kind = kind if kind in KINDS else KIND_RUDDER
        sub = str(d.get("subkind", ""))
        allowed = SUBKINDS.get(w.kind, ())
        w.subkind = sub if sub in allowed else (allowed[0] if allowed else "")
        w.label = str(d.get("label", ""))
        w.x = int(d.get("x", 40))
        w.y = int(d.get("y", 40))
        w.deadzone = _clamp(float(d.get("deadzone", 0.05)), 0.0, 0.9)
        w.dot_mm = _clamp(float(d.get("dot_mm", 9.5)), 2.0, 200.0)
        w.dot_max_mm = _clamp(float(d.get("dot_max_mm", 30.0)), w.dot_mm, 300.0)
        w.track_mm = _clamp(float(d.get("track_mm", 110.0)), w.dot_max_mm, 600.0)
        w.boxes = int(_clamp(int(d.get("boxes", 4)), 1, 12))
        w.box_step_mm = _clamp(float(d.get("box_step_mm", 10.0)), 2.0, 100.0)
        w.centre_dot_mm = _clamp(float(d.get("centre_dot_mm", 3.0)), 0.0, 100.0)
        w.cursor_mm = _clamp(float(d.get("cursor_mm", 10.0)), 2.0, 200.0)
        w.bar_h_mm = _clamp(float(d.get("bar_h_mm", 80.0)), 10.0, 400.0)
        w.bar_w_mm = _clamp(float(d.get("bar_w_mm", 22.0)), 5.0, 200.0)
        w.pitch = AxisRef.from_dict(d.get("pitch"))
        w.roll = AxisRef.from_dict(d.get("roll"))
        w.main = AxisRef.from_dict(d.get("main"))
        return w


@dataclass
class AppConfig:
    schema: int = SCHEMA_VERSION
    px_per_mm: float = DEFAULT_PX_PER_MM
    overlay_mode: str = "transparent"   # "transparent" | "windowed"
    overlay_screen: int = 0
    overlay_locked: bool = True         # locked == click-through, no dragging
    overlay_visible: bool = True
    win_x: int = 200
    win_y: int = 200
    win_w: int = 900
    win_h: int = 600
    poll_hz: int = 60
    show_labels: bool = True
    show_values: bool = False
    widgets: list[WidgetConfig] = field(default_factory=list)

    def widget(self, wid: str) -> WidgetConfig | None:
        for w in self.widgets:
            if w.id == wid:
                return w
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": SCHEMA_VERSION,
            "saved_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "px_per_mm": self.px_per_mm,
            "overlay_mode": self.overlay_mode,
            "overlay_screen": self.overlay_screen,
            "overlay_locked": self.overlay_locked,
            "overlay_visible": self.overlay_visible,
            "win_x": self.win_x,
            "win_y": self.win_y,
            "win_w": self.win_w,
            "win_h": self.win_h,
            "poll_hz": self.poll_hz,
            "show_labels": self.show_labels,
            "show_values": self.show_values,
            "widgets": [w.to_dict() for w in self.widgets],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "AppConfig":
        c = cls()
        c.px_per_mm = _clamp(float(d.get("px_per_mm", DEFAULT_PX_PER_MM)), 0.5, 40.0)
        mode = str(d.get("overlay_mode", "transparent"))
        c.overlay_mode = mode if mode in ("transparent", "windowed") else "transparent"
        c.overlay_screen = int(d.get("overlay_screen", 0))
        c.overlay_locked = bool(d.get("overlay_locked", True))
        c.overlay_visible = bool(d.get("overlay_visible", True))
        c.win_x = int(d.get("win_x", 200))
        c.win_y = int(d.get("win_y", 200))
        c.win_w = int(d.get("win_w", 900))
        c.win_h = int(d.get("win_h", 600))
        c.poll_hz = int(_clamp(int(d.get("poll_hz", 60)), 10, 250))
        c.show_labels = bool(d.get("show_labels", True))
        c.show_values = bool(d.get("show_values", False))
        c.widgets = [WidgetConfig.from_dict(w) for w in d.get("widgets", []) if isinstance(w, dict)]
        return c


def save(cfg: AppConfig, path: Path | None = None) -> None:
    """Atomically write the config. Raises only on a genuinely broken disk."""
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(cfg.to_dict(), indent=2)

    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".config-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        tmp = ""
    finally:
        if tmp:
            try:
                os.unlink(tmp)
            except OSError:
                pass

    # Directory fsync makes the rename itself durable. No-op where unsupported.
    try:
        dfd = os.open(str(path.parent), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except (OSError, AttributeError):
        pass

    # Known-good second copy, written only once the live file is committed.
    try:
        shutil.copyfile(path, prev_path())
    except OSError:
        pass


def load(path: Path | None = None) -> AppConfig:
    """Load the config, falling back to the previous copy, then to defaults."""
    path = path or config_path()
    for candidate in (path, prev_path()):
        try:
            raw = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            data = json.loads(raw)
        except ValueError:
            # Corrupt: keep it for inspection rather than silently overwriting.
            try:
                candidate.replace(candidate.with_suffix(".corrupt.json"))
            except OSError:
                pass
            continue
        if isinstance(data, dict):
            return AppConfig.from_dict(data)
    return AppConfig()
