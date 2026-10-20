# stream-director

**Status:** idea

## What it is

A control layer over OBS Studio, driven from a phone. OBS does the capture,
compositing and encoding — the job it is already good at. `stream-director` is the
thing that sits beside it and changes the picture on command, so that adjusting a
layout mid-game does not mean alt-tabbing out of the game.

Two tiers of control, deliberately:

1. **Fast path** — a page of buttons on the phone. Scene cuts, source mute, layout
   presets. Deterministic, sub-100 ms, no model in the loop.
2. **Claude path** — talk or type to Claude on the phone. "Crop cam 3 tighter, it's
   showing too much desk." "Cam 2's audio is hot, drop it 6 dB." "Two-up with the
   game big and the face cam bottom-right." Claude resolves that into
   obs-websocket calls.

The second tier is the point of the project. The first tier exists because the
second cannot be fast enough.

## Why

Gaming on one machine, streaming from another, with four phone cameras pointed at
different things. Every layout tweak currently costs a trip out of the game — which
in practice means the layout never gets tweaked, and the shot stays wrong for the
whole session. Voice is the only input channel not already occupied by the game.

## Scope

### What it does

- Holds a persistent obs-websocket v5 connection to OBS on the streaming laptop.
- Exposes OBS operations as a small, well-named tool surface: scene switching,
  source visibility, transforms **including crop**, filters, audio levels and
  per-source sync offsets, record/stream start-stop.
- Serves a phone-facing web page over Tailscale: mic button, text box, and the
  fast-path buttons.
- Calls the Claude API with that tool surface defined, and applies what comes back.
- Named layout presets, so "go two-up" is one call rather than six transforms.
- Per-source sync offset management, because four wifi cameras will not arrive in
  step.

### What it deliberately does not do

- **It does not replace OBS.** No compositor, no encoder, no capture code. That
  was the alternative design and it is a 1–2 year project; this is a 1–3 week one.
- **It is not a live switcher.** The Claude path is 2–6 seconds end to end. Cuts
  belong on the fast path. Anything needing frame accuracy is out of scope.
- **It does not manage the cameras' own apps.** Whatever is serving video from each
  Android phone is configured on that phone.
- No cloud component. Nothing is internet-facing; Tailscale is the whole access
  story.

## The hardware chain

Settled as of 2026-10-19 MDT:

| Link | Decision |
| --- | --- |
| Gaming PC → laptop | **Cheap USB3 UVC HDMI dongle** to start. Accepts 1080p30 and poor colour to prove the pipeline; upgrade path is a Cam Link 4K / HD60 X (~$120–150) or NDI over wired LAN. |
| Android cams → laptop | 2–4 phones over **5 GHz wifi**. 2.4 GHz will not carry four streams. |
| Per-cam resolution | **720p** is the realistic target, not 1080p. |
| Phone camera mounts | Clamps already bought off Amazon. Not a build item. |
| Laptop encode | Hardware encode (NVENC/QSV) is **mandatory**, not an optimisation — see the load note below. |

A laptop HDMI port is output-only, which is why the dongle exists; the gaming PC
cannot simply be plugged into the laptop.

### The load that will bite first

The laptop simultaneously decodes four network camera streams, ingests one USB
capture device, composites five sources, and encodes the result. The four decodes
are the hidden cost and the most likely first failure. Expect to discover a source
count ceiling and design the layout presets around it.

### Camera latency is not uniform

Each phone lands with 150–500 ms of latency, and **a different amount per phone**.
Three distinct problems hide behind that one number:

| Problem | Tractable? |
| --- | --- |
| **Static offset** — each source sits at its own fixed lag | Yes. Measure once, correct permanently. |
| **Clock drift** — phone and laptop clocks differ by tens of ppm, so alignment decays over a session | Partly. Needs re-nudging, maybe hourly. |
| **Jitter / rebuffering** — a congested channel makes latency jump, not sit still | No. Not fixable with offsets at all. |

**Correction only ever adds delay.** Nothing can make a late source early, so
aligning sources means delaying all of them to match the worst one. The program
output therefore sits at the latency of the laggiest camera. Acceptable: viewers do
not care about absolute latency, and Rob plays off the gaming PC's own monitor, not
off the OBS preview.

Two different OBS mechanisms, routinely confused:

- **Render Delay** — a video filter, milliseconds. The one for matching camera video
  to camera video.
- **Sync Offset** in Advanced Audio Properties — audio only, for matching a source's
  own audio to its own video.

Both are settable over obs-websocket, so the daemon owns them.

### Sync only matters between some pairs

Not every source needs aligning, which makes this much smaller than it first looks:

| Pair | Tolerance | Why |
| --- | --- | --- |
| Mic ↔ face cam | **Tight** | Lip sync. Detectable almost immediately; distracting past ~100 ms. |
| Game ↔ mic | Moderate | A reaction should land with the thing reacted to. |
| Overhead hand cam ↔ game | Loose | Keypress-to-response looks odd at 300 ms but survives. |
| Wide / room shot | **Irrelevant** | Unobservable. |

**Design rule that follows: the face cam goes on USB, and wifi is reserved for the
cams whose sync does not matter.** DroidCam and Camo both support USB tethering —
~50–100 ms and, critically, *stable*: no jitter, no rebuffering, no drift to chase.
The sources where sync matters get the reliable transport; a hiccup on a loose room
cam costs nothing.

Worth evaluating USB for **all four**, since it deletes the drift and jitter
problems outright rather than managing them. Open question: USB bandwidth and port
count on the laptop with four phones at 720p through a hub.

### Calibration routine

Point every camera at one millisecond-resolution stopwatch, capture a few seconds of
program output, step through frames, read each camera's displayed time. The
differences are the offsets.

Automatable, and a good fit for this project: the daemon renders a high-contrast
timecode on the laptop screen, pulls a screenshot of each source over
obs-websocket, reads the value off each, computes offsets and writes them back as
Render Delay values. Surfaced as a one-tap **recalibrate** on the phone page, which
is also the answer to drift.

## Stack

Not chosen yet. Decisions pending, in rough order of how much they constrain
everything else:

- Language and runtime for the daemon.
- obs-websocket v5 client library.
- How the mic button gets to text — on-device speech recognition in the browser, or
  audio uploaded to the daemon and transcribed server-side.
- Claude API tool-calling loop; model choice.

Per `CLAUDE.md`, no stack gets picked silently — this section gets filled in with
an actual decision before the first line of code.

## How to run

Nothing to run yet.

## Android camera source options

Unresolved. Three candidates, cheapest-first:

| Option | Trade |
| --- | --- |
| IP Webcam | Free. RTSP/MJPEG into an OBS media source. Highest latency. |
| DroidCam OBS | Proper OBS source type, lower latency. Paid for HD. |
| Camo | Best image quality. Paid per device, so 4 cams is the expensive answer. |

Worth testing IP Webcam first on two phones before paying for anything, since the
latency figure is the thing that decides it and it depends on this wifi.

## Open questions

- **Stack**, as above.
- **Which Android camera app**, pending a two-phone latency test.
- **How many cameras the laptop actually sustains.** Four is the ask; the real
  number comes from measurement.
- **USB or wifi for the cameras.** USB removes drift and jitter entirely; the
  constraint is laptop ports and bandwidth at four phones. Needs testing.
- **Does the fast path need to be hardware?** A phone page of buttons may be enough,
  or a Stream Deck may turn out to be the right answer for cuts.
- **Does Claude need to see the preview?** Reading OBS state is enough for "crop cam
  3 tighter" only if the model knows what the shot currently looks like. Pulling a
  screenshot of a source over obs-websocket and passing it in is possible, and would
  change the quality of the adjustments a lot. Not scoped yet.
- **Undo.** A misheard instruction that wrecks the layout mid-stream needs a one-tap
  revert. Transform snapshots before each Claude-applied change would cover it.

## Printing and fabrication

Camera mounts are bought, so there is nothing to print right now. Rob has said he
likes the printed option, so raise it when a physical problem comes up rather than
defaulting to buying — cable management, a dongle or capture-device holder, a laptop
stand with airflow for the encode load, a labelled cam-number marker from the vinyl
cutter. See `available-tools.md`.
