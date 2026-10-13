# wire-tags — print guide

Everything here assumes the Bambu Lab H2D, a 0.4 mm nozzle and **0.20 mm
layers**. The layer height is not a free choice: `TEXT_H` is 0.60 mm so the
lettering is exactly three layers. Slice at 0.16 or 0.28 and the colour change
lands between layers, and the letters come out a layer thick or four.

## Filament

**PETG Basic, both colours.** PLA is the wrong material here and it is worth
saying why: the clip is a snap arm, and PLA snap arms go brittle and crack —
usually on the second or third fit, after you have decided the design works.
PETG takes the spread, and at ~80 °C it does not care about a car dashboard or
a sunny window either.

From `../filament.md`, PETG Basic is on the shelf in **yellow, reflex blue,
orange, white and black**. Any pair works; the renders use reflex blue with
white lettering. White or yellow lettering on a dark body is what reads across
a room. There is no need to match body colours between tags — a colour per
cable family is free, and it is the fastest way to find a lead in a bundle.

## Files

Each tag is **two STLs**, and it needs both:

| File | Filament | What it is |
| --- | --- | --- |
| `<name>-<d>mm-body.stl` | body colour | the plate and both clips |
| `<name>-<d>mm-text.stl` | lettering colour | the word, 0.60 mm thick |

They are modelled in one coordinate system, so they land on top of each other
with no manual positioning.

**In Bambu Studio**, load `…-body.stl`, then right-click the object →
**Add part → Load…** and pick `…-text.stl`. That makes one *multi-part
object*; click the text part and assign it the second filament. Dragging both
files in at once and answering yes to *"Load these files as a single object
with multiple parts?"* does the same thing. (PrusaSlicer calls it the same;
this is per-part filament assignment, not colour painting.)

The colour change is in the first three layers only, so one purge covers the
whole plate however many tags are on it. **Print the set in one job**: eight
tags cost barely more purge than one.

## Slicer settings

| Setting | Value | Why |
| --- | --- | --- |
| Layer height | 0.20 mm | `TEXT_H` is three of them |
| Walls | 4 | `WALL` is 1.60 mm = 4 × 0.4; the clip is all perimeter |
| Top / bottom | 4 / 4 | the plate is only 2.4 mm thick |
| Infill | 15% | there is almost no infill in a part this size |
| **Supports** | **off** | nothing on the part overhangs past 45° — `test_fit.py` measures it. If the slicer wants supports, something in `params.py` moved |
| Brim | off | the plate is a 14 mm wide flat face |
| Seam | rear or aligned | a seam blob on a lip is a lump in the snap |

Each tag is 1.7–2.1 cm³ — a few minutes and a couple of grams.

## Print the fit coupon first

`fit-coupon.stl` is one part in one colour, 82 × 18 mm, about ten minutes.

It carries five clips at the nominal diameter **−0.4, −0.2, 0.0, +0.2, +0.4**,
engraved on the top face beside each station, with the mouths alternating so
one coupon tests both hands. Each station is a whole tag's worth of geometry —
the mouth, the wall and the ride height move with the bore, not just the hole.

1. Print it in the filament you will use for the tags. A different brand of
   PETG is a different answer.
2. Push the real cable into each station.
3. The one you want **snaps in with a click, holds when you shake it, and
   comes off when you mean it.** Too tight is a station that needs two thumbs;
   too loose is one the cable slides along.
4. Build the tags at that station's offset:
   `python3 build.py --label USB-C --diameter 4.7` for a 4.5 mm cable that
   wanted +0.2.

If every station is tight, raise `FIT` in `params.py` by the step that worked
and rerun `test_fit.py` — that is the number the coupon exists to find, and
once it is right every future tag inherits it.

## Fitting a tag

Lay the cable across both clips and **press it down and sideways** — the
mouths are aimed 46° up and out, and they are aimed opposite ways, so the
cable goes into one clip and then the other rather than both at once. It will
not drop in from straight above; that is what stops it dropping out again.

To remove, roll the tag off the cable the way it went on. Do not lever it off
with a screwdriver: the lips are 1.6 mm of PETG and they will take a cable,
not a lever.

## What to check on the first print

- The lettering recess is **flush** — a letter standing proud means the two
  parts were not loaded as one object.
- The bore roof is clean. A drooped ceiling means supports were left on, or
  the layer height moved.
- The lips are sharp, not stringy. Stringing across the mouth is a dry-filament
  problem, not a model problem.
- The clip holds the cable **at both ends**. If one end holds and the other
  does not, the cable is not the diameter you thought it was — measure it with
  calipers and build that size.
