"""The settings window: the ordinary window where everything is configured."""

from __future__ import annotations

import time

from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtGui import QColor, QFont, QGuiApplication, QPainter, QPen
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDoubleSpinBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QProgressBar, QPushButton, QRadioButton,
    QScrollArea, QSpinBox, QTabWidget, QVBoxLayout, QWidget,
)

from . import config as C
from .app import new_widget
from .config import (
    KIND_JOYSTICK, KIND_RUDDER, KIND_THROTTLE, SLOT_MAIN, SLOT_PITCH, SLOT_ROLL,
    AxisRef, WidgetConfig,
)

DETECT_MS = 5000
DETECT_THRESHOLD = 0.30


# -- ruler ---------------------------------------------------------------


class RulerWidget(QWidget):
    """A 100 mm bar. Hold a real ruler against it and nudge until they agree."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.px_per_mm = C.DEFAULT_PX_PER_MM
        self.setMinimumHeight(76)

    def set_scale(self, px_per_mm: float) -> None:
        self.px_per_mm = px_per_mm
        self.setMinimumWidth(int(px_per_mm * 100) + 24)
        self.update()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        x0, y0 = 12.0, 14.0
        length = self.px_per_mm * 100.0

        p.setPen(QPen(QColor(120, 120, 120), 1))
        p.setBrush(QColor(245, 245, 245))
        p.drawRect(int(x0), int(y0), int(length), 26)

        p.setPen(QPen(QColor(30, 30, 30), 1))
        f = QFont()
        f.setPixelSize(10)
        p.setFont(f)
        for cm in range(11):
            x = x0 + self.px_per_mm * 10 * cm
            tall = cm % 5 == 0
            p.drawLine(int(x), int(y0), int(x), int(y0 + (26 if tall else 13)))
            if tall:
                p.drawText(int(x) - 18, int(y0 + 52), 36, 14,
                           Qt.AlignHCenter, f"{cm} cm" if cm == 10 else f"{cm}")
        p.end()


# -- axis detection ------------------------------------------------------


class AxisDetector(QObject):
    """Watches every axis on every device and reports the one that moved."""

    detected = Signal(str, int, str, int)   # guid, ordinal, name, axis
    finished = Signal()

    def __init__(self, hub, parent=None):
        super().__init__(parent)
        self.hub = hub
        self._base: dict[tuple[str, int], list[float]] = {}
        self._timer = QTimer(self)
        self._timer.setInterval(40)
        self._timer.timeout.connect(self._step)
        self._stop = QTimer(self)
        self._stop.setSingleShot(True)
        self._stop.setInterval(DETECT_MS)
        self._stop.timeout.connect(self.cancel)

    @property
    def running(self) -> bool:
        return self._timer.isActive()

    def start(self) -> None:
        self._base = {}
        for dev in self.hub.devices():
            self._base[(dev.guid, dev.ordinal)] = self.hub.snapshot(dev)
        self._timer.start()
        self._stop.start()

    def cancel(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
            self._stop.stop()
            self.finished.emit()

    def _step(self) -> None:
        best = None
        best_delta = DETECT_THRESHOLD
        for dev in self.hub.devices():
            base = self._base.get((dev.guid, dev.ordinal))
            now = self.hub.snapshot(dev)
            if not base or len(base) != len(now):
                continue
            for i, (b, n) in enumerate(zip(base, now)):
                d = abs(n - b)
                if d > best_delta:
                    best_delta = d
                    best = (dev.guid, dev.ordinal, dev.name, i)
        if best is not None:
            self._timer.stop()
            self._stop.stop()
            self.detected.emit(*best)
            self.finished.emit()


# -- one axis assignment -------------------------------------------------


class AxisRow(QWidget):
    changed = Signal()

    def __init__(self, app, ref: AxisRef, title: str, parent=None):
        super().__init__(parent)
        self.app = app
        self.ref = ref
        self._loading = False

        self.device = QComboBox()
        self.device.setMinimumWidth(240)
        self.axis = QComboBox()
        self.axis.setMinimumWidth(90)
        self.invert = QCheckBox("Inverted")
        self.detect = QPushButton("Detect")
        self.detect.setToolTip("Click, then move the axis you want on this slot.")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(QLabel(title))
        row.addWidget(self.device, 1)
        row.addWidget(self.axis)
        row.addWidget(self.invert)
        row.addWidget(self.detect)

        self._detector = AxisDetector(app.hub, self)
        self._detector.detected.connect(self._on_detected)
        self._detector.finished.connect(self._detect_done)

        self.device.currentIndexChanged.connect(self._commit)
        self.axis.currentIndexChanged.connect(self._commit)
        self.invert.toggled.connect(self._commit)
        self.detect.clicked.connect(self._start_detect)

        self.reload()

    def reload(self) -> None:
        self._loading = True
        self.device.clear()
        self.device.addItem("— none —", None)

        devs = self.app.hub.devices()
        for d in devs:
            self.device.addItem(d.display, (d.guid, d.ordinal, d.name, d.axes))

        idx = 0
        if self.ref.assigned:
            for i in range(1, self.device.count()):
                guid, ordinal, _n, _a = self.device.itemData(i)
                if guid == self.ref.guid and ordinal == self.ref.ordinal:
                    idx = i
                    break
            else:
                # Saved device is not plugged in: keep the assignment visible
                # rather than silently dropping it.
                label = f"{self.ref.name or self.ref.guid[:8]} (not connected)"
                self.device.addItem(label, (self.ref.guid, self.ref.ordinal,
                                            self.ref.name, self.ref.axis + 1))
                idx = self.device.count() - 1
        self.device.setCurrentIndex(idx)
        self._fill_axes()
        self.invert.setChecked(self.ref.invert)
        self._loading = False

    def _fill_axes(self) -> None:
        data = self.device.currentData()
        self.axis.clear()
        if data is None:
            self.axis.setEnabled(False)
            return
        self.axis.setEnabled(True)
        count = max(1, int(data[3]))
        for i in range(count):
            self.axis.addItem(f"Axis {i}", i)
        if 0 <= self.ref.axis < count:
            self.axis.setCurrentIndex(self.ref.axis)

    def _commit(self) -> None:
        if self._loading:
            return
        if self.sender() is self.device:
            self._loading = True
            self._fill_axes()
            self._loading = False
        data = self.device.currentData()
        if data is None:
            self.ref.guid, self.ref.ordinal, self.ref.name, self.ref.axis = "", 0, "", -1
        else:
            self.ref.guid, self.ref.ordinal, self.ref.name = data[0], data[1], data[2]
            self.ref.axis = int(self.axis.currentData() or 0)
        self.ref.invert = self.invert.isChecked()
        self.changed.emit()

    def _start_detect(self) -> None:
        if self._detector.running:
            self._detector.cancel()
            return
        self.detect.setText("Move it…")
        self._detector.start()

    def _detect_done(self) -> None:
        self.detect.setText("Detect")

    def _on_detected(self, guid: str, ordinal: int, name: str, axis: int) -> None:
        self.ref.guid, self.ref.ordinal, self.ref.name, self.ref.axis = guid, ordinal, name, axis
        self.reload()
        self.changed.emit()


# -- editor for one overlay widget ---------------------------------------


class WidgetEditor(QWidget):
    changed = Signal()
    kind_changed = Signal()

    def __init__(self, app, wcfg: WidgetConfig, parent=None):
        super().__init__(parent)
        self.app = app
        self.cfg = wcfg
        self._loading = True

        form = QFormLayout(self)
        form.setLabelAlignment(Qt.AlignRight)

        self.kind = QComboBox()
        self.kind.addItem("Joystick (2 axes)", KIND_JOYSTICK)
        self.kind.addItem("Rudder", KIND_RUDDER)
        self.kind.addItem("Throttle", KIND_THROTTLE)
        self.kind.setCurrentIndex(max(0, self.kind.findData(wcfg.kind)))

        self.subkind = QComboBox()
        self.subkind.addItem("Plane", "plane")
        self.subkind.addItem("Heli (collective)", "heli")
        self.subkind.setCurrentIndex(max(0, self.subkind.findData(wcfg.subkind or "plane")))

        self.label = QLineEdit(wcfg.label)
        self.label.setPlaceholderText(wcfg.default_label())

        self.deadzone = QDoubleSpinBox()
        self.deadzone.setRange(0.0, 50.0)
        self.deadzone.setSingleStep(0.5)
        self.deadzone.setSuffix(" %")
        self.deadzone.setValue(wcfg.deadzone * 100.0)
        self.deadzone.setToolTip(
            "Inside this the readout is centred/black. Outside it, travel is "
            "rescaled so the dot leaves neutral smoothly."
        )

        form.addRow("Type", self.kind)
        self.sub_label = QLabel("Sub-type")
        form.addRow(self.sub_label, self.subkind)
        form.addRow("Label", self.label)
        form.addRow("Deadzone", self.deadzone)

        self.pos_x = QSpinBox()
        self.pos_x.setRange(0, 16000)
        self.pos_x.setValue(wcfg.x)
        self.pos_y = QSpinBox()
        self.pos_y.setRange(0, 16000)
        self.pos_y.setValue(wcfg.y)
        prow = QWidget()
        ph = QHBoxLayout(prow)
        ph.setContentsMargins(0, 0, 0, 0)
        ph.addWidget(QLabel("X"))
        ph.addWidget(self.pos_x, 1)
        ph.addWidget(QLabel("Y"))
        ph.addWidget(self.pos_y, 1)
        self.pos_x.valueChanged.connect(self._move)
        self.pos_y.valueChanged.connect(self._move)
        form.addRow("Position (px)", prow)

        # Axis slots.
        self.rows: list[AxisRow] = []
        box = QGroupBox("Axes")
        bl = QVBoxLayout(box)
        if wcfg.kind == KIND_JOYSTICK:
            specs = [(SLOT_PITCH, "Pitch (up = positive)", wcfg.pitch),
                     (SLOT_ROLL, "Roll (right = positive)", wcfg.roll)]
        else:
            specs = [(SLOT_MAIN, "Axis", wcfg.main)]
        for _slot, title, ref in specs:
            r = AxisRow(app, ref, title)
            r.changed.connect(self._emit)
            self.rows.append(r)
            bl.addWidget(r)
        form.addRow(box)

        # Size settings, per widget, all in millimetres.
        self.size_box = QGroupBox("Size (mm)")
        sform = QFormLayout(self.size_box)
        self.spins: dict[str, QDoubleSpinBox] = {}

        def spin(key: str, title: str, lo: float, hi: float, value: float, step=1.0):
            s = QDoubleSpinBox()
            s.setRange(lo, hi)
            s.setSingleStep(step)
            s.setDecimals(1)
            s.setSuffix(" mm")
            s.setValue(value)
            s.valueChanged.connect(self._emit)
            self.spins[key] = s
            sform.addRow(title, s)

        if wcfg.kind == KIND_RUDDER:
            spin("dot_mm", "Dot at centre", 2.0, 200.0, wcfg.dot_mm)
            spin("dot_max_mm", "Dot at full", 2.0, 300.0, wcfg.dot_max_mm)
            spin("track_mm", "Track length", 10.0, 600.0, wcfg.track_mm, step=5.0)
        if wcfg.kind == KIND_JOYSTICK:
            b = QSpinBox()
            b.setRange(1, 12)
            b.setValue(wcfg.boxes)
            b.valueChanged.connect(self._emit)
            self.boxes = b
            sform.addRow("Number of boxes", b)
            spin("box_step_mm", "Box spacing", 2.0, 100.0, wcfg.box_step_mm)
            spin("centre_dot_mm", "Centre dot", 0.0, 100.0, wcfg.centre_dot_mm)
            spin("cursor_mm", "Cursor", 2.0, 200.0, wcfg.cursor_mm)
        else:
            self.boxes = None
        if wcfg.kind == KIND_THROTTLE:
            spin("bar_h_mm", "Bar height", 10.0, 400.0, wcfg.bar_h_mm, step=5.0)
            spin("bar_w_mm", "Bar width", 5.0, 200.0, wcfg.bar_w_mm)
        form.addRow(self.size_box)

        self.sub_label.setVisible(wcfg.kind == KIND_THROTTLE)
        self.subkind.setVisible(wcfg.kind == KIND_THROTTLE)

        self.kind.currentIndexChanged.connect(self._on_kind)
        self.subkind.currentIndexChanged.connect(self._on_kind)
        self.label.textChanged.connect(self._emit)
        self.deadzone.valueChanged.connect(self._emit)
        self._loading = False

    def _on_kind(self) -> None:
        if self._loading:
            return
        self.cfg.kind = self.kind.currentData()
        self.cfg.subkind = self.subkind.currentData() if self.cfg.kind == KIND_THROTTLE else ""
        self.kind_changed.emit()

    def _move(self) -> None:
        if self._loading:
            return
        self.cfg.x, self.cfg.y = self.pos_x.value(), self.pos_y.value()
        self.changed.emit()

    def sync_position(self) -> None:
        """Pull the boxes back in line after a drag moved the readout."""
        self._loading = True
        self.pos_x.setValue(self.cfg.x)
        self.pos_y.setValue(self.cfg.y)
        self._loading = False

    def _emit(self) -> None:
        if self._loading:
            return
        self.cfg.label = self.label.text()
        self.cfg.deadzone = self.deadzone.value() / 100.0
        for key, s in self.spins.items():
            setattr(self.cfg, key, s.value())
        if self.boxes is not None:
            self.cfg.boxes = self.boxes.value()
        if self.cfg.dot_max_mm < self.cfg.dot_mm:
            self.cfg.dot_max_mm = self.cfg.dot_mm
        if self.cfg.track_mm < self.cfg.dot_max_mm:
            self.cfg.track_mm = self.cfg.dot_max_mm
        self.changed.emit()

    def refresh_devices(self) -> None:
        for r in self.rows:
            r.reload()


# -- main window ---------------------------------------------------------


class SettingsWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.editor: WidgetEditor | None = None
        self._loading = False
        self._last_bars = 0.0
        self.setWindowTitle("stick-watch")
        self.resize(1000, 760)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_axes_tab(), "Overlay axes")
        self.tabs.addTab(self._build_devices_tab(), "Devices")
        self.tabs.addTab(self._build_display_tab(), "Display && overlay")

        # The two controls reached for mid-session live above the tabs, where
        # they stay visible whichever tab is showing.
        root = QWidget()
        col = QVBoxLayout(root)
        col.setContentsMargins(8, 8, 8, 0)
        col.setSpacing(8)
        col.addWidget(self._build_header())
        col.addWidget(self.tabs, 1)
        self.setCentralWidget(root)

        self.reload_list()
        self.rebuild_device_panel()
        self._load_display()

    # -- header ---------------------------------------------------------

    def _build_header(self) -> QWidget:
        bar = QWidget()
        row = QHBoxLayout(bar)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self.enabled_btn = QPushButton()
        self.enabled_btn.setCheckable(True)
        self.enabled_btn.setMinimumHeight(58)
        self.enabled_btn.setCursor(Qt.PointingHandCursor)
        self.enabled_btn.toggled.connect(self._display_changed)
        row.addWidget(self.enabled_btn, 2)

        self.lock_btn = QPushButton()
        self.lock_btn.setCheckable(True)
        self.lock_btn.setMinimumHeight(58)
        self.lock_btn.setCursor(Qt.PointingHandCursor)
        self.lock_btn.toggled.connect(self._display_changed)
        row.addWidget(self.lock_btn, 3)

        self.labels_btn = QPushButton()
        self.labels_btn.setCheckable(True)
        self.labels_btn.setMinimumHeight(58)
        self.labels_btn.setCursor(Qt.PointingHandCursor)
        self.labels_btn.toggled.connect(self._display_changed)
        row.addWidget(self.labels_btn, 2)
        return bar

    def _paint_enabled_button(self) -> None:
        if self.enabled_btn.isChecked():
            self.enabled_btn.setText("OVERLAY ENABLED\nClick to disable it")
            self.enabled_btn.setStyleSheet(
                "QPushButton { background: #19525e; color: #d8f2f8; font-size: 15px;"
                " font-weight: 700; border: 2px solid #3f93a4; border-radius: 8px; }"
                "QPushButton:hover { background: #1f6472; }")
        else:
            # Deliberately alarming: if nothing is on the glass, this says why.
            self.enabled_btn.setText("OVERLAY DISABLED\nClick to enable it")
            self.enabled_btn.setStyleSheet(
                "QPushButton { background: #532626; color: #f6d5d5; font-size: 15px;"
                " font-weight: 700; border: 2px solid #9c5151; border-radius: 8px; }"
                "QPushButton:hover { background: #652e2e; }")

    def _paint_labels_button(self) -> None:
        if self.labels_btn.isChecked():
            self.labels_btn.setText("LABELS SHOWN\nClick to hide them")
            self.labels_btn.setStyleSheet(
                "QPushButton { background: #273a52; color: #dceaff; font-size: 15px;"
                " font-weight: 700; border: 2px solid #5080b4; border-radius: 8px; }"
                "QPushButton:hover { background: #2f4765; }")
        else:
            self.labels_btn.setText("LABELS HIDDEN\nClick to show them")
            self.labels_btn.setStyleSheet(
                "QPushButton { background: #33363b; color: #b6bcc4; font-size: 15px;"
                " font-weight: 700; border: 2px solid #585e66; border-radius: 8px; }"
                "QPushButton:hover { background: #3d4149; }")

    # -- tab 1 ----------------------------------------------------------

    def _build_axes_tab(self) -> QWidget:
        page = QWidget()
        outer = QHBoxLayout(page)

        left = QVBoxLayout()
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_select)
        left.addWidget(self.list, 1)

        self.add_kind = QComboBox()
        self.add_kind.addItem("Joystick (2 axes)", (KIND_JOYSTICK, ""))
        self.add_kind.addItem("Rudder", (KIND_RUDDER, ""))
        self.add_kind.addItem("Throttle — plane", (KIND_THROTTLE, "plane"))
        self.add_kind.addItem("Throttle — heli", (KIND_THROTTLE, "heli"))
        left.addWidget(self.add_kind)

        btns = QHBoxLayout()
        add = QPushButton("Add")
        add.clicked.connect(self._add)
        dup = QPushButton("Duplicate")
        dup.clicked.connect(self._duplicate)
        rem = QPushButton("Remove")
        rem.clicked.connect(self._remove)
        for b in (add, dup, rem):
            btns.addWidget(b)
        left.addLayout(btns)

        hint = QLabel(
            "The overlay starts empty. Add an axis, pick the device and axis "
            "(or hit Detect and wiggle it), then use the button above to "
            "unlock the overlay and drag it where you want."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #888;")
        left.addWidget(hint)

        lw = QWidget()
        lw.setLayout(left)
        lw.setMaximumWidth(340)
        outer.addWidget(lw)

        self.editor_area = QScrollArea()
        self.editor_area.setWidgetResizable(True)
        self.editor_area.setFrameShape(QFrame.NoFrame)
        outer.addWidget(self.editor_area, 1)
        return page

    def reload_list(self, select: int | None = None) -> None:
        self._loading = True
        current = self.list.currentRow() if select is None else select
        self.list.clear()
        for w in self.app.cfg.widgets:
            item = QListWidgetItem(w.display_label())
            item.setData(Qt.UserRole, w.id)
            self.list.addItem(item)
        self._loading = False
        if self.list.count():
            self.list.setCurrentRow(max(0, min(current, self.list.count() - 1)))
        else:
            self._set_editor(None)

    def _on_select(self, row: int) -> None:
        if self._loading:
            return
        if row < 0 or row >= len(self.app.cfg.widgets):
            self._set_editor(None)
            return
        self._set_editor(self.app.cfg.widgets[row])

    def _set_editor(self, wcfg: WidgetConfig | None) -> None:
        # QScrollArea.setWidget() destroys the widget it replaces. Changing a
        # widget's type rebuilds the editor from inside one of that editor's
        # own signal handlers, so take ownership back and defer the delete
        # instead -- otherwise Qt frees the object we are still running in.
        old = self.editor_area.takeWidget()
        if old is not None:
            old.setParent(None)
            old.deleteLater()
        if wcfg is None:
            self.editor = None
            self.editor_area.setWidget(QWidget())
            return
        ed = WidgetEditor(self.app, wcfg)
        ed.changed.connect(self._editor_changed)
        ed.kind_changed.connect(self._editor_kind_changed)
        self.editor = ed
        self.editor_area.setWidget(ed)

    def _editor_changed(self) -> None:
        row = self.list.currentRow()
        if 0 <= row < self.list.count():
            self.list.item(row).setText(self.app.cfg.widgets[row].display_label())
        self.app.touch()
        self.app.refresh_overlay()

    def _editor_kind_changed(self) -> None:
        self.app.touch(immediate=True)
        self.app.refresh_overlay()
        self.reload_list(self.list.currentRow())

    def _add(self) -> None:
        kind, sub = self.add_kind.currentData()
        w = new_widget(kind, sub)
        self.app.cfg.widgets.append(w)
        self.app.refresh_overlay()
        # New readouts join the row along the bottom centre. Adding one
        # re-tidies the row; drag them wherever you like afterwards.
        self.app.overlay.arrange_bottom_centre()
        self.app.touch(immediate=True)
        self.reload_list(len(self.app.cfg.widgets) - 1)

    def _duplicate(self) -> None:
        row = self.list.currentRow()
        if not (0 <= row < len(self.app.cfg.widgets)):
            return
        src = self.app.cfg.widgets[row]
        copy = WidgetConfig.from_dict(src.to_dict())
        copy.id = new_widget(src.kind, src.subkind).id
        copy.x, copy.y = src.x + 40, src.y + 40
        self.app.cfg.widgets.insert(row + 1, copy)
        self.app.touch(immediate=True)
        self.app.refresh_overlay()
        self.reload_list(row + 1)

    def _remove(self) -> None:
        row = self.list.currentRow()
        if not (0 <= row < len(self.app.cfg.widgets)):
            return
        del self.app.cfg.widgets[row]
        self.app.touch(immediate=True)
        self.app.refresh_overlay()
        self.reload_list(min(row, len(self.app.cfg.widgets) - 1))

    # -- tab 2 ----------------------------------------------------------

    def _build_devices_tab(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        bar = QHBoxLayout()
        rescan = QPushButton("Rescan devices")
        rescan.clicked.connect(self._rescan)
        bar.addWidget(rescan)
        bar.addStretch(1)
        v.addLayout(bar)

        self.dev_area = QScrollArea()
        self.dev_area.setWidgetResizable(True)
        v.addWidget(self.dev_area, 1)
        self._bars: list[tuple[QProgressBar, QLabel, object, int]] = []
        return page

    def _rescan(self) -> None:
        self.app.hub.rescan()
        self.on_devices_changed()

    def on_devices_changed(self) -> None:
        self.rebuild_device_panel()
        if self.editor is not None:
            self.editor.refresh_devices()

    def rebuild_device_panel(self) -> None:
        host = QWidget()
        v = QVBoxLayout(host)
        self._bars = []
        devs = self.app.hub.devices()
        if not devs:
            lab = QLabel("No joystick devices found. Plug one in and hit Rescan.")
            lab.setStyleSheet("color: #a06020;")
            v.addWidget(lab)
        for dev in devs:
            box = QGroupBox(f"{dev.display}   —   {dev.axes} axes")
            f = QFormLayout(box)
            f.addRow("GUID", QLabel(dev.guid))
            for i in range(dev.axes):
                bar = QProgressBar()
                bar.setRange(-1000, 1000)
                bar.setValue(0)
                bar.setTextVisible(False)
                val = QLabel("0.000")
                val.setMinimumWidth(60)
                row = QWidget()
                h = QHBoxLayout(row)
                h.setContentsMargins(0, 0, 0, 0)
                h.addWidget(bar, 1)
                h.addWidget(val)
                f.addRow(f"Axis {i}", row)
                self._bars.append((bar, val, dev, i))
            v.addWidget(box)
        v.addStretch(1)
        self.dev_area.setWidget(host)

    def devices_tab_live(self) -> bool:
        """True only when the axis bars are actually on screen.

        Repainting three dozen progress bars at the polling rate is not free,
        and it is pure waste while another tab is showing.
        """
        return (self.isVisible() and not self.isMinimized()
                and self.tabs.currentIndex() == 1)

    def on_tick(self) -> None:
        if not self._bars:
            return
        now = time.monotonic()
        if now - self._last_bars < 0.05:    # 20 Hz is plenty for a bar
            return
        self._last_bars = now
        cache: dict[int, list[float]] = {}
        for bar, val, dev, i in self._bars:
            vals = cache.get(dev.instance_id)
            if vals is None:
                vals = self.app.hub.snapshot(dev)
                cache[dev.instance_id] = vals
            if i < len(vals):
                scaled = int(vals[i] * 1000)
                if bar.value() != scaled:
                    bar.setValue(scaled)
                    val.setText(f"{vals[i]:+.3f}")

    # -- tab 3 ----------------------------------------------------------

    def _build_display_tab(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)

        cal = QGroupBox("Screen calibration")
        cv = QVBoxLayout(cal)
        note = QLabel(
            "Everything on the overlay is sized in millimetres. Hold a ruler "
            "against the bar below and adjust until 100 mm on the bar is "
            "100 mm on the ruler. This is saved."
        )
        note.setWordWrap(True)
        cv.addWidget(note)
        self.ruler = RulerWidget()
        cv.addWidget(self.ruler)

        rr = QHBoxLayout()
        self.ppm = QDoubleSpinBox()
        self.ppm.setRange(0.5, 40.0)
        self.ppm.setDecimals(3)
        self.ppm.setSingleStep(0.02)
        self.ppm.setSuffix(" px/mm")
        self.ppm.valueChanged.connect(self._ppm_changed)
        rr.addWidget(QLabel("Scale"))
        rr.addWidget(self.ppm)
        use_sys = QPushButton("Use what Windows reports")
        use_sys.clicked.connect(self._use_system_dpi)
        rr.addWidget(use_sys)
        rr.addStretch(1)
        cv.addLayout(rr)
        v.addWidget(cal)

        ov = QGroupBox("Overlay")
        of = QFormLayout(ov)
        self.mode_transparent = QRadioButton("Transparent, over the sim (click-through)")
        self.mode_windowed = QRadioButton("Plain window (second monitor)")
        grp = QButtonGroup(self)
        grp.addButton(self.mode_transparent)
        grp.addButton(self.mode_windowed)
        self.mode_transparent.toggled.connect(self._display_changed)
        of.addRow("Mode", self.mode_transparent)
        of.addRow("", self.mode_windowed)

        self.screen = QComboBox()
        for i, s in enumerate(QGuiApplication.screens()):
            g = s.geometry()
            self.screen.addItem(f"{i}: {s.name()}  {g.width()}x{g.height()}", i)
        self.screen.currentIndexChanged.connect(self._display_changed)
        of.addRow("Monitor", self.screen)

        self.values = QCheckBox("Show numeric values")
        self.values.toggled.connect(self._display_changed)
        of.addRow("", self.values)

        arrange = QPushButton("Arrange readouts along the bottom centre")
        arrange.clicked.connect(self._arrange)
        of.addRow("", arrange)

        self.hz = QSpinBox()
        self.hz.setRange(10, 250)
        self.hz.setSuffix(" Hz")
        self.hz.valueChanged.connect(self._display_changed)
        of.addRow("Polling rate", self.hz)
        self.measured = QLabel("measuring…")
        self.measured.setStyleSheet("color: #888;")
        of.addRow("", self.measured)
        self._rate_timer = QTimer(self)
        self._rate_timer.setInterval(1000)
        self._rate_timer.timeout.connect(self._update_rate)
        self._rate_timer.start()
        v.addWidget(ov)

        warn = QLabel(
            "While unlocked the overlay tints the whole screen, each readout "
            "shows a blue plate to grab, and a bar at the top carries a Done "
            "button. Esc locks it again too — either way your placement is kept.\n\n"
            "An overlay cannot draw over a sim running in exclusive fullscreen. "
            "Set the sim to borderless windowed, or use the plain window on a "
            "second monitor."
        )
        warn.setWordWrap(True)
        warn.setStyleSheet("color: #a06020;")
        v.addWidget(warn)

        path = QLabel(f"Settings are saved continuously to:\n{C.config_path()}")
        path.setWordWrap(True)
        path.setStyleSheet("color: #888;")
        v.addWidget(path)

        v.addStretch(1)
        quit_btn = QPushButton("Quit stick-watch")
        quit_btn.clicked.connect(self.close)
        v.addWidget(quit_btn)
        return page

    def _paint_lock_button(self) -> None:
        if self.lock_btn.isChecked():
            self.lock_btn.setText(
                "LOCKED  —  overlay ignores the mouse\n"
                "Click to unlock and move the readouts")
            self.lock_btn.setStyleSheet(
                "QPushButton { background: #24502c; color: #dff5e2; font-size: 15px;"
                " font-weight: 700; border: 2px solid #4f9a5c; border-radius: 8px; }"
                "QPushButton:hover { background: #2c6236; }")
        else:
            self.lock_btn.setText(
                "UNLOCKED  —  drag the readouts on the overlay\n"
                "Click to lock, or press Esc on the overlay")
            self.lock_btn.setStyleSheet(
                "QPushButton { background: #6a4a15; color: #ffeccc; font-size: 15px;"
                " font-weight: 700; border: 2px solid #d39a3a; border-radius: 8px; }"
                "QPushButton:hover { background: #7d581b; }")

    def sync_lock_state(self) -> None:
        """Follow a lock change made from the overlay (Esc or the Done button)."""
        self._loading = True
        self.lock_btn.setChecked(self.app.cfg.overlay_locked)
        self._loading = False
        self._paint_lock_button()

    def _arrange(self) -> None:
        self.app.overlay.arrange_bottom_centre()
        if self.editor is not None:
            self.editor.sync_position()

    def on_widget_moved(self, wid: str) -> None:
        """Keep the position boxes honest when a readout is dragged."""
        if self.editor is not None and self.editor.cfg.id == wid:
            self.editor.sync_position()

    def _update_rate(self) -> None:
        if not self.isVisible() or self.isMinimized() or self.tabs.currentIndex() != 2:
            return
        self.measured.setText(f"{self.app.measured_hz:.1f} Hz actually achieved")

    def _load_display(self) -> None:
        self._loading = True
        cfg = self.app.cfg
        self.ppm.setValue(cfg.px_per_mm)
        self.ruler.set_scale(cfg.px_per_mm)
        self.mode_transparent.setChecked(cfg.overlay_mode == "transparent")
        self.mode_windowed.setChecked(cfg.overlay_mode != "transparent")
        self.screen.setCurrentIndex(max(0, min(cfg.overlay_screen, self.screen.count() - 1)))
        self.enabled_btn.setChecked(cfg.overlay_visible)
        self.lock_btn.setChecked(cfg.overlay_locked)
        self.labels_btn.setChecked(cfg.show_labels)
        self.values.setChecked(cfg.show_values)
        self.hz.setValue(cfg.poll_hz)
        self._loading = False
        self._paint_enabled_button()
        self._paint_lock_button()
        self._paint_labels_button()

    def _ppm_changed(self, v: float) -> None:
        if self._loading:
            return
        self.app.cfg.px_per_mm = v
        self.ruler.set_scale(v)
        self.app.touch()
        self.app.refresh_overlay()

    def _use_system_dpi(self) -> None:
        screens = QGuiApplication.screens()
        idx = max(0, min(self.app.cfg.overlay_screen, len(screens) - 1))
        self.ppm.setValue(screens[idx].physicalDotsPerInch() / 25.4)

    def _display_changed(self) -> None:
        if self._loading:
            return
        cfg = self.app.cfg
        cfg.overlay_mode = "transparent" if self.mode_transparent.isChecked() else "windowed"
        cfg.overlay_screen = int(self.screen.currentData() or 0)
        cfg.overlay_visible = self.enabled_btn.isChecked()
        self._paint_enabled_button()
        cfg.overlay_locked = self.lock_btn.isChecked()
        self._paint_lock_button()
        cfg.show_labels = self.labels_btn.isChecked()
        self._paint_labels_button()
        cfg.show_values = self.values.isChecked()
        cfg.poll_hz = self.hz.value()
        self.app.touch()
        self.app.restart_poll()
        self.app.refresh_overlay(remode=True)

    # -- lifecycle ------------------------------------------------------

    def closeEvent(self, ev):
        self.app.shutdown()
        self.app.overlay.close()
        ev.accept()
