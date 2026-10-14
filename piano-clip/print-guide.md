# piano-clip — print guide

Read this before slicing. The short version: **print the coupons first, standing
on end, and do not print the finished clip until one of them has been on the
music rest.**

## Filament

All PLA, all on the shelf per `filament.md`:

| STL | Filament |
| --- | --- |
| `piano-clip-body.stl` | PLA Basic **Cocoa Brown** 10802 |
| `piano-clip-white.stl` | PLA Basic **Jade White** |
| `piano-clip-black.stl` | PLA Basic **Black** |
| `coupon-1/2/3.stl` | Cocoa Brown — see below |

Print the coupons in **Cocoa Brown specifically**, not whatever is loaded. The
spring rate is a property of the material, so a coupon in some other PLA
answers a question nobody asked.

## Step 1 — the coupons

Three of them, distinguished by pips on the spine, lowest preload first:

| Coupon | Pips | Gap | Preload | Force a blade | Strain |
| --- | --- | --- | --- | --- | --- |
| `coupon-1.stl` | 1 | 5.80 mm | 0.6 mm | 1.82 N | 0.173 % |
| `coupon-2.stl` | 2 | 5.00 mm | 1.0 mm | 3.04 N | 0.288 % |
| `coupon-3.stl` | 3 | 4.20 mm | 1.4 mm | 4.26 N | 0.403 % |

All three are inside the 0.5 % long-term strain limit, so any of them is a
legitimate answer. Print all three — together they are about 9 g.

**Orientation: stand them on one end**, so a blade's length lies in the layer
plane. The footprint is small, about 100 mm², so give them a brim. This is the
orientation that matters most and the reasoning is in the next section.

Then put each one on the music rest over the dust sheet and pick the one that
holds without being a fight to fit. Set `PRELOAD` in `params.py` to that
coupon's figure and run `python3 build.py` again.

If all three slide, the stack is thinner than the 7 mm measured and the fix is
to re-measure, not to guess upward. If none will go on, it is thicker.

## Step 2 — orientation for the finished clip

This is a genuine trade-off and it is worth understanding rather than
following.

A printed part is weakest **between** layers. The thing to avoid is a stress
that runs along the build axis, because then every layer boundary is a crack
across the load path. In this part the stress that matters runs along a
blade's length.

**Standing on one end** — build axis along the keyboard. The blade's length
and its bending direction both lie in the layer plane, so it flexes in the
strongest mode available and no layer boundary is loaded at all. The slot
prints as a plain vertical slit and nothing needs support. This is the right
answer for the spring, and it is why the coupons go this way.

The trouble is colour. The keyboard then runs *along the build axis*, so
nearly every layer through the key bed contains a colour boundary: about 209
layers with a brown-to-white change and 85 of those with black as well, call
it 290 tool changes. At even 0.3 g of purge each that is 88 g thrown away for
a 13.6 g part.

**Lying on its back** — build axis through the piano's depth. The keyboard now
sits inside about 18 layers, so the count falls to roughly 47 changes. The
spring is still acceptable, because bending a plate whose thickness is the
build direction still puts each layer in tension along its own plane. But the
front blade is then a 44 × 25 mm shelf floating 12 mm above the bed, and it
needs a support block under the whole of it.

### What to actually do

**Print the body standing on end in Cocoa Brown, and the keyboard flat and
separately**, then glue the keyboard into its recess.

The two key STLs already form a self-contained strip — the white band is
41.8 × 5.7 × 0.8 mm with the black keys sitting 0.35 mm proud of it — and laid
flat it is about six layers, of which only the top two carry black. That is
roughly **three tool changes for the whole keyboard**, against 290.

It buys the best spring orientation, no support anywhere, and almost no purge,
at the cost of one glue joint. The joint carries nothing: the keyboard is
decoration sitting in a recess, and the clip would work with it missing.

If a single-piece print is wanted anyway, lay it on its back and accept the
support block and the purge. Do not print it standing as it is used — that is
the one orientation that loads the layer boundaries directly.

## Settings

Nothing exotic. Defaults for PLA Basic, plus:

- **0.2 mm layers.** 1.2 mm of blade is six layers; three perimeters at 0.4 mm
  means the blade is entirely perimeter with no infill, which is what makes
  the spring rate predictable.
- **Walls: 3.** Any more and the blade is still three because that is all the
  thickness there is — but the cabinet benefits.
- **Infill 15 %** for the cabinet. It carries nothing.
- **Brim** on anything standing on end.
- **No supports** on the recommended route. If you lay it on its back instead,
  support only the front blade, and use a PETG interface layer under it — PLA
  and PETG barely bond, so it peels away cleanly. There is no dedicated
  support material on the shelf and none is needed for this.

## What to look at on the first part off the plate

- **Do the blades spring back?** Spread them by hand and let go. They should
  return. If a blade stays bent, the layer adhesion is poor — raise the
  temperature rather than thickening the blade.
- **Are the ribs there?** Three per face, 0.35 mm proud, at 5.5, 11 and
  16.5 mm down. They are the only part that touches, so if they printed
  rounded off the gap is wrong by up to 0.7 mm.
- **Do the black keys read?** They are 0.55 mm wide, 1.47× over scale already,
  and they are the feature most likely to come out ragged.
