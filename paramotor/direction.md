# paramotor

**Status:** idea

## What it is
Research into powered paragliding (PPG) for one specific pilot: 6'8" (203 cm),
285 lb (129 kg), flying in Alberta. This is deliberately not a general "how to get
into paramotoring" guide. Nearly all published PPG advice — thrust figures, wing
sizes, harness fit, training expectations — assumes a pilot somewhere around
75–95 kg and 175–185 cm. That pilot is not this pilot, and almost every number
changes as a result.

The question the project exists to answer: **is PPG viable at this size, what
equipment actually fits, and what does the path to flying legally in Alberta look
like?**

## Why
The size question gets a lazy answer everywhere it is asked online — usually some
version of "sure, you just need a bigger motor." That is roughly a third of the
truth. The binding constraints turn out to be the *wing's* certified weight range,
the *frame's* published maximum pilot weight, the *reserve's* certified suspended
load, and harness geometry for a 203 cm torso — in that order. Working through it
once, with the actual numbers written down and sourced, is worth more than
re-litigating it with every dealer.

Alberta adds a second complication that generic advice never covers: field
elevations here run roughly 2,400–3,600 ft, and summer density altitude regularly
puts a heavy pilot at the edge of the thrust they need.

## Scope
What this does:

- Work out all-up weight and what it gates: wing size, thrust, reserve, frame rating.
- Identify specific makes and models that publish figures covering this pilot,
  and name the ones that explicitly do not.
- Cover the Canadian regulatory path (Transport Canada ultralight permit,
  registration, insurance) and Alberta training options.
- Record what things cost, and where the size premium falls.
- Keep sources attached so a stale figure can be re-checked.

What this deliberately does not do:

- Not flight instruction. Nothing here substitutes for a school, and no conclusion
  in this folder should be treated as clearance to fly.
- Not a build project. No frame fabrication, no engine work, no software.
- Not a general PPG buyer's guide for other people.

## Stack
Markdown notes and sources. No tooling. If it ever wants a weight/thrust
calculator or a spec comparison table, the stack gets picked then.

## How to run
Nothing to run. Read in this order:

- `sizing.md` — **the core.** All-up weight, and the four constraints it drives.
  Start here; everything else follows from these numbers.
- `gear.md` — engines, frames, wings, harness and reserve, filtered to what fits.
- `canada.md` — Transport Canada requirements, training path, Alberta schools.
- `costs.md` — budget, the size premium, and buying used.
- `verify.md` — figures taken from secondary sources that need confirming before
  any money moves.

## Open questions
- **Foot launch or wheels?** Foot launch is the constrained path (frame pilot-weight
  ratings, running with ~80 lb on your back). A trike or quad removes both problems
  but changes the sport, the cost, and where you can fly from. Not decided.
- **Does a school here have gear that fits?** Training is done on the school's
  equipment. If their machines and wings are rated to 120 kg pilots, the training
  question is upstream of the buying question. Unresolved — needs a phone call.
- **Is weight a fixed input or a variable?** Every constraint in `sizing.md` is a
  function of all-up weight, and the options widen sharply below about 120 kg pilot
  weight. Recorded here as a factual lever, not advice.
- Do the Alberta density-altitude figures need real measurement rather than the
  rule-of-thumb used in `sizing.md`?
