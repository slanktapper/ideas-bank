# rover — plan

Written 2026-10-19 MDT. A sketch for a future project, not a build order.

---

## 1. Phases

Ordered so that the cheapest phase can kill the project, and no money is spent
before the property has had its say.

**Phase 0 — survey the property. No hardware, no spend.**
The single most valuable thing that can be done today, and it needs a tape
measure and an afternoon.

- Map it: distances, the route a patrol would actually take, what it passes.
- Slopes — grade in percent, measured. Tracks tolerate a lot, but not
  everything, and a 25% side-slope is a rollover.
- Surfaces along the route: gravel, grass, dirt, concrete, and where they meet.
  Transitions are where robots get stuck, not open ground.
- **Sky view**, logged with a phone GNSS app along the route. RTK wants open
  sky; tree canopy and walls cause multipath. Dead zones here decide whether
  RTK alone is enough or dead reckoning has to carry real distance.
- Where a dock could go, and whether it has power and shelter.
- Standing water, mud after rain, and where snow drifts in winter.

**Gate: if the route has no sky view and no sensible dock site, the project is a
different project.** Better to learn that for free.

**Phase 1 — chassis on the bench.** Tracks, motors, power, low-level controller,
emergency stop. **Teleoperation only — no autonomy whatsoever.** Drive it around
the property on a controller and find out what it actually gets stuck on. Most
of what Phase 2 needs to know is learned here.

**Phase 2 — navigation.** RTK, geofence, waypoint following, obstacle stop. The
geofence goes in *first* and is tested by trying to drive through it. Autonomy
arrives after the thing that stops autonomy.

**Phase 3 — payload.** Camera, on-board person detection, recording, storage,
retention. Patrol imagery before trigger behaviour.

**Phase 4 — integration.** Subscribe to `property-watch` events; record-on-detect
with standoff. Last, because it is the easy part and depends on everything else.

**Phase 5 — winter.** Heated battery box, charge-above-zero logic, traction,
sensor clearing. Scoped honestly against **The winter problem** in
`direction.md`.

---

## 2. Interface to `property-watch`

Agreed as a **one-way event contract**. `rover` subscribes; the hub publishes to
the world and neither knows nor cares who listens. No shared code, no shared
data, no shared storage — the only thing crossing the boundary is a message.

Sketch, to be settled when `property-watch` Phase 1 designs its event model:

```jsonc
{
  "event": "drive.vehicle.parked",
  "ts": "2026-10-19T19:42:11Z",   // UTC on the wire, Alberta time at display
  "zone": "front-drive",
  "confidence": 0.86
}
```

What `rover` needs from it: a **zone** it can resolve to a waypoint, a
timestamp, and an event type it can map to a behaviour. What it must *not* need:
any knowledge of which sensor fired, or any ability to talk back.

If the robot ever needs the hub to change, that is a conversation and a decision
recorded in both `direction.md` files — not a patch that quietly couples two
projects that were built apart on purpose.

---

## 3. Design notes worth not rediscovering

- **Skid steer chews turf.** Differential tracks turn by slipping. On gravel
  that is free; on grass, a few hundred pivot turns in one spot leaves bare
  earth. Route planning should prefer wide arcs, and the dock approach should
  not be on lawn.
- **The dock is harder than the robot.** Final alignment, contact reliability
  in rain and ice, and recovering from a missed approach are where outdoor
  robot projects stall. Budget real time; printed funnels and a wide capture
  angle do more than precision.
- **Charging below 0 °C damages lithium cells**, both Li-ion and LiFePO4, while
  discharging below zero is fine. The dock must warm the pack before accepting
  charge, or refuse to charge. This is a safety rule, not a performance tweak.
- **Put the emergency stop below the autonomy**, in the low-level controller, so
  a hung or crashed high-level brain cannot drive. Hardware cutoff as well as a
  software one.
- **Watchdog on the geofence**, same reasoning: a boundary enforced by the layer
  that can crash is not a boundary.
- **Detection runs on-board.** Streaming video to the hub to classify it adds
  latency and dies with the Wi-Fi. The Jetson is in the budget for this reason.
- **Wi-Fi coverage across the property is an unlisted dependency** — and it is
  the same unknown that `property-watch`'s spike hits at the drive. Whatever
  that spike learns about coverage is worth reading before Phase 1.

---

## 4. Printed and cut parts

Per `available-tools.md` this is an obvious fit — a robot is mostly brackets.
Colours and materials from `filament.md`.

| Part | Material | Note |
| --- | --- | --- |
| Body shell, electronics trays | **PETG** | Functional default; ~80 °C, tough |
| Sensor and camera mounts | PETG black | Black for UV on anything facing out |
| Dock alignment funnels | PETG | Wide capture angle beats precision |
| Battery box | **ABS** | ~100 °C, and the heated box is the one hot part |
| Track treads, bump trim, seals | **TPU — not on the shelf** | The right material, and there is none |
| Labels, geofence markers | vinyl, cutter | Black/red/orange on hand |

**Two material gaps to order against, neither urgent today.** **TPU** for treads
and anything that must seal or absorb a knock — there is no flexible filament at
all. **ASA** for the outdoor shell, the UV-stable material `filament.md` also
lists as absent; this is the same gap `property-watch` hit for its drive
enclosure, so one order covers both. PETG is a workable substitute for a season;
PLA is not a candidate outdoors in any form.

Structural parts carrying drive loads are the place to be careful: printed
brackets are fine for sensors and trays, and are the wrong answer for motor
mounts and track tensioners. Those want metal.
