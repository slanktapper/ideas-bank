"""The overlay window.

Two modes, switchable at runtime:

* **transparent** -- a frameless, click-through, always-on-top window covering
  one monitor. It never takes focus, so it will not pull you out of the sim.
  This works over a borderless-windowed sim; nothing can draw over a sim
  running in *exclusive* fullscreen, which is a DirectX limitation rather than
  something this program can fix.
* **windowed** -- an ordinary always-on-top window with an opaque background,
  for putting on a second monitor.

Widget positions are stored in client-area pixels and are shared between the
two modes, so a widget parked in the corner of a 2560-wide transparent canvas
is clamped back into view if you switch to a small window.
"""

from __future__ import annotations

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import QWidget

from .config import AppConfig
from .widgets import StickWidget, make_widget

BACKDROP = QColor(16, 18, 22)
UNLOCK_HINT = QColor(90, 170, 255, 190)
# While unlocked the whole canvas is tinted. This is not decoration: a
# translucent window is hit-tested per pixel on Windows, so a fully
# transparent pixel passes the click through to whatever is behind. Without
# an alpha everywhere, only the few opaque pixels of a readout are grabbable.
UNLOCK_WASH = QColor(10, 14, 20, 90)


class OverlayWindow(QWidget):
    def __init__(self, app) -> None:
        super().__init__(None)
        self.app = app
        self.widgets: dict[str, StickWidget] = {}
        self.setWindowTitle("stick-watch overlay")
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

    # -- window flags ---------------------------------------------------

    def apply_mode(self, cfg: AppConfig) -> None:
        """Rebuild window flags for the current mode and lock state."""
        was_visible = self.isVisible()
        transparent = cfg.overlay_mode == "transparent"

        flags = Qt.Window
        if transparent:
            flags |= Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint
            if cfg.overlay_locked:
                # Only refuse focus while locked. Unlocked, this is an ordinary
                # interactive window and needs to behave like one.
                flags |= Qt.WindowDoesNotAcceptFocus | Qt.WindowTransparentForInput
        else:
            flags |= Qt.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground, transparent)
        self.setAttribute(Qt.WA_NoSystemBackground, transparent)

        if transparent:
            screens = QGuiApplication.screens()
            idx = max(0, min(cfg.overlay_screen, len(screens) - 1))
            self.setGeometry(screens[idx].geometry())
        else:
            self.setGeometry(cfg.win_x, cfg.win_y, cfg.win_w, cfg.win_h)

        for w in self.widgets.values():
            w.draggable = not cfg.overlay_locked

        if cfg.overlay_visible:
            self.show()
        elif was_visible or self.isVisible():
            self.hide()
        self.update()

    # -- contents -------------------------------------------------------

    def rebuild(self, cfg: AppConfig) -> None:
        """Recreate child widgets to match the config."""
        wanted = {w.id for w in cfg.widgets}
        for wid in list(self.widgets):
            if wid not in wanted:
                self.widgets.pop(wid).deleteLater()

        for wcfg in cfg.widgets:
            existing = self.widgets.get(wcfg.id)
            kind_key = (wcfg.kind, wcfg.subkind)
            if existing is not None and getattr(existing, "_kind_key", None) != kind_key:
                existing.deleteLater()
                existing = None
            if existing is None:
                w = make_widget(wcfg, cfg.px_per_mm, self)
                w._kind_key = kind_key
                w.moved.connect(self.app.on_widget_moved)
                self.widgets[wcfg.id] = w
                w.show()
                existing = w
            existing.apply(wcfg, cfg.px_per_mm, cfg.show_labels, cfg.show_values)
            existing.draggable = not cfg.overlay_locked

        self.clamp_into_view()

    def clamp_into_view(self) -> None:
        for w in self.widgets.values():
            x = max(0, min(w.cfg.x, max(0, self.width() - w.width())))
            y = max(0, min(w.cfg.y, max(0, self.height() - w.height())))
            if (x, y) != (w.cfg.x, w.cfg.y):
                w.cfg.x, w.cfg.y = x, y
            w.move(x, y)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.clamp_into_view()
        if self.app.cfg.overlay_mode == "windowed":
            g = self.geometry()
            self.app.cfg.win_x, self.app.cfg.win_y = g.x(), g.y()
            self.app.cfg.win_w, self.app.cfg.win_h = g.width(), g.height()
            self.app.touch()

    def moveEvent(self, ev):
        super().moveEvent(ev)
        if self.app.cfg.overlay_mode == "windowed":
            g = self.geometry()
            self.app.cfg.win_x, self.app.cfg.win_y = g.x(), g.y()
            self.app.touch()

    # -- placement ------------------------------------------------------

    def arrange_bottom_centre(self, gap: int = 18, margin: int = 28) -> None:
        """Lay the readouts out in centred rows along the bottom edge.

        Readouts fill a row left to right, centred; when the next one will not
        fit, a new row starts above. Rows share a bottom edge, so a short
        readout sits level with a tall one rather than floating.
        """
        order = [self.widgets[w.id] for w in self.app.cfg.widgets
                 if w.id in self.widgets]
        if not order:
            return

        avail = max(1, self.width() - 2 * margin)
        rows: list[tuple[list, int]] = []
        run: list = []
        run_w = 0
        for w in order:
            extend = w.width() if not run else run_w + gap + w.width()
            if run and extend > avail:
                rows.append((run, run_w))
                run, run_w = [w], w.width()
            else:
                run.append(w)
                run_w = extend
        rows.append((run, run_w))

        baseline = self.height() - margin
        for row, row_w in reversed(rows):
            tallest = max(w.height() for w in row)
            top = max(0, baseline - tallest)
            x = max(0, (self.width() - row_w) // 2)
            for w in row:
                y = top + (tallest - w.height())   # bottom-align within the row
                w.cfg.x, w.cfg.y = x, y
                w.move(x, y)
                x += w.width() + gap
            baseline = top - gap
        self.app.touch(immediate=True)

    def paintEvent(self, ev):
        cfg = self.app.cfg
        p = QPainter(self)
        if cfg.overlay_mode == "windowed":
            p.fillRect(self.rect(), BACKDROP)
        if not cfg.overlay_locked:
            if cfg.overlay_mode != "windowed":
                # Gives every pixel an alpha, so clicks land on the window
                # instead of falling through it. See UNLOCK_WASH above.
                p.fillRect(self.rect(), UNLOCK_WASH)
            p.setPen(QPen(UNLOCK_HINT, 4))
            p.setBrush(Qt.NoBrush)
            p.drawRect(self.rect().adjusted(2, 2, -3, -3))
        p.end()
