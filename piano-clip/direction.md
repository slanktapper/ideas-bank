# piano-clip

**Status:** prototype — model and fit coupons build and check clean, nothing
printed yet

## What it is

A miniature of Rob's Korg Concert C-600 that is also the clip holding the
white dust sheet on it. The sheet drapes over the piano including the acrylic
music rest; the clip saddles the top edge of that rest with the sheet over it,
two sprung blades reaching 25 mm down each face and pinching the cloth against
the acrylic. What you see from across the room is a small brown piano standing
on top of the sheet.

Scale is **one millimetre per inch** — the real cabinet is 48 in wide and the
model is 48 mm wide, 1:25.4. That was chosen so every number in `params.py`
can be checked against a tape measure in your head.

## Why

The sheet slides off. A tablecloth clip would do the job and look like a
tablecloth clip. This one does the job and looks like the thing it is holding
the sheet onto.

## The piano it is a model of

Rob gave the cabinet as 48 × 16 in. Everything else came off the photograph
rather than from a spec sheet, because the C-600 is old enough that no
retailer listing for it survives:

- **76 keys, E1–G7**, not 88. Detecting dark runs across the key bed in the
  photo found **31 black keys** in the correct 3-2-3-2 pattern, opening on a
  group of three and closing on a single — which is exactly E1–G7. The
  independent check is that an 88-key bed is 1220 mm on its own and could not
  fit inside a 1219 mm cabinet.
- **Scale from the photo:** first to last black key centre is 2641 px, which
  is six octaves, 990 mm — so 2.67 px/mm. That predicts a 45-white-key bed of
  2830 px; the measured bed is 2823 px. The photograph and the arithmetic
  agree to a quarter of a percent.
- **Key bed 1061 mm** in a 1219 mm cabinet, so a 79 mm cheek each side.
- The **music rest is smoked translucent acrylic** in a black base trough, not
  wood. You can see the wall panelling through it.

`build.py` regenerates the 31 sharps from the note pattern itself — a sharp
sits above every white key except E and B — so the count is a consequence of
the keyboard rather than an assertion about it. It comes out at 31.

## Scope

**What it does.** Grips the music rest through the sheet, 25 mm deep, and
looks like the piano while doing it.

**What it deliberately does not do.**

- **Model the stand.** No leg panels, no pedal box. The cabinet is the case
  only — lid, control strip, keyboard, key slip — because that is what reads
  at this size and because the two spring blades occupy the space underneath.
- **Separate the white keys.** At 0.93 mm a key, the groove between two of
  them would be 0.1 mm, a quarter of a nozzle line. The keyboard is a single
  white band and reads as a keyboard from the black key grouping, which is
  what the eye uses anyway.
- **Grip anything but the music rest.** It is sized for one thickness of
  acrylic plus two layers of cotton. It is not a general-purpose clip.
- **Hold the whole sheet.** One clip anchors one point. How many it takes is
  Rob's call once one exists.

## Three features are deliberately fatter than scale

Each is a lie about the piano, told because the nozzle cannot do otherwise,
and recorded so it can be argued with:

| Feature | At scale | Printed | Over scale |
| --- | --- | --- | --- |
| Black keys | 0.374 mm | 0.55 mm | 1.47× |
| Music rest panel | 0.177 mm | 1.20 mm | 6.77× |
| Key band | — | 0.80 mm | — |

The music rest is the big one, and it is why the rest looks slab-like next to
the photograph. Below about 1.2 mm it would not print as a wall at all.

## How the clip works

Two blades under the cabinet, 44 mm wide and 1.2 mm thick — three perimeters
at 0.4 mm — hanging 25 mm. The numbers that matter:

    gripping gap   5.00 mm   = measured stack 7.0 - 2 x 1.0 preload
    plain face     5.70 mm   held clear, so the ribs are what touch
    mouth          8.90 mm   at the flared tips, feeds itself on over fabric
    deflection     1.00 mm   a blade, in use
    strain         0.288 %   against a 0.5 % long-term limit for PLA
    force          3.04 N    a blade, 6.08 N to spread

Three ribs across each inner face at 5.5, 11 and 16.5 mm down are the only
things that contact. The plain face stands 0.35 mm clear of them on purpose,
so that the gripping gap is a number with one meaning. Both faces of the music
rest carry fabric when the sheet is on, so nothing the clip touches is bare
acrylic and the ribs cannot scratch it.

The root is thickened to 2.15 mm over the top 2.4 mm so the blade does not
hinge on a sharp corner, and the tips flare outward so the clip feeds itself
on rather than catching the cloth.

## The thickness it grips, and how it was got

**7.0 mm, measured 2026-10-14 MDT.** Rob pinched the music rest through the
dust sheet and read the gap between his fingers. That is the whole stack —
acrylic plus both layers of cloth, squeezed about as hard as a clip squeezes
it — so it is exactly what the blades have to swallow, with nothing inferred
in between.

It replaced a worse number. This file first carried 4.5 mm of acrylic,
estimated off the original photograph, which put the stack at 5.1 mm. That
was 1.9 mm thin — a glancing-angle measurement of a translucent edge is about
the least reliable thing a photograph offers. Working back from 7 mm, the
acrylic is nearer 6.2 mm, and `MREST_T_REAL` now carries that figure purely
so the model *looks* right. Nothing in the clip reads it any more; the clip
is sized from `GRIPPED_T`, the thing actually measured.

The general point is worth keeping: the model is full of dimensions scaled off
a photograph, and they are fine for a shape nobody has to fit. The one
dimension that had to fit something real was the one to go and measure.

## The test print

`build.py` writes three fit coupons beside the clip. Each is the real grip and
none of the piano — full 44 mm blade width and the full 25 mm reach, because
clamping force scales with blade width and a narrow coupon would feel wrong in
exactly the way that matters. They drop the cabinet, the keyboard and the
music rest: about three quarters of the print time and all of the colour
changes.

| Coupon | Pips | Gap | Preload | Force a blade | Strain |
| --- | --- | --- | --- | --- | --- |
| `coupon-1.stl` | 1 | 5.80 mm | 0.6 mm | 1.82 N | 0.173 % |
| `coupon-2.stl` | 2 | 5.00 mm | 1.0 mm | 3.04 N | 0.288 % |
| `coupon-3.stl` | 3 | 4.20 mm | 1.4 mm | 4.26 N | 0.403 % |

Pips on the spine count the coupon, lowest preload first, so three of them on
the bench cannot be confused once they are off the plate. All three sit under
the 0.5 % long-term limit, so any of them is a legitimate answer — the point
is to pick the grip by feel on the real music rest rather than argue about it
here. Print them in Cocoa Brown, not whatever happens to be loaded: the spring
rate is the material's, so a coupon in some other PLA answers a different
question.

Whichever wins, set `PRELOAD` in `params.py` to its figure and rebuild.

## Material

PLA throughout, three colours, all on the shelf per `filament.md`:

| Part | Filament |
| --- | --- |
| Cabinet, music rest, blades | PLA Basic **Cocoa Brown** 10802 |
| White keys | PLA Basic **Jade White** |
| Black keys | PLA Basic **Black** |

**This is a compromise and it is worth knowing about.** A spring held open for
months wants PETG, which does not creep the way PLA does. There is no brown
PETG — Cocoa Brown is PLA and it is the only brown in the building. Choosing
brown therefore chooses PLA for the whole part, since mixing PLA and PETG in
one print gives a part that delaminates at the boundary by design.

The blades are sized to buy that back: at 0.288 % strain the part is well
inside where PLA creeps quickly. It will still relax somewhat over a year of
sitting open. If the grip goes slack, the honest fix is black or white PETG
and no brown.

## Stack

Python. `trimesh` with `manifold3d` for the booleans, `shapely` for the
extruded side-view profiles, and the renderer in `../3d-tools`. No CAD
application, no GUI.

## How to run

```bash
cd piano-clip
python3 -m pip install -r requirements.txt
python3 build.py            # 22 checks, 3 STLs, 5 renders
```

It writes nothing if a check fails and exits non-zero. STLs land in `stl/`,
one per filament colour, ready to be loaded as three parts of one object.

`print-guide.md` is the one to read before printing.

## What the checks are for

Two of them exist because something was wrong and nothing was asking:

- **The mouth is wider than the music rest plus fabric.** The first version of
  this check computed the mouth as gap plus flare and forgot that the flare is
  measured from the plain inner face, which stands clear of the ribs. It
  understated the mouth by 0.7 mm. Sectioning the profile and reading the real
  gap down the blade is what caught it.
- **The ribs are the narrowest point.** Without this, a change to `RIB_H` can
  silently make the plain face the gripping surface, and then `SLOT_GAP` means
  nothing.

## Open questions

- **The proportions are leg-heavy.** 25 mm of grip under an 11 mm cabinet
  means the clip is two-thirds skirt. It still reads as an upright piano's
  lower panel, but 15–18 mm of grip would look more like the photograph and
  would still hold a bedsheet. Rob asked for 25 and 25 is what is built.
- **Which coupon wins.** Until one is printed and tried, `PRELOAD = 1.0` is a
  calculation, not a result.
- **Print orientation is a genuine trade-off**, and `print-guide.md` argues it
  rather than settling it. Standing on one end is right for the spring and
  wrong for the colour changes.
- **Solid blades, not fingers.** Splitting each blade into two or three
  narrower fingers would lower the force and let them conform to a rest that
  is not perfectly flat. Worth it only if the solid blade turns out to grip
  unevenly.
- **How many clips.** One anchors one point in the middle. The ends of the
  sheet are still free.
