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
- **WiFi, on the same walk.** A phone survey app alongside the GNSS one — same
  trip, second dataset, no extra effort. It will not be the robot's antenna at
  the robot's height, so it is indicative only, but it answers the cheap
  version of the question today: is coverage a nuisance or a project? See §3.
- Where a dock could go, and whether it has power and shelter.
- Standing water, mud after rain, and where snow drifts in winter.

**Gate: if the route has no sky view and no sensible dock site, the project is a
different project.** Better to learn that for free.

**Phase 1 — chassis on the bench.** Tracks, motors, power, low-level controller,
emergency stop. **Teleoperation only — no autonomy whatsoever.** Drive it around
the property on a controller and find out what it actually gets stuck on. Most
of what Phase 2 needs to know is learned here. Start logging link metrics on
these drives: position is rough without RTK, but it is the real antenna at the
real height, and teleop over a patchy link teaches you where the holes are
rather faster than a map does.

**Phase 2 — navigation.** RTK, geofence, waypoint following, obstacle stop. The
geofence goes in *first* and is tested by trying to drive through it. Autonomy
arrives after the thing that stops autonomy. Accurate position also turns the
Phase 1 logging into a real survey — the signal map (§3) starts accumulating
here, for free, on every patrol.

**Phase 3 — payload.** Camera, on-board person detection, recording, storage,
retention. Patrol imagery before trigger behaviour. Once there is a real video
bitrate to measure, calibrate the signal map against it (§3.3) and build
store-and-forward on top: record locally always, upload from good ground.

**Phase 4 — integration.** Subscribe to `property-watch` events; record-on-detect
with standoff, driving to the ranked observation post for the zone (§3.4) rather
than at the event. Last, because it is the easy part and depends on everything
else.

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

## 3. The signal map

The robot is the only thing on the property that goes everywhere and knows
where it is. That makes a radio survey nearly free: a sample every second along
a patrol it was driving anyway. Two halves to this — building the map, and
letting it change behaviour.

### 3.1 What a sample is

RSSI alone is a bad proxy for "can I stream video from here". A −60 dBm link
beside an interference source is worse than a clean −70. So a sample is a small
row, not a number:

```jsonc
{
  "ts": "2026-10-19T19:42:11Z",
  "x": 41.2, "y": -18.7,        // property frame, from RTK
  "heading_deg": 212,            // the robot shadows its own antenna
  "band": "5",                   // 2.4 / 5 / 6 — mapped separately, see below
  "bssid": "...", "channel": 44,
  "rssi_dbm": -63, "noise_dbm": -92, "snr_db": 29,
  "phy_rate_mbps": 180, "retry_pct": 4.1
}
```

**Map each band separately.** 2.4 and 5 GHz behave oppositely outdoors — 2.4
carries much further and through foliage, 5 gives the bandwidth video wants
over shorter distance. A single blended "signal quality" number averages two
radios that disagree, and is worse than either.

**Log heading with every sample.** The robot's own body and battery box sit
between its antenna and half the property; several dB swing with heading is
normal. A map built driving north and used driving south is wrong in a way
that is very hard to debug later. Logging heading at least makes it visible,
and two antennas make it smaller.

**Scan sparingly.** Association metrics are free and continuous. A full scan of
all visible BSSIDs is richer — it shows alternatives and neighbours' channels
— but on many chipsets it briefly breaks the association. Never scan while
streaming.

### 3.2 Holding the map

A **grid of cells, 1–2 m**, each holding per band: sample count, mean, **and
variance**, plus last-seen. Explicitly marked unsurveyed where nothing has been
measured.

Two decisions inside that, both deliberate:

- **Keep variance, not just a mean.** A cell averaging −65 dBm with ±15 dB
  swing is a worse place to upload from than a steady −70. The whole point is
  predictability, and an average throws it away.
- **Do not interpolate across obstacles.** Kriging or IDW produce a prettier
  heatmap and invent data in exactly the places RF is least smooth — building
  corners cast hard radio shadows. An honest map with holes in it beats a
  smooth map that is confidently wrong behind the shop. Unsurveyed is a state,
  not a zero.

**Decay old samples.** Wet foliage attenuates badly, leaf-on and leaf-off are
different properties, and the neighbours change their channels. Weight by
recency and let repeated patrols refresh it. A map built once is a snapshot
being used as a fact.

### 3.3 Calibrating it against the real job

dBm thresholds are a starting point, not an answer. The usual rules of thumb —
better than about −67 dBm and SNR above ~20 dB for video — are worth having on
day one and worth discarding on day thirty.

What replaces them: at a handful of candidate spots, run a **real uplink
throughput and latency probe** — the actual video bitrate, sustained. That
sparse ground truth calibrates the dense cheap samples, and turns the map from
"signal strength" into **"can this cell carry the stream"**, which is the only
question being asked of it.

### 3.4 Using the map

**Observation posts.** When a detection arrives for a zone, the robot should
not drive to the middle of that zone. It should drive to the best cell that
satisfies all of: sightline to the zone, inside standoff distance, inside the
geofence, reachable, and good signal. Precompute a ranked shortlist per zone
and re-rank as the map improves.

**When nothing satisfies both, seeing the event wins.** If the only cell with
a sightline is a dead zone, go there anyway and buffer. Observation is the job;
the livestream is a convenience.

**Record locally, always. Upload opportunistically.** Signal quality decides
*when* footage leaves the robot, never *whether* it was captured. Write to
local storage first, flush from good ground — including, when a sighting is
over, deliberately driving to a known-good cell to empty the buffer. This is
the requirement to "broadcast back from good areas" done in the order that
cannot lose footage.

**Route planning prefers good corridors — gently.** Favour well-covered paths
where the detour is small, so teleop and live view stay alive. Do not let
signal dictate coverage: the patrol's job is to visit things, and a route that
avoids the dead corner of the property stops inspecting the dead corner.

**Going dark is a planned state, not a fault.** The map says where the holes
are, so the robot can announce "out of contact for about 40 seconds" before
entering one, and recover on a timeout rather than treating silence as an
emergency. This is also the argument for keeping control off the video link
entirely — see the open question in `direction.md`.

### 3.5 Where it fits in the phases

The survey starts long before the robot is autonomous:

- **Phase 0** — walk the route with a phone WiFi app on the *same trip* as the
  GNSS sky-view walk. One afternoon, two datasets, no hardware. Enough to know
  whether coverage is a nuisance or a project.
- **Phase 1** — teleop driving logs link metrics with rough position. Crude,
  but it is real data from the real antenna at the real height.
- **Phase 2** — RTK arrives, and the survey becomes automatic and accurate.
- **Phase 3** — throughput calibration, then observation posts and
  store-and-forward.

---

## 4. Design notes worth not rediscovering

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
- **Wi-Fi coverage is no longer an unlisted dependency** — §3 makes it a
  measured one. It is still the same unknown `property-watch`'s spike hits at
  the drive, and whatever that spike learns is worth reading before Phase 1.

---

## 5. Printed and cut parts

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
