# Spike 01 — can radar read the front drive?

**Status:** not started. Written 2026-10-19 MDT.

Phase 0 of `plan.md`, and the gate on everything else. The platform choice waits
on this deliberately: committing a stack around a sensor that cannot do the job
is the mistake this ordering avoids.

## The question

> Mounted where it can actually be mounted, can a 24 GHz radar reliably tell a
> vehicle **approaching** from one **parking** from one **turning around and
> leaving** — without firing on the road?

Everything else about the drive node follows from the answer.

## What gets built

Deliberately minimal. No hub, no platform, no app, no classifier.

- One **ESP32** + one **HLK-LD2451**, UART at 115200.
- Firmware that does one thing: read frames and append them as CSV, with a
  millisecond timestamp. No interpretation, no thresholds, no alerting.
- Logs to SD or straight over Wi-Fi to a file on any machine. Whichever is less
  work — this gets thrown away.
- A temporary mount. Clamp, zip ties, a block of wood. Not a printed enclosure
  yet; the whole point is that the right angle is not yet known.

## Log format

One row per frame per target. Keep it dumb and wide — regret is always the
field not logged.

```csv
ts_utc_ms,target_id,distance_m,speed_kmh,direction,angle_deg,snr
```

Store UTC in the file, convert to Alberta time at display, per `CLAUDE.md`.

## How it runs

1. **Mount and aim.** Try two or three positions. Record height, angle and a
   rough sketch for each — an unrecorded aim makes the data unreadable later.
2. **Set range gating** to just inside the property line. First and best defence
   against the road.
3. **Log for a week.** Real traffic, real weather. Alberta in late October will
   also answer the cold question for free.
4. **Keep a ground-truth note** alongside. Even a rough one — *"14:05 my truck
   in, parked"*, *"18:40 someone turned around"*. Twenty labelled events make
   the difference between tuning the classifier and guessing at it.

## What it has to show

The spike passes if, from the logs:

- [ ] A vehicle is detected at the **top of the drive**, far enough out that
      "approaching" is a warning and not a surprise.
- [ ] **Approach and depart are cleanly separable** by direction and range.
- [ ] **Parking produces a recognisable signature** — track fades at close
      range, no receding track. Confirm this is distinguishable from a target
      simply lost.
- [ ] **A U-turn looks different from a park** in the logs, by dwell time and
      minimum range.
- [ ] **Road traffic is rejected** by range gating and aim — or a count of how
      many get through, which tells you the real false-alarm rate.
- [ ] Rain and snow do not flood it with phantom targets.
- [ ] **Power and Wi-Fi exist at the mounting point.** Not a radar question,
      but it sinks Phase 3 just as hard, and now is when it is cheap to find
      out.

## What it produces

- `logs/` — the raw CSV, kept. This is the asset; the firmware is not.
- `findings.md` — what the data showed, answering each box above.
- Real values for `T_park`, `T_uturn` and `R_dwell`, measured rather than
  guessed.
- A recommended mount height and angle, which is what the printed wedge gets
  designed to.
- A verdict on the platform question, with the radar's needs now known.

## If it fails

Worth knowing the fallbacks before starting, so a bad week is not a dead end:

- **Range too short / aim impossible** → two radars, or move the mount, or
  accept detection only at the near end of the drive.
- **Road traffic cannot be rejected** → add a second sensor as a gate crossing
  and require both, or go to the camera option that was set aside.
- **Park and U-turn indistinguishable** → the LD2450 (6 m, X/Y trajectory) as a
  *second*, close-range sensor over the parking area, with the LD2451 doing
  long-range approach. Each then does what it is actually built for.

Record which of these happened, even informally. A fallback chosen for a reason
written down is worth more than a working sensor nobody remembers siting.
