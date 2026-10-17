"""Application controller: owns the config, the device hub, and both windows."""

from __future__ import annotations

import time
import uuid

from PySide6.QtCore import QObject, QTimer, Slot

from . import config as C
from .config import KIND_JOYSTICK, KIND_RUDDER, KIND_THROTTLE, AppConfig, WidgetConfig
from .devices import DeviceHub, centred, unipolar
from .overlay import OverlayWindow
from .widgets import JoystickWidget, ThrottleHeliWidget, ThrottlePlaneWidget, RudderWidget

# Changes are coalesced for this long before hitting the disk. Short enough
# that a crash cannot plausibly lose a setting, long enough that dragging a
# widget does not write a file per mouse-move.
SAVE_DEBOUNCE_MS = 200


def new_widget(kind: str, subkind: str = "") -> WidgetConfig:
    """A widget with its kind's default geometry."""
    return WidgetConfig(id=uuid.uuid4().hex[:8], kind=kind, subkind=subkind)


class App(QObject):
    def __init__(self) -> None:
        super().__init__()
        self.cfg: AppConfig = C.load()
        self.hub = DeviceHub()
        self.hub.start()

        self._dirty = False
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(SAVE_DEBOUNCE_MS)
        self._save_timer.timeout.connect(self.flush)

        self.overlay = OverlayWindow(self)
        self.settings = None  # set by main(), avoids an import cycle

        self._poll = QTimer(self)
        self._poll.timeout.connect(self.tick)
        self.measured_hz = 0.0
        self._ticks = 0
        self._rate_since = time.monotonic()

    # -- persistence ----------------------------------------------------

    def touch(self, immediate: bool = False) -> None:
        """Record that the config changed. Always reaches disk promptly."""
        self._dirty = True
        if immediate:
            self.flush()
        else:
            self._save_timer.start()

    @Slot()
    def flush(self) -> None:
        if not self._dirty:
            return
        self._dirty = False
        try:
            C.save(self.cfg)
        except OSError as exc:
            self._dirty = True
            print(f"stick-watch: could not save config: {exc}")

    # -- lifecycle ------------------------------------------------------

    def start(self) -> None:
        self.overlay.rebuild(self.cfg)
        self.overlay.apply_mode(self.cfg)
        self.restart_poll()

    def restart_poll(self) -> None:
        hz = max(10, min(250, self.cfg.poll_hz))
        self._poll.start(max(4, int(round(1000.0 / hz))))

    def shutdown(self) -> None:
        self._poll.stop()
        self.flush()
        self.hub.stop()

    def refresh_overlay(self, remode: bool = False) -> None:
        self.overlay.rebuild(self.cfg)
        if remode:
            self.overlay.apply_mode(self.cfg)

    @Slot(str, int, int)
    def on_widget_moved(self, wid: str, x: int, y: int) -> None:
        w = self.cfg.widget(wid)
        if w is not None:
            w.x, w.y = x, y
            self.touch()

    # -- per-frame ------------------------------------------------------

    def values_for(self, wcfg: WidgetConfig) -> tuple[dict[str, float], bool]:
        """Processed values for one widget, plus whether a device is missing.

        A slot that was never assigned is not "missing" -- it just reads zero,
        so a joystick widget with only roll mapped still works.
        """
        out: dict[str, float] = {}
        missing = False
        assigned_any = False

        for slot, ref in wcfg.refs():
            if not ref.assigned:
                out[slot] = 0.0
                continue
            assigned_any = True
            raw = self.hub.raw(ref)
            if raw is None:
                missing = True
                out[slot] = 0.0
                continue
            if wcfg.kind == KIND_THROTTLE and wcfg.subkind == "plane":
                v = unipolar(raw, wcfg.deadzone)
            else:
                v = centred(raw, wcfg.deadzone)
            # Quantise: raw axes jitter in the last few digits, and an
            # unquantised value repaints every readout on every frame even
            # when the stick is sitting still.
            out[slot] = round(v, 3)

        return out, (missing or not assigned_any)

    @Slot()
    def tick(self) -> None:
        self._ticks += 1
        now = time.monotonic()
        if now - self._rate_since >= 1.0:
            self.measured_hz = self._ticks / (now - self._rate_since)
            self._ticks = 0
            self._rate_since = now

        if self.hub.poll() and self.settings is not None:
            self.settings.on_devices_changed()

        for wcfg in self.cfg.widgets:
            w = self.overlay.widgets.get(wcfg.id)
            if w is None:
                continue
            vals, missing = self.values_for(wcfg)
            if w.missing != missing:
                w.missing = missing
                w.update()
            if isinstance(w, JoystickWidget):
                w.set_values(vals.get("roll", 0.0), vals.get("pitch", 0.0))
            elif isinstance(w, (RudderWidget, ThrottlePlaneWidget, ThrottleHeliWidget)):
                w.set_value(vals.get("main", 0.0))

        if self.settings is not None and self.settings.devices_tab_live():
            self.settings.on_tick()
