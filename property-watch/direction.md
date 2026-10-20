# property-watch

**Status:** idea

## What it is

A monitoring system for the whole property, built from a handful of ESP32 nodes
reporting to a hub on site. Three things to begin with, and room for more:

1. **Dual-WAN health** — both internet uplinks watched continuously, with the
   monitoring data itself travelling over both paths so losing one link does not
   lose the record of losing it.
2. **Front drive** — a 24 GHz radar node that tells the difference between a
   vehicle *approaching*, *parking*, and *turning around and leaving*, and alerts
   on each differently.
3. **Temperature** — several sensors around the property, designed from day one
   so that adding a tenth node is a config change, not a rewrite.

On top of that, a web app for looking at the property's state and history, and
push alerts on the phones of everyone who lives here.

## Why

The property has two internet uplinks and no way to know which one is failing,
or when. The front drive is used by people who should be there and people who
should not, and "something moved" is not useful at 2 a.m. — "a vehicle came in,
sat for four minutes and left" is. Temperature matters in an Alberta winter,
where an unheated building going below freezing is a burst-pipe bill.

Each of these is individually small. Built separately they would be three
half-finished things with three sets of credentials and no shared history. Built
together they are one system with one place to look.

## Scope

**In scope**

- ESP32 sensor nodes, mains or PoE powered, reporting to a hub on site.
- A hub that stores everything locally, so a WAN outage loses nothing.
- Alert delivery to several named residents, routed by alert type and severity.
- A web app showing live state and history, reachable both on the LAN and from
  outside.
- Expansion as a first-class concern: a new sensor is a new node definition, not
  new plumbing.

**Deliberately not in scope**

- **Not a security system.** No sirens, no locks, no door/window contacts, no
  dispatch, no claim of intruder detection. It observes and tells people.
- **No video, no faces, no plates.** The drive is watched by radar. A camera is
  a separate decision, with its own privacy conversation, and is not assumed.
- **No cloud dependency for the core loop.** Sensing, recording and local
  viewing must work with both uplinks down. Only outbound alerts and remote
  access need the internet.
- **No control.** Nothing here switches a relay, opens a gate, or turns on heat.
  Read-only until there is a reason to change that, deliberately taken.

## Stack

**Undecided, on purpose.** The platform choice — Home Assistant + ESPHome, a
fully custom stack, or a hybrid — is deferred until the radar is proven in the
actual driveway. Committing a stack around a sensor that may not perform is the
mistake this ordering avoids. See `plan.md` for the three candidates and what
the spike has to produce before the choice is made.

What *is* settled:

- **ESP32** sensor nodes.
- **24 GHz mmWave radar** for the drive, not a camera and not a PIR.
- **A hub on site** that owns the data, with both WANs as egress paths.

## How to run

Nothing to run yet. The first piece of work is the hardware spike in
`spike-01-radar.md` — one ESP32 and one radar module on the drive, logging raw
tracks, no platform and no app.

## Open questions

- **WAN topology.** Is this one dual-WAN router with a single LAN behind it, or
  two routers each with their own LAN? It decides whether nodes have one network
  to join or a choice of two, and how the hub reaches both paths. Assumed
  hub-centric with dual egress for now, which is correct either way.
- **Out-of-band alerting.** If both WANs are down, nothing reaches a phone. An
  LTE stick on the hub is the only fix. Worth it, or is "both down" rare enough
  to accept?
- **Radar siting at the drive.** Power and Wi-Fi coverage at the mounting point
  are unknown, and are likelier to sink this than the radar is.
- **Who counts as a resident**, and does everyone get every alert? A vehicle at
  3 a.m. is not the same alert as a shed at 2 °C.
- **Retention.** How long is history kept, and at what resolution?
