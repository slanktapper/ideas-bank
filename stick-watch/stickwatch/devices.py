"""Joystick enumeration and axis reading, via pygame/SDL2.

Two environment variables matter and are set before pygame is imported:

* ``SDL_VIDEODRIVER=dummy`` -- we want SDL's joystick and event subsystems
  without it opening a window of its own.
* ``SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1`` -- without this SDL stops
  delivering axis motion when its window is not focused, which for an overlay
  that never takes focus means every axis reads zero.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame  # noqa: E402  (must follow the env setup above)

from .config import AxisRef


@dataclass
class DeviceInfo:
    guid: str
    ordinal: int           # nth device sharing this guid, in instance order
    name: str
    axes: int
    instance_id: int

    @property
    def display(self) -> str:
        suffix = f" #{self.ordinal + 1}" if self.ordinal else ""
        return f"{self.name}{suffix}"


class DeviceHub:
    """Owns the open SDL joysticks and hands out current axis values."""

    def __init__(self) -> None:
        self._sticks: dict[int, pygame.joystick.JoystickType] = {}
        self._infos: list[DeviceInfo] = []
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        pygame.display.init()
        pygame.joystick.init()
        self._started = True
        self.rescan()

    def stop(self) -> None:
        if not self._started:
            return
        self._sticks.clear()
        self._infos = []
        pygame.joystick.quit()
        pygame.display.quit()
        self._started = False

    # -- enumeration ----------------------------------------------------

    def _open(self, index: int) -> bool:
        """Open one device by enumeration index. True if it is new to us.

        Idempotent: SDL re-announces devices it has already announced, and
        opening one twice must not count as a change.
        """
        try:
            js = pygame.joystick.Joystick(index)
            js.init()
            iid = js.get_instance_id()
        except pygame.error:
            return False
        if iid in self._sticks:
            return False
        self._sticks[iid] = js
        return True

    def rescan(self) -> None:
        """Re-open every attached device. Only for the manual Rescan button."""
        if not self._started:
            return
        pygame.joystick.quit()
        pygame.joystick.init()
        self._sticks.clear()
        for i in range(pygame.joystick.get_count()):
            self._open(i)
        self._reindex()
        # Re-initialising the subsystem makes SDL re-announce every device.
        # Drop those: left queued, the next poll() reads them as a hot-plug
        # and rescans, which re-announces again -- a loop at the poll rate.
        pygame.event.clear()

    def _reindex(self) -> None:
        seen: dict[str, int] = {}
        infos: list[DeviceInfo] = []
        for iid in sorted(self._sticks):
            js = self._sticks[iid]
            try:
                guid = js.get_guid()
                name = js.get_name()
                axes = js.get_numaxes()
            except pygame.error:
                continue
            ordinal = seen.get(guid, 0)
            seen[guid] = ordinal + 1
            infos.append(DeviceInfo(guid, ordinal, name, axes, iid))
        self._infos = infos

    def devices(self) -> list[DeviceInfo]:
        return list(self._infos)

    # -- per-frame ------------------------------------------------------

    def poll(self) -> bool:
        """Pump SDL events. Returns True if the device set actually changed.

        Devices are added and dropped one at a time. Nothing here tears down
        the joystick subsystem: doing that re-announces every device, and
        reacting to those announcements is how this turns into a loop.
        """
        if not self._started:
            return False
        changed = False
        for ev in pygame.event.get():   # get() pumps, so no separate pump
            if ev.type == pygame.JOYDEVICEADDED:
                if self._open(ev.device_index):
                    changed = True
            elif ev.type == pygame.JOYDEVICEREMOVED:
                if self._sticks.pop(ev.instance_id, None) is not None:
                    changed = True
        if changed:
            self._reindex()
        return changed

    def _find(self, ref: AxisRef) -> DeviceInfo | None:
        if not ref.guid:
            return None
        same = [d for d in self._infos if d.guid == ref.guid]
        if same:
            if ref.ordinal < len(same):
                return same[ref.ordinal]
            return same[0]
        # GUID gone (different SDL build, replaced hardware): try the name.
        by_name = [d for d in self._infos if ref.name and d.name == ref.name]
        if by_name:
            return by_name[min(ref.ordinal, len(by_name) - 1)]
        return None

    def raw(self, ref: AxisRef) -> float | None:
        """Raw axis value in -1..1, inversion applied. None if unavailable."""
        if not ref.assigned:
            return None
        dev = self._find(ref)
        if dev is None or ref.axis >= dev.axes:
            return None
        js = self._sticks.get(dev.instance_id)
        if js is None:
            return None
        try:
            v = float(js.get_axis(ref.axis))
        except pygame.error:
            return None
        v = max(-1.0, min(1.0, v))
        return -v if ref.invert else v

    def available(self, ref: AxisRef) -> bool:
        return self.raw(ref) is not None

    def snapshot(self, dev: DeviceInfo) -> list[float]:
        """Every axis of one device, for the live bars in the settings window."""
        js = self._sticks.get(dev.instance_id)
        if js is None:
            return []
        try:
            return [float(js.get_axis(i)) for i in range(dev.axes)]
        except pygame.error:
            return []


# -- deadzone maths ------------------------------------------------------


def centred(raw: float, deadzone: float) -> float:
    """Centre-referenced axis -> -1..1, rescaled from the deadzone edge.

    Inside the deadzone the result is exactly 0.0; just outside it the result
    leaves 0 continuously, so there is no visual jump as the stick breaks out.
    """
    dz = max(0.0, min(0.9, deadzone))
    mag = abs(raw)
    if mag <= dz:
        return 0.0
    scaled = (mag - dz) / (1.0 - dz)
    return scaled if raw >= 0 else -scaled


def unipolar(raw: float, deadzone: float) -> float:
    """Full-travel axis (plane throttle) -> 0..1, with both ends squared off.

    A deadzone at each end means idle really reads 0% and the stop really
    reads 100%, which is what matters on a throttle.
    """
    dz = max(0.0, min(0.45, deadzone))
    t = (raw + 1.0) / 2.0
    if t <= dz:
        return 0.0
    if t >= 1.0 - dz:
        return 1.0
    return (t - dz) / (1.0 - 2.0 * dz)
