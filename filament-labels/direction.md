# filament-labels

**Status:** prototype

## What it is

Three tags that say **PLA**, **PETG** and **ABS**, to tape to the side of the bins
the filament lives in. Each is an 80 × 30 × 3.0 mm rounded slab in two colours:
a solid coloured body — black, indigo purple or cocoa brown — with the word in
jade white. At 3 mm it is a plaque rather than a sticker: rigid, no flex,
nothing for a knocked corner to peel back.

Colour carries the meaning, which is the point of doing it this way round. A
black tag is ABS from across the workshop, before the word is legible.

They print face down, so the face you read is the one that was against the plate
and carries its texture. The lettering is not engraved or raised — it is the
second filament coming through the white, flush with the surface, so there is no
relief to catch dust and nothing to rub off.

The models are generated from `build.py`; there is no mesh to edit by hand. Change
a number in `params.py` and every tag follows, lettering included.

## Why

Rob's filament holders have no way of saying what is in them. A bin of white
filament is a bin of white filament whether the white is PLA or PETG, and the two
want different temperatures, different bed prep and different expectations about
what the part will do at 70 °C. The label has to survive being handled, so a
printed tag beats a paper one; and since the printer has eight slots, a two-colour
tag costs an evening on the plate rather than a trip to a label maker.

## Scope

**It does:** three tags, one per material, at one size, generated from one set of
parameters. Colour and material come from `../filament.md`, which is the only
stock list. It also lays out a plate, because these are printed in batches of one
type — 24 fit, and a batch costs no more purge than a single tag does.

**It deliberately does not:**

- Carry anything but the material name. No temperatures, no brand, no colour
  swatch, no QR code. A bin label is read from across a workshop, and every extra
  thing on it costs letter height.
- Mount. It is taped on. No clips, no magnets, no hooks — those depend on the bin,
  and the bin is not modelled here.
- Cover materials that are not on the shelf. There is no ASA, TPU, PVA, PC or
  nylon tag, because `../filament.md` says there is none of it to put in a bin.
  Adding one is a row in `params.py`.

## The two decisions worth knowing

**Everything is PLA, including the tag that says PETG.** The letter colours Rob
asked for — indigo purple and cocoa brown — exist only in PLA. The white he asked
for exists only in PETG: `../filament.md` is explicit that there is no plain white
PLA, and that the white in stock is PETG. Those two cannot be one part.
`../available-tools.md` notes that PLA and PETG barely bond, and leans on exactly
that to make breakaway supports — so a PLA letter set into a PETG tag is a part
designed to shed its lettering. The whole set is PLA, and the background is jade
white, which is the only pale PLA on the shelf. A tag reading "PETG" printed in
PLA is a label, not a sample, so this costs nothing.

**The white is the letters, and that is why it is 0.80 mm.** The number has
survived three rearrangements of this design, because it is about one interface
rather than about the layout: a white letter with a dark body behind it. A pale
filament over a dark one at 0.40 mm reads grey. The working minimum is about
0.60 mm, and bright white over black — the ABS tag — wants 0.80 mm. Printing
face-down makes it worse rather than better: the first layer is squashed into the
plate texture, so in the valleys the white is thinner than its nominal 0.20 mm. So
the letters are 4 layers deep, with 2.20 mm of colour over the back of them.

What kept changing is how much white there is, and this arrangement wants the
least by a distance:

| | Jade white, set of three |
| --- | --- |
| White body, coloured letters | 9.5 g |
| White skin over the whole face | 5.6 g |
| **White letters on a coloured body** | **1.5 g** |

The background no longer costs any white at all, because the background is no
longer white. `build.py` prints what 2, 3, 4 and 5 layers each cost, so dropping to
3 is one number away — though at 1.5 g there is now very little to save.

Thickness does not touch any of this. The letters are set by opacity, so making the
tag thicker spends body colour and no more white.

## Stack

Python 3.10+, `numpy` + `trimesh` with the `manifold3d` boolean engine, `shapely`
for the 2D work. Lettering comes from `../3d-tools/text3d.py` and renders from
`../3d-tools/render.py`. No GUI, no CAD application.

`text3d.py` and the Outfit Bold typeface were moved into `../3d-tools` for this
project — they were `cactus-pot`'s, and a second consumer is what the shared folder
exists for. The pot's STL is unchanged by the move, byte for byte, which is how
that was checked.

    python3 -m pip install -r requirements.txt

## How to run

    python3 build.py                # stl/ and renders/
    python3 build.py --no-renders   # just the STLs, a couple of seconds
    python3 test_fit.py             # 45 checks, about 2 seconds

`print-guide.md` is what to do with the files once they exist.

## The numbers that matter

| | |
| --- | --- |
| `TAG_W`, `TAG_H`, `TAG_T` | 80 × 30 × 3.00 mm — 15 layers at 0.20 |
| `WHITE_D` | 0.80 mm — how deep the white letters run, 4 layers |
| `COLOUR_BEHIND` | 2.20 mm of body colour over the back of the letters |
| `CORNER_R` | 4.0 mm, so a knocked corner does not lift the tape |
| cap height | 18.12 mm, solved — not set by hand. See below |
| `MARGIN_X`, `MARGIN_Y` | 7.0 and 5.0 mm of clear tag around the word |
| `BED_W`, `BED_D` | 300 × 320 mm — the **dual-nozzle** envelope, 24 tags a plate |

**The cap height is solved, and "PETG" is what solves it.** All three words are set
at one size, the largest at which the widest of them still fits the panel, so the
set reads as a set. At 80 mm wide that size is 18.12 mm, and it is the *width* of
PETG that binds — the height would allow 19.40. Make the tag narrower and all three
words shrink together; make it taller and nothing changes until height becomes the
binding constraint.

The three also share a baseline, because each word is centred on its cap box rather
than on its ink. ABS and PETG have round letters that overshoot the cap line and
baseline by 0.28 mm; PLA does not. Centring on ink would put the three baselines at
three different heights, which is visible when the tags are side by side.

## Open questions

- **Jade white is not white.** It is a soft off-white with a green cast. As
  lettering on a dark body it has more contrast behind it than it did as a
  background, so it should carry — but nobody has held one yet. If it reads dirty,
  the alternative on the shelf is milky pink PLA, which is worse, or ordering white
  PLA.
- **The letters are separate bodies.** One per letter, by definition, since letters
  do not touch. Each sits flat on the plate from layer one, welds PLA-to-PLA to the
  colour around it, and has 2.20 mm of colour roofed over it, so there is nowhere
  for one to go. Worth watching on the first print all the same: it is the one
  thing this arrangement does that the previous two did not.
- **Does 0.80 mm actually hide black?** It should, and it matters more now than it
  did: the white is the thing being read, not the thing being read against. Grey
  letters on black would be the whole label failing rather than a slightly dingy
  background. The first tag printed settles it, and the answer is a number in
  `params.py` either way. Print the ABS tag first — black is the worst case.
- **Tape, or something better.** Taped on is what was asked for, and 3 mm makes it
  more of a question than 1.2 mm did: a thicker tag stands further off the bin, so a
  knock has more leverage on the adhesive. Nothing has been changed for it, because
  the tag being rigid also means it will not peel progressively the way a thin one
  does — it either holds or it comes off whole. If it comes off, the cheap fix is a
  3M VHB square; the expensive one is modelling the bin and clipping on.
- **No PETG or ABS tag in its own material.** There is an argument that the PETG tag
  should be printed in PETG so the label is also a sample of the material. It cannot
  be, for the colour reasons above, and it would mean a separate job in a different
  material for one tag. Noted and rejected, not forgotten.
- **How many of each.** Unanswered, and it does not need answering in code: a
  plate holds 24 of one type and the purge is the same at any count, so the number
  is whatever Rob wants on the day. `plate_layout()` fills the plate; printing six
  means deleting eighteen in the slicer.
- **The other bins.** This does three materials because that is what is on the shelf.
  Mistletoe green, silk gold and the rest are colours rather than materials, and a
  colour label is a different idea — probably a swatch, not a word.
