# twist-grip — print guide

Read this before spending filament. Nothing here has been printed yet, so
everything below is reasoning from `../available-tools.md` and the geometry,
not experience with this part.

## Print the coupon first

```
stl/coupon-ring.stl   37 x 48 x 16 mm
stl/coupon-body.stl   35 x 45 x 14 mm
stl/coupon-jaw.stl    32 x 13 x 12 mm
```

About 19 g all told and well under half an hour, against 145 g and several
hours for the real set. It is a 50° wedge of the actual object, cut from the
finished meshes rather than modelled to resemble them, so the walls, the
groove floor, the channel lid and every overhang are exactly what the full
part would print.

It carries all four fits that matter:

| fit | clearance as drawn | what wrong feels like |
| --- | --- | --- |
| pin in groove | 0.35 mm each side | gritty, or slop you can hear |
| jaw in channel | 0.35 mm each side | jaw rocks, or will not slide |
| lug under lip | 0.30 mm | body rattles up and down |
| ring on skirt | 0.35 mm | ring wobbles instead of turning true |

Assemble the wedge and slide the jaw through its 25° or so of travel. If it
binds, raise `FIT_SLIDE` in `params.py` by 0.05 and reprint the coupon. If it
is sloppy, lower it. Then rebuild and print the real thing.

## Material

**PETG**, from the five colours on the shelf. It is the functional default
for good reasons here: it slides on itself without the galling PLA does, it
is tough enough for a pin in a groove taking a side load, and — the one that
decides it — **it does not creep**. This object is meant to be squeezed and
left squeezed, which is precisely the load that makes PLA sag over days in a
warm room.

ABS would also do and has the chamber for it, but there is one colour of it
and no reason to spend the chamber's time.

Suggested colours, all on hand: **black** ring, **white** body, **orange**
jaws. The jaws are the moving part and want to read as separate. Any pairing
works; the renders use that one.

## Orientation

All three print flat, no supports, nothing to clean up.

| part | orientation | why |
| --- | --- | --- |
| ring | as modelled, grooves and wall upward | every cavity opens to the sky |
| **body** | **top face down**, skirt upward | the channel's lid then prints over a gap that is already there instead of bridging one |
| jaw | pin upward, flat on its base | nothing overhangs |

`build.py` already writes them in these orientations — load the STLs as they
come and do not let the slicer "optimise" them.

Two overhangs to expect, both small and both fine in PETG:

- the three lugs on the skirt stand 1.65 mm proud of it, printing as a short
  ledge over air;
- the ring's inner lip juts 1.6 mm inward at z = 3.8.

If either comes out ragged it is cosmetic — neither is a bearing surface.

## Settings

Nothing exotic. 0.4 mm nozzle, 0.2 mm layers.

- **Walls: 4.** The thinnest wall in the object is 1.6 mm, which is exactly
  four lines, so it wants to be solid perimeter rather than thin infill.
- **Infill: 25%+.** The ring and body are mostly plate; the jaws are small
  enough to print solid and should be, since the pin is cantilevered.
- **Jaws: print both.** `stl/jaw.stl` is one jaw. The mechanism needs two
  identical ones.
- Dry filament. PETG strings when damp and this part has slots everywhere for
  strings to land in.

## Assembly

No screws, no glue, no tools.

1. Slide both jaws into the body's channels from the outside, pads inward.
2. Hold them part way out, where the pins sit at about r = 48.
3. Bring the ring up over the skirt from below, with its three lip notches
   over the three lugs and the outer ends of the grooves under the pins. It
   only goes on one way round.
4. Twist. The lugs leave their notches and it is together.

From then on the cam holds the jaws in radially and the lip holds the body
down. It comes apart again by twisting back to full open and lifting — which
is deliberate, and the only position it is possible in.

## What to look at when it comes off the plate

- **The bore.** A 40 mm circle, clear, with both pads flush with it at full
  open. If a pad stands proud the jaws are not reaching their outer stop.
- **The sweep.** Half a turn, stopping positively at both ends. It should
  stop because a pin met the flat end of its groove, not because something
  wedged.
- **Holding.** Press on a jaw face with the ring part way round. It should
  not unwind; the spiral is shallow enough to lock on friction alone. If it
  creeps, the surfaces are more slippery than the 0.3 assumed and the design
  wants a detent.
- **The faces meeting.** Twisted all the way over, the two pads should land
  flat against each other, not at an angle.
