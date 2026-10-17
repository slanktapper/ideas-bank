"""Headless checks for the parts that are easy to break and hard to see.

Run from the project folder:  python selftest.py
No joystick and no display needed.
"""

from __future__ import annotations

import os
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["STICKWATCH_CONFIG_DIR"] = tempfile.mkdtemp(prefix="stickwatch-selftest-")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

from stickwatch import config as C
from stickwatch.devices import DeviceHub, centred, unipolar

FAILURES: list[str] = []


def check(label: str, got, want) -> None:
    ok = got == want
    print(f"{'PASS' if ok else 'FAIL'}  {label}: {got!r}" + ("" if ok else f" (want {want!r})"))
    if not ok:
        FAILURES.append(label)


class FakeStick:
    """Enough of pygame.joystick.Joystick for the hot-plug path."""

    def __init__(self, index: int):
        if index not in (0, 1):
            raise pygame.error("no such device")
        self._i = index

    def init(self): pass
    def get_instance_id(self): return 100 + self._i
    def get_guid(self): return f"guid{self._i}"
    def get_name(self): return f"Fake Stick {self._i}"
    def get_numaxes(self): return 4
    def get_axis(self, i): return 0.0


def test_deadzone() -> None:
    check("deadzone: inside reads exactly zero", centred(0.09, 0.10), 0.0)
    check("deadzone: rescales from the edge", round(centred(0.55, 0.10), 4), 0.5)
    check("deadzone: full travel reaches 1", centred(1.0, 0.10), 1.0)
    check("deadzone: sign is kept", centred(-1.0, 0.10), -1.0)
    check("throttle: idle squares off to 0", unipolar(-0.95, 0.10), 0.0)
    check("throttle: stop squares off to 1", unipolar(0.95, 0.10), 1.0)
    check("throttle: centre is half", round(unipolar(0.0, 0.10), 4), 0.5)


def test_hotplug_does_not_loop() -> None:
    """A device announcement must never trigger a subsystem rescan.

    Regression: rescan() tears down and re-inits the joystick subsystem, which
    makes SDL re-announce every device. Reacting to those announcements by
    rescanning again loops at the polling rate and drags the whole app down.
    """
    hub = DeviceHub()
    hub.start()
    rescans = [0]
    real_rescan = hub.rescan
    def counted():
        rescans[0] += 1
        real_rescan()
    hub.rescan = counted
    pygame.joystick.Joystick = FakeStick   # type: ignore[assignment]

    pygame.event.post(pygame.event.Event(pygame.JOYDEVICEADDED, device_index=0))
    check("hotplug: a new device is a change", hub.poll(), True)
    check("hotplug: it is now listed", len(hub.devices()), 1)

    # SDL re-announcing a device it already announced must be a no-op.
    for _ in range(5):
        pygame.event.post(pygame.event.Event(pygame.JOYDEVICEADDED, device_index=0))
        hub.poll()
    check("hotplug: re-announcement changes nothing", len(hub.devices()), 1)

    pygame.event.post(pygame.event.Event(pygame.JOYDEVICEADDED, device_index=1))
    hub.poll()
    check("hotplug: a second device is picked up", len(hub.devices()), 2)

    pygame.event.post(pygame.event.Event(pygame.JOYDEVICEREMOVED, instance_id=100))
    check("hotplug: removal is a change", hub.poll(), True)
    check("hotplug: it is dropped", len(hub.devices()), 1)

    for _ in range(100):
        if hub.poll():
            FAILURES.append("hotplug: idle poll reported a change")
            break
    check("hotplug: idle polling is quiet", True, True)
    check("hotplug: poll never rescans the subsystem", rescans[0], 0)
    hub.stop()


def test_config_survives_a_crash() -> None:
    """Settings must be on disk before any shutdown runs."""
    cfg = C.AppConfig()
    w = C.WidgetConfig(kind=C.KIND_RUDDER)
    w.deadzone, w.track_mm, w.x, w.y = 0.08, 140.0, 321, 654
    cfg.widgets.append(w)
    cfg.px_per_mm = 4.37
    C.save(cfg)

    back = C.load()           # as if nothing had been closed
    check("persist: widget survives", len(back.widgets), 1)
    check("persist: deadzone survives", back.widgets[0].deadzone, 0.08)
    check("persist: track length survives", back.widgets[0].track_mm, 140.0)
    check("persist: position survives", (back.widgets[0].x, back.widgets[0].y), (321, 654))
    check("persist: calibration survives", back.px_per_mm, 4.37)

    # A truncated live file must fall back to the previous good copy.
    C.config_path().write_text("{ this is not json", encoding="utf-8")
    check("persist: corrupt file falls back", len(C.load().widgets), 1)


if __name__ == "__main__":
    test_deadzone()
    test_hotplug_does_not_loop()
    test_config_survives_a_crash()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: " + ", ".join(FAILURES))
        raise SystemExit(1)
    print("all checks passed")
