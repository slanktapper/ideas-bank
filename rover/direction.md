# rover

**Status:** idea — recorded as a future feature, not started.

## What it is

A tracked ground robot that drives the property on a schedule, inspects the
things nobody wants to walk out to in February, and films when `property-watch`
reports something. Patrol and inspection are the primary job. Recording a
detected person is **one triggered behaviour among several**, not the reason the
machine exists.

That ordering is deliberate, and it came out of a single number. A ground robot
crossing 100 m at a realistic 1 m/s, plus waking and undocking, is over two
minutes to scene. Whoever set the sensor off has gone. A robot justified purely
on intercepting people would spend its life filming an empty driveway — a job
fixed cameras do instantly and for a fraction of the money. A robot that walks
the fence line, reads a temperature where no node is wired, checks that the shed
door is shut and photographs the gate after a windstorm earns its keep on
ordinary days, and is *also* there when something happens.

## Why

The property is big enough that checking it is a chore and small enough that
nobody does it until something has already gone wrong. Wiring a sensor to every
place worth knowing about is not worth it; walking out to every place worth
knowing about is not going to happen. A machine that does the walk is the thing
that is actually missing.

`property-watch` will know *that* something happened at the drive. It will never
know what the back of the shop looks like.

## Scope

**In scope**

- Scheduled autonomous patrol over a defined route, within a hard geofence.
- Inspection payload: camera, plus environmental sensors reaching places
  `property-watch` has no node.
- Record-on-detect, triggered by `property-watch` events, filming **from a
  standoff distance**.
- Self-docking and self-charging. A robot needing a human to plug it in is a
  robot that stops being used in week three.
- Teleoperation and a live view, for when autonomy is not trusted or not wanted.
- **A radio-quality map of the property, surveyed as a byproduct of patrol.**
  The robot already knows where it is and already drives everywhere, so
  position-tagged link measurements cost nothing but storage. Accumulated over
  repeated passes, per band, with variance kept and not just an average.
- **Comms-aware behaviour, driven by that map.** Where the robot parks to watch
  something, and where it uploads from, are chosen against measured signal
  rather than guessed. Footage is always written locally first and uploaded
  from ground known to be good.

**Deliberately not in scope**

- **Not an interceptor.** It does not approach, follow, confront, block or
  pursue a person. It observes from a distance and keeps its distance. A machine
  that moves toward people escalates situations and carries liability that a
  hobby project has no business taking on.
- **No deterrent escalation.** No siren, no strobe, no speaker challenge, no
  spotlight aimed at anyone. This was offered as an option and deliberately not
  chosen.
- **No audio recording**, default off and treated as off. See **Recording
  people** below — audio is the legally sharp edge, not video.
- **Nothing beyond the geofence.** Not down the road, not onto a neighbour's
  land, not out of sight of the property. The geofence is a privacy control as
  much as a navigation one.
- **Not a snow machine.** See **The winter problem** — this is a cleared-surface
  robot, and pretending otherwise would design the wrong thing.
- **Not load-bearing, not a tool carrier.** It carries sensors. It does not tow,
  plough, lift or mow.
- **The signal map is not a site survey for anything but the robot.** It is
  measured at robot antenna height, roughly half a metre, by a machine whose own
  body shadows its antenna. That is exactly the right data for deciding where
  *this* robot transmits from, and the wrong data for siting a mast-mounted
  access point. Do not let it be reused as one without a fresh survey at the
  real height.

## The winter problem

This belongs in the scope section rather than a footnote, because it is the
constraint that decides the machine.

SMP Robotics sells outdoor patrol robots rated to **−25 °C**, and its own
documentation requires that **patrol routes be cleared of snow** — the robot
moves on snow-free routes. That is a vendor who builds these for a living saying
the product handles *cold*, not *snow*. Independent guidance on patrol robots
adds that IP54 does not cover snow and that many units in this class are rated
0–40 °C, which simply excludes Alberta.

The real difficulties are documented and consistent: localisation degrades in
deep snow, terrain changes during a blizzard, snow hides the route surface,
obscures sensors and destroys traction.

So the honest position, written down now so it is not discovered in January:

- **Three-season autonomous**, roughly April to November.
- **Winter is cleared paths only**, or the robot sits in the garage and the
  patrol job reverts to a person.
- **Batteries are the hard part, and it is charging, not running.** Lithium
  cells — Li-ion and LiFePO4 alike — must not be *charged* below 0 °C without
  plating damage, though they discharge happily well below it. A heated battery
  compartment, or a dock that warms the pack before it accepts charge, is not a
  refinement. It is the difference between a robot and a brick.

Choosing tracks over the mower-base conversion is the right call against this
backdrop: tracks handle gravel, grass, slope and shallow snow in a way mower
wheels do not.

## Stack

Nothing chosen. The shape, subject to the survey in `plan.md`:

- **Chassis:** purpose-built, differential-drive tracks. Off-the-shelf rubber
  tracks; printed body, mounts and trays.
- **Low level:** a microcontroller owning motors, encoders, power and the
  emergency stop, so a crashed brain cannot drive the robot.
- **High level:** a single-board computer with enough GPU for on-board person
  detection — Jetson Orin Nano class. An ESP32 cannot do this, which is the
  clean break from every node in `property-watch`.
- **Navigation:** RTK GNSS as primary, since open ground defeats lidar SLAM;
  IMU and track odometry across sky-view gaps; a depth sensor for obstacles.
- **Geofence:** enforced low, below the autonomy, as a hard boundary.

## How to run

Nothing to run. This is a recorded future feature. `plan.md` holds the phasing,
and Phase 0 is a property survey that needs no hardware at all.

## Recording people

Not legal advice, and worth real advice before the camera is switched on. The
practical shape in Canada:

- **Audio is the sharp edge, not video.** Intercepting private communication is
  criminal territory, and a roving microphone is a far worse idea than a roving
  camera. Audio stays off, and the hardware should make that true rather than
  configurable.
- **Video of your own property for domestic purposes is ordinarily fine.**
  Recording past the property line — the road, a neighbour's yard — is where
  complaints and liability begin.
- **A mobile camera is different in kind from a fixed one.** A fixed camera
  points where it was aimed; a robot can be anywhere, pointed anywhere. That is
  exactly why the geofence is a privacy control here.
- **Residents are not the public.** People who live here should know the robot
  exists, what it records and how long it is kept, before it drives.

## Open questions

- **The property itself is unknown to this document.** Area, distances, slopes,
  surfaces, tree cover, where RTK has sky view. Phase 0 answers all of it, and
  nothing should be bought first.
- **Where does the dock live**, and does it have power and shelter? Dock
  approach and alignment is routinely the hardest part of an outdoor robot.
- **Budget.** A tracked build with RTK and a Jetson is not a cheap project, and
  the number shapes every choice below it.
- **Winter plan**, chosen rather than defaulted: cleared routes, garage months,
  or accept a robot that is useful two thirds of the year.
- **Who is allowed to see the footage**, and how long is it kept? Needs the same
  answer as the retention question left open in `property-watch`.
- **Does the signal map stay inside this project?** It would obviously help
  `property-watch` decide where a sensor node has coverage and where a repeater
  is needed. That is a cross-project data flow, so per `CLAUDE.md` it is a
  decision to be taken deliberately and not a convenience to be helped to.
  Nothing flows until it is asked and answered — and the height caveat above
  applies hard if it ever does.
- **Does robot control belong on WiFi at all?** Surveying the property will
  prove there are dead zones; the question is whether telemetry, commands and
  the e-stop heartbeat should be on the same patchy link as the video. A
  separate low-bandwidth radio for control is the conventional answer and a
  safety argument, not a performance one.
- **How good is good enough?** The thresholds that decide "upload from here"
  have to come from measured uplink throughput on the real hardware, not from
  dBm rules of thumb. Phase 3 produces them.
- **TPU is not on the shelf** (`filament.md`), and it is the material for track
  treads, bump trim and anything sealing. Likely needed before Phase 1.
