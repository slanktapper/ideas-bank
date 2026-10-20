# property-watch — plan

Written 2026-10-19 MDT. Revise as the spike reports back.

---

## 1. Architecture

One principle decides most of the rest: **the hub is on site and owns the
data.** Sensors talk to it over the LAN. Nothing a sensor measures crosses the
internet to be recorded. That is what makes "a WAN went down" an *event in the
log* rather than *a hole in the log*.

```
  ┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
  │ drive node │   │ WAN-A probe│   │ WAN-B probe│   │ temp nodes │
  │  ESP32 +   │   │   ESP32    │   │   ESP32    │   │  ESP32 ×n  │
  │  LD2451    │   │            │   │            │   │            │
  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘   └─────┬──────┘
        └────────────────┴───── LAN ──────┴────────────────┘
                               │
                      ┌────────▼────────┐
                      │   hub, on site  │   local storage = source of truth
                      │  ingest + rules │   history survives both WANs down
                      │  + web app      │   LAN-reachable always
                      └───┬─────────┬───┘
                     WAN A│         │WAN B
                          ▼         ▼
                    push alerts, remote access, off-site copy
```

### Every node follows the same shape

This is the expansion story, and it has to be true from the first node:

1. Reports on a fixed schedule **and** on change.
2. **Buffers locally** when the hub is unreachable, and backfills on reconnect.
   A node that drops readings during a hub reboot makes the history a liar.
3. Sends a heartbeat. **Silence is an alert** — a dead sensor must not read as
   "nothing is wrong".
4. Is defined by one config file. Adding the tenth temperature sensor is
   copying a file and changing a name.
5. Updates over the air. Nodes on a roof or at the end of a drive do not get
   visited with a laptop.

---

## 2. Dual-WAN: probing and surviving

Your requirement — *push data through both so one going down doesn't lose
everything* — has four separate failure points, and they want different
answers. Worth separating, because three of the four are cheap and one is not.

| Failure | What's at risk | Answer |
| --- | --- | --- |
| One WAN down | Alerts and remote access | Hub routes over both; critical alerts sent **twice, once per path**, with a dedup key so phones show one |
| Both WANs down | All outbound contact | Nothing on the LAN is lost. Reaching a phone needs an LTE stick on the hub — see open question |
| Hub down | Everything, while it's down | Nodes buffer and backfill. A second collector is possible but is the expensive answer |
| Hub lost | All history | Rolling encrypted copy pushed off-site over whichever WAN is up |

### Making a probe actually use its own uplink

The non-obvious part. An ESP32 on a shared LAN cannot choose a WAN by itself —
it just sends to the default gateway. Two options:

- **One dual-WAN router:** give each probe a static IP and add a policy route —
  *source 10.0.0.41 → WAN A*, *source 10.0.0.42 → WAN B*. Clean, and the probe
  firmware stays identical.
- **Two routers, two LANs:** each probe joins the SSID of the uplink it watches.
  Simpler to reason about; the hub then needs a foot in both networks.

Which of these you have is an open question in `direction.md`, and it is the
one I would most like answered before Phase 1.

### What a probe measures

Every 30 s, out its own uplink:

- Reachability to **three independent targets** — one target's outage must not
  look like yours.
- Round-trip latency and jitter; loss over a rolling window.
- DNS resolution time, separately. DNS dies on its own more often than links do.

Deliberately **not** throughput: an ESP32 cannot saturate a real uplink. If you
want speed graphs later that is a Raspberry Pi per uplink, and it is additive —
same hub, same schema, no rework.

---

## 3. The front drive

### Part choice — corrected

I named the **LD2450** when asking. Checking it before you spend money: it is a
**6 m** human-trajectory module. A driveway is not 6 m. The right part is the
**HLK-LD2451**, which is the vehicle-detection member of the same family:
**10–100 m, adjustable**, reporting distance, speed and *approaching vs.
receding* directly, over UART. Roughly ±20° beam, 5 V, −40 to +85 °C, which
matters here.

The trade: the LD2451 gives range + direction, not the X/Y track the LD2450
gives. So behaviour is inferred from how range changes over time rather than
read off a map. The state machine below says how — and it is the main thing the
spike has to prove.

### Telling the three behaviours apart

Key insight: FMCW radar sees *moving* targets. A car that parks **disappears**.
That is not a bug — absence at close range is exactly the parked signature.

```
  IDLE
   └─ target, direction=approaching, range closing
        → APPROACHING          ── alert: "vehicle approaching" (instant)
             │
             ├─ range stops closing, target fades, no receding track
             │     within T_park (~45 s)
             │        → PARKED        ── alert: "vehicle parked"
             │             └─ later receding track → DEPARTED
             │
             └─ receding track within T_uturn (~90 s),
                minimum range never below R_dwell
                   → U-TURN           ── alert: "vehicle turned around"
```

Three numbers — `T_park`, `T_uturn`, `R_dwell` — decide every classification,
and none of them can be guessed from a desk. They come out of a week of logs.

What will actually be hard, in order: **rejecting the road.** A ±20° beam aimed
down a drive will still catch traffic on the road beyond it. Mitigations are
range gating (ignore beyond the property line), aim, and requiring a track to
cross a near threshold. Expect to iterate on the mount angle.

---

## 4. Temperature

The easy part, and worth doing early precisely because it is easy — it proves
the whole pipeline end to end with a sensor that cannot surprise you.

- **DS18B20** on a one-wire bus for anything needing a probe on a cable or
  several sensors per node, **SHT41** where humidity is wanted too. Avoid DHT22.
- One node can carry several sensors; locations are a config list.
- Alerting is per-sensor thresholds with hysteresis, not one global rule. A shed
  at 2 °C is urgent; a garage at 2 °C is Tuesday.
- Freeze alerts need a **rate** rule as well as a threshold — *falling 3 °C/hour
  and below 5 °C* catches a failing heater hours before 0 °C does.

---

## 5. Phases

**Phase 0 — radar spike.** `spike-01-radar.md`. One ESP32, one LD2451, bare
firmware, on the drive, logging raw frames for a week. No platform, no app, no
hub. **Gate: nothing else starts until this reports.**

**Phase 1 — platform + hub + dual-WAN.** Pick the stack (§6), stand up the hub,
build the two WAN probes. Smallest end-to-end slice that is genuinely useful:
you learn which uplink is flaky within a day.

**Phase 2 — temperature.** Three or four nodes. Proves the node pattern, the
config-file-per-node claim, and threshold alerting.

**Phase 3 — drive in production.** Classifier from Phase 0's logs, the state
machine, alert routing by time of day.

**Phase 4 — app and residents.** Dashboard, history, per-resident alert
preferences, remote access over both WANs.

**Phase 5 — expansion.** Whatever the first four made obvious. Likely
candidates: door/gate state, water, power monitoring, a camera decision.

---

## 6. The platform decision, deferred to Phase 1

Deciding after the spike, as agreed. Recording the candidates so the decision is
made against something.

| | Home Assistant + ESPHome | Hybrid | Fully custom |
| --- | --- | --- | --- |
| Node firmware | ~30 lines YAML, OTA free | same | you write and maintain it |
| Resident push | Companion app, free, per-person | Companion app | you build web push + auth |
| History / dashboard | built in | HA data, your UI | you build it |
| Custom radar logic | external component (C++) | same | native |
| Time to useful | weekend | weeks | months |

The honest read: unless the spike shows the radar needs logic that fights
ESPHome, **HA + ESPHome is the default** and the hybrid is the hedge. Decide
with the spike's data in hand.

---

## 7. Printed and cut parts

Per `available-tools.md`, mounts and enclosures are a clear fit, so these are
proposed rather than asked about. Colours and materials are from `filament.md`.

| Part | Material | Note |
| --- | --- | --- |
| Drive node enclosure / radome | **PETG black** | 24 GHz passes straight through plastic — no window, no cutout, the radar sits behind a sealed wall |
| Angled wedge mount, printed in 3–4 angles | PETG black | Aim is critical with a ±20° beam; print a set, test, keep the one that works |
| Temperature sensor housings | PETG | Louvred Stevenson-screen style for anything in sun, or it reads the sun |
| Hub bracket, cable strain reliefs | PLA (indoors) | Indoor only |
| Node labels — ID, which WAN, install date | vinyl, cutter | Black/red/orange on the shelf. Future-you will not remember which probe is WAN A |

**One material caveat, worth knowing now.** The proper outdoor plastic is ASA —
UV-stable — and `filament.md` says there is none on hand. Black PETG is the best
available substitute and its carbon black pigment helps, but PETG does degrade
in sustained UV over a few years. For a box on the drive meant to be left alone,
**a roll of ASA is worth ordering** before Phase 3. PLA is not a candidate
outdoors at all: ~60 °C softening, brittle in cold, poor UV.

---

## 8. Rough bill of materials

Approximate, for sizing only — check current prices before ordering.

| Item | Qty | Notes |
| --- | --- | --- |
| ESP32 dev boards | 6–8 | 2 WAN probes, 1 drive, 3–4 temp, 1 spare |
| HLK-LD2451 radar | 1 (+1 spare) | The drive node |
| DS18B20 probes | 4–6 | Waterproof versions for outdoor runs |
| SHT41 | 1–2 | Where humidity matters |
| Hub | 1 | Mini PC or Pi 5 + SSD. **SSD, not SD** — SD cards die under a time-series write load |
| PoE splitters or PSUs | per node | Power at the drive is an open question |
| Weatherproof glands, wire | — | |
| Filament, vinyl | — | On the shelf, plus ASA if ordered |

Biggest unknowns are not on this list: **power and Wi-Fi at the drive.** Both
are likelier to sink Phase 3 than the radar is, and both are answered by the
spike.
