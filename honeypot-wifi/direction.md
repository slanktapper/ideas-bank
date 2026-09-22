# honeypot-wifi

**Status:** idea

## What it is
A small mesh of ESP32 sensor nodes placed around an acreage that listen — and only
listen — to the 2.4 GHz radio around the property. Each node watches 802.11
management traffic (probe requests, beacons, association and deauthentication
frames) and BLE advertisements, and reports what it hears to a collector service on
the home network. The collector builds a baseline of what is normally in radio range
— the house APs, the neighbours' networks that bleed over, the farm equipment, the
household's own phones, watches and tags — and raises an alert when something departs
from that baseline: an unfamiliar device lingering near the driveway at 3 a.m., an AP
that appeared overnight, a burst of deauthentication frames aimed at the house
network, a device that keeps coming back.

A second, friendlier channel runs on the same hardware: nodes recognise the
household's own known devices and emit a presence event, so arriving home can turn on
the yard lights without a motion sensor guessing at it.

Despite the name, this is not a honeypot in the classic sense — nothing is advertised
to lure anyone in. It is a passive listening net. The name stuck from the first
conversation; the decoy-AP idea it implies is recorded under Open questions and is
deliberately not part of the current design.

## Why
An acreage has long sightlines, few neighbours, and a lot of ground that nobody is
watching most of the time. A driveway sensor tells you something is there; it does
not tell you whether it has been there before. Almost everyone who comes down the
road is carrying a phone, a smartwatch, a set of earbuds or a vehicle head unit, and
every one of those is chattering on the 2.4 GHz band whether or not it ever connects
to anything. That chatter is enough to answer the questions that actually matter:
is there a device here that has never been here before, has it been here on three
separate nights, is it sitting at the property line or moving along the road, and is
anyone actively attacking the house Wi-Fi.

There is also a longer-term reason to build it carefully: this may eventually be
offered as a service to other rural properties. That ambition sets the constraints
below — everything must be defensible as pure defensive monitoring of one's own
property, with no capability that would be awkward to explain to a customer, an
insurer, or a lawyer.

## Scope

### What this does
- **Passive Wi-Fi sensing.** Promiscuous-mode capture of 802.11 *management* frames
  only, with channel hopping across the 2.4 GHz band. Records frame type, source and
  destination addresses, SSID where present, RSSI, channel, and timing.
- **Passive BLE sensing.** Scan-only observation of BLE advertisements: address,
  address type (public vs. random), advertised service UUIDs and manufacturer data,
  RSSI, timing.
- **Baselining and anomaly detection.** The collector learns what is normally
  present, per node and per time of day, and alerts on departures: new or returning
  unknown devices, new APs, devices with unusually strong signal at a perimeter node,
  deauthentication or disassociation floods against the household networks, and
  devices seen across multiple nodes in a pattern that reads as movement.
- **Coverage shaping.** Remote nodes at the driveway, gate, shop and property corners
  for area coverage; directional antennas on nodes aimed at the road and driveway for
  reach and crude bearing. Multiple nodes reporting RSSI on the same device gives a
  rough sense of where it is.
- **Presence triggers.** Known devices — the household's phones, or a carried BLE tag
  — produce a presence event on the node that sees them, which the collector turns
  into an automation call (yard lights, notification, whatever is wired up).
- **Alerting.** Collector-side rules push notifications for the events worth waking up
  for, and keep the rest for review.

### What this deliberately does not do
These are hard boundaries, not preferences. They exist because this is a defensive
tool and may become a product.

- **Never transmits on the monitored bands** except for a node's own backhaul link.
  No deauthentication, no disassociation, no jamming, no beacon spam, no probe
  flooding, no BLE spam.
- **No decoy or rogue AP.** No evil twin, no captive portal, no SSID impersonation of
  anyone else's network.
- **No traffic interception.** Management-frame headers and BLE advertisement
  metadata only. No payload capture, no handshake capture, no WPA cracking, no
  attempt to read, store or decrypt the contents of anyone's communications.
- **No credential capture** of any kind, by any mechanism.
- **No identity resolution.** The system deals in device observations, not people. It
  does not try to attach a name, phone number, account or identity to an unknown
  device, and does not correlate against external databases.
- **Not a deterrent or response system.** It observes and reports. Anything that acts
  back on an intruder's equipment is out of scope permanently.

### Legal and privacy posture
Receive-only monitoring of radio metadata on one's own property is the whole design,
and the boundaries above are what keep it there — in particular, capturing headers
and advertisement metadata rather than the contents of communications. If this ever
becomes a service for other properties, more is needed before the first customer:
Canadian federal (PIPEDA) and Alberta (PIPA) privacy law can treat a device
identifier tied to a place and a time as personal information, which brings in
consent, notice, retention limits and safeguards. Data minimisation and a short
retention window should be designed in from the start rather than retrofitted, and
a lawyer should look at it before it is sold. Nothing here is legal advice.

## Stack
- **Nodes:** ESP32, firmware in C on **ESP-IDF v5.x** (`idf.py` build/flash/monitor).
  The whole job is low-level radio work — `esp_wifi_set_promiscuous()` with a raw
  frame callback, the NimBLE scan API, channel hopping and duty-cycling between the
  two — which is ESP-IDF's native territory.
- **Radio module:** a variant with an external antenna connector (u.FL/IPEX) for the
  directional nodes. Exact chip not settled — see Open questions.
- **Transport:** nodes batch observations and **HTTP POST JSON** to the collector over
  the property LAN, with on-device buffering so a node that loses its link backfills
  rather than drops.
- **Collector:** a small service on the home network — HTTP endpoint, SQLite store,
  baseline/rules engine, alerting, and an outbound webhook for automations.
  Implementation language not chosen yet; see Open questions.

## How to run
Nothing to run yet — no firmware and no collector exist. This file is the design so
far. The first milestone is a single node on a bench that captures management frames
and BLE advertisements and POSTs them to a stub collector, to find out what the real
frame rates, drop rates and duty-cycle limits look like before anything goes outside.

## Open questions

**Hardware**
- Which ESP32. The classic ESP32 and the S3 are 2.4 GHz only, which misses 5 GHz
  Wi-Fi entirely — a real blind spot, since modern phones prefer 5 GHz when
  associated. The C5 is dual-band and would close it. Decide whether 5 GHz coverage
  is worth the newer, less-trodden part. Note that probe requests, the most useful
  signal for spotting an unassociated device, are still sent on 2.4 GHz by nearly
  everything.
- One radio, two jobs. Wi-Fi promiscuous capture and BLE scanning share a single
  radio; both are duty-cycled and both will miss things. How much is missed, and
  whether perimeter nodes should specialise (some Wi-Fi-only, some BLE-only), is an
  empirical question for the bench milestone.
- Antennas: which directional pattern for the road and driveway, and how much
  omni coverage is needed to fill in behind them.
- Power and backhaul for remote nodes. Solar plus LiFePO₄ at the gate, or run power?
  Will property Wi-Fi even reach the far nodes, or is an ESP-NOW relay hop or a
  wired/PoE run needed to get them to the collector?
- Node count and placement — driveway entrance, gate, shop, house, corners.

**Detection quality**
- MAC randomisation. Modern iOS and Android randomise addresses in probe requests and
  BLE advertisements, so an unknown device usually cannot be tracked across visits by
  address alone. How far coarse fingerprinting (information-element sets, timing,
  RSSI patterns) can be pushed without becoming identity resolution — which is out of
  scope — needs testing. Baseline anomaly detection tolerates randomisation much
  better than per-device tracking does.
- Presence detection of known devices is the mirror of that problem and is more
  tractable: a carried BLE tag with a stable identifier, or a device configured with a
  fixed MAC for the home network, is far more reliable than trying to recognise a
  randomising phone. A tag is the likely answer.
- What "out of the ordinary" means precisely: how long a baseline needs to learn, how
  to handle seasonal and time-of-day variation, and how to keep false alarms from
  passing traffic on the road low enough that alerts stay worth reading.

**Software**
- Collector implementation language. Python with FastAPI and SQLite is the obvious
  first pick — fast to write, good enough for this event volume, easy to hand to
  someone else later. Not decided; picking it means picking it deliberately.
- Retention: how long raw observations are kept versus rolled up. Short by default,
  for the privacy reasons above.
- Where alerts and automation calls go — push notification service, Home Assistant
  webhook, both.

**Direction**
- The decoy-AP idea the project name implies: an SSID nothing legitimate should ever
  join, logging association attempts as a high-signal indicator. It is genuinely
  useful and genuinely defensive when it logs metadata only, but it means
  transmitting, and it complicates the service story. Parked, not rejected.
- The service ambition: what a second property would actually need — provisioning,
  multi-tenancy, updates, support — and what the privacy work costs before a first
  customer.
