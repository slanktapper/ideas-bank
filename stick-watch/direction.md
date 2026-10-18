# stick-watch

**Status:** working — built 2026-10-17 MDT, not yet run against real hardware

## What it is

A desktop app that shows flight-sim controller axes live, big enough to read
out of the corner of your eye. Two windows: an **overlay** that draws the
readouts, and a **settings window** where you choose which axes appear on it.

The overlay starts empty. You add an axis, pick the device and axis (or press
Detect and wiggle the one you mean), choose its type, and drag it where you
want. Every readout is sized in **millimetres on the glass**, not pixels, so
"a 19 mm dot" is 19 mm when you hold a ruler against the screen.

Three axis types:

| Type | Sub-type | Display |
| --- | --- | --- |
| Joystick | — | Concentric squares, a centre dot, and a crosshair cursor driven by two mapped axes |
| Rudder | — | Horizontal slider, dead centre in the middle: the dot travels the track, black at centre, red growing to the left, green growing to the right |
| Throttle | plane | Bar filled from the bottom, with a large percentage |
| Throttle | heli | **Collective** — the same bar filled from the centre detent: green climbing above, red falling below, over a near-transparent track |

## Why

Flying on instruments or on a camera view, you cannot see what your hands are
doing. A trim that has crept off centre, a collective that is not quite at the
detent, a rudder you are standing on without noticing — all of it is invisible
until the aircraft misbehaves. This puts the physical axis positions where the
eye already is.

## Scope

**What it does.** Reads any HID controller SDL can see, applies a per-axis
deadzone and inversion, and draws it at a physically calibrated size. Settings
persist across runs and are written to disk as you change them.

**What it deliberately does not do.**

- **Modify or intercept input.** It reads axes. It does not remap, curve, or
  feed anything to the sim. Nothing here can affect what the sim receives.
- **Draw over exclusive-fullscreen.** No overlay can. Set the sim to borderless
  windowed, or use the plain-window mode on a second monitor.
- **Buttons, hats, or POV.** Axes only.
- **Per-axis calibration.** It trusts what the driver reports as −1..1.

## Display rules

**Deadzone** is a percentage of full travel, set per readout. Inside it the
readout is exactly neutral — the rudder dot is black, the joystick cursor sits
on the centre dot. Outside it, travel is **rescaled from the deadzone edge**,
so the dot leaves neutral smoothly instead of jumping to 10% the instant the
stick breaks out. The plane throttle squares off both ends instead, so idle
really reads 0% and the stop really reads 100%.

**Rudder.** A horizontal slider with dead centre in the middle, marked by a
heavy full-height line, with ticks at half and full travel. The dot travels the
track with the pedals and carries the size and colour as well: diameter runs
from `dot at centre` (19 mm default) to `dot at full` (30 mm default), black in
the deadzone, red to the left, green to the right. Position says where you are,
size and colour say how far. Track length (110 mm default) and both diameters
are saved.

**Joystick.** Box *k* of *N* sits `k × spacing` out from the centre and marks
`k/N` of full travel, so the outermost box is 100% deflection. Defaults: 4
boxes at 10 mm spacing, so full deflection is 40 mm from centre and the
outermost box is 80 mm across. Box count, spacing, centre dot (3 mm) and
cursor (10 mm) are all saved. Positive roll moves the cursor right, positive
pitch moves it up; flip either with the Inverted box.

**Throttle, heli — the collective.** The same bar as the plane throttle,
filled from the centre detent outwards instead of from the bottom: green
climbing above centre, red falling below. A heavy centre line is drawn on top
of the fill and overhangs both edges, so nothing can bury the one thing this
instrument exists to show.

It carries no percentage. The only figure that matters on a collective is
whether you are on the detent, and the centre line already says that, so the
space under the bar holds the readout's **name** instead — defaulting to
`Collective`. There is no label above the bar; that would just say it twice.

The track behind the fill is **nearly transparent** (alpha 30), so the sim
shows through it. The fill, the centre line and the outline stay solid and
carry the reading on their own. The plane throttle keeps a solid track.

## Persistence

**Nothing waits for a clean shutdown.** Every change — a dragged widget, a spin
box, the calibration — marks the config dirty and is written within 200 ms.

The write is atomic: a temp file in the same directory, `fsync`ed, then
`os.replace`d over the real file, so a crash leaves either the whole old file
or the whole new one and never a half-written mix. A second copy,
`config.prev.json`, is written only after the live file is committed, and is
used if the live file is ever unreadable. Pulling the plug mid-session loses at
most the last fifth of a second of fiddling.

Settings live in `%APPDATA%\stick-watch\config.json` (override with the
`STICKWATCH_CONFIG_DIR` environment variable).

Devices are remembered by **SDL GUID plus an ordinal**, not by enumeration
order, so axes stay mapped across reboots and USB ports — and two identical
sticks stay apart. An unplugged device keeps its assignment and the readout
says "no device" rather than silently reading zero.

## Stack

Python 3.10+, PySide6 (Qt 6) for both windows and all drawing, pygame/SDL2 for
the controllers. No build step.

Two SDL settings matter and are applied in `devices.py` before pygame loads:
`SDL_VIDEODRIVER=dummy` (no stray SDL window) and
`SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1` — without the second one SDL stops
reporting axis motion whenever its window is unfocused, which for an overlay
that never takes focus means every axis reads zero.

## Positioning

New readouts land in a centred row along the **bottom of the display**, sharing
a bottom edge, wrapping to a row above when they no longer fit across. Adding
one re-tidies the row; **Arrange readouts along the bottom centre** on the
Display tab does the same on demand.

Three ways to place them, because the mouse is the one that can fail:

1. **Drag**, with the overlay unlocked.
2. **Position (px)** boxes in each readout's editor — no mouse involved.
3. **Arrange along the bottom centre**, which resets everything to the row.

### Locking

One big two-state button on the Display tab, green for LOCKED and amber for
UNLOCKED, saying what it will do when clicked.

Getting back out of unlocked mode needs its own answer, because an unlocked
overlay is always-on-top and catching clicks, so the settings window behind it
can be unreachable. Three ways back, and all of them keep your placement:

- **Esc** on the overlay.
- The **Done — lock overlay** button on the bar across the top of the overlay,
  which is the one that still works when something else has the keyboard.
- The big button on the Display tab, if you can reach it.

Locking by any route also raises the settings window back to the front.

Unlocking tints the whole overlay and puts a blue plate on each readout. That
is not decoration. A translucent window on Windows is hit-tested per pixel, so
a fully transparent pixel passes the click through to whatever is behind it —
with only a thin border drawn, nothing but the few opaque pixels of a dot could
be grabbed, which made the overlay feel immovable. The wash gives every pixel
an alpha so clicks land. `WindowDoesNotAcceptFocus` is likewise set only while
locked; unlocked, this is an ordinary interactive window.

## Performance

The polling loop reads axes and repaints; everything else is meant to stay out
of its way.

- **Hot-plug is incremental.** Devices are opened and dropped one at a time
  from SDL's own events. Nothing in the loop tears down the joystick
  subsystem — doing that makes SDL re-announce every device, and reacting to
  those announcements rescans again, which loops at the polling rate. That bug
  cost roughly every frame; `selftest.py` now guards against it returning.
- **Axis values are quantised** to three decimals before they reach a readout.
  Raw axes jitter in the last few digits, and an unquantised value repaints
  every readout on every frame even with the stick sitting still.
- **The Devices tab only updates while it is on screen**, throttled to 20 Hz,
  and skips bars whose value has not moved.

The Display tab shows the rate actually achieved next to the rate requested.
If those two disagree badly, something in the loop is costing more than it
should.

Known remaining cost: in transparent mode the overlay is a full-screen layered
window, so Windows recomposites a screen-sized surface whenever a readout
repaints. Shrinking the window to the bounding box of the readouts while
locked would cut that a lot, and is the next thing to try if it is still slow.

## Self-test

```
python selftest.py
```

Checks the deadzone maths, the hot-plug path, and that settings survive a
crash. No joystick and no display needed.

## How to run

Windows, first time and every time:

```
run-windows.bat
```

It builds `.venv`, installs the dependencies, and starts the app. Or by hand:

```
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m stickwatch
```

**First run, in order:**

1. **Display & overlay → Screen calibration.** Hold a ruler against the bar and
   adjust until 100 mm on the bar is 100 mm on the ruler. Default is 4.82 px/mm
   (24″ at 2560×1440).
2. **Devices.** Confirm your sticks are listed and the bars move.
3. **Overlay axes → Add.** Pick a type, press **Detect**, move the axis.
4. **Display & overlay →** untick **Locked** to drag readouts into place, then
   tick it again to make the overlay click-through.

## Open questions

- **No global hotkey to unlock the overlay.** Unlocking is done from the
  settings window, because a real global hotkey needs the Win32 API and this
  stays pure Qt. If reaching for the settings window mid-flight gets annoying,
  that is the thing to add.
- **Size settings are per readout, not per type.** Two rudder readouts are
  sized independently. Fine for one of each; tedious if that changes.
- **No per-axis calibration or curve display.** Raw driver values only.
- **Untested against real hardware.** Written and checked headlessly — the
  drawing, the deadzone maths and the persistence are verified, but no physical
  stick has been plugged into it yet.
