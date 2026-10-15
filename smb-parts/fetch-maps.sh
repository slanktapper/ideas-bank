#!/usr/bin/env bash
# The Super Mario Bros. level maps: get them, or check the ones already here.
#
#   ./fetch-maps.sh --check    # verify and measure whatever is in maps/  <-- use this
#   ./fetch-maps.sh --fetch    # download the 32 main levels from ian-albert.com
#
# --check is the one to run after dropping files into maps/ by hand. It reads
# every GIF actually present rather than assuming a filename list, so it copes
# with the sub-area maps whose names are not known up front.
#
# --fetch needs ian-albert.com to be reachable, which in a cloud session means
# the environment's network policy must allow it. See maps-source.md. It only
# knows the 32 main levels; it is not the way to get the full set.

set -uo pipefail

BASE="https://ian-albert.com/games/super_mario_bros_maps"
HERE="$(cd "$(dirname "$0")" && pwd)"
DIR="$HERE/maps"

check() {
  python3 -I - "$DIR" <<'PY'
import os, re, sys, struct

d = sys.argv[1]
if not os.path.isdir(d):
    sys.exit("no maps/ directory at %s" % d)

names = sorted(n for n in os.listdir(d) if n.lower().endswith(".gif"))
if not names:
    print("maps/ holds no GIFs yet.")
    sys.exit(1)

def natural(n):
    # mario-8-4.gif sorts after mario-8-3.gif, and mario-10-x after mario-9-x
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", n)]

good, bad = [], []
for n in sorted(names, key=natural):
    p = os.path.join(d, n)
    with open(p, "rb") as f:
        head = f.read(10)
    if head[:3] != b"GIF":
        bad.append((n, "not a GIF, starts %r" % head[:6]))
        continue
    # Width and height are bytes 6-9 of the header, little-endian uint16 each.
    # Read directly so this needs no imaging library.
    w, h = struct.unpack("<HH", head[6:10])
    if w == 0 or h == 0:
        bad.append((n, "header declares a zero dimension"))
        continue
    good.append((n, w, h, os.path.getsize(p)))

print("%-28s %8s %7s %12s" % ("file", "width", "height", "bytes"))
print("%-28s %8s %7s %12s" % ("-" * 28, "-" * 8, "-" * 7, "-" * 12))
for n, w, h, size in good:
    print("%-28s %8d %7d %12d" % (n, w, h, size))

if good:
    total = sum(g[3] for g in good)
    # A 15-tile-tall playfield at 16 px per tile is 240 px; anything else is a
    # map of something other than a standard level, which is worth seeing.
    odd_height = sorted({g[2] for g in good if g[2] != 240})
    print("\n%d GIF(s), %.1f MB total" % (len(good), total / 1e6))
    print("widest %d px, tallest %d px" % (max(g[1] for g in good),
                                           max(g[2] for g in good)))
    print("megapixels, summed: %.0f" % (sum(g[1] * g[2] for g in good) / 1e6))
    if odd_height:
        print("heights other than the standard 240 px: %s"
              % ", ".join(str(x) for x in odd_height))

# The 32 main levels are the part of the set whose names are predictable.
canon = ["mario-%d-%d.gif" % (w, l) for w in range(1, 9) for l in range(1, 5)]
have = {n.lower() for n, _, _, _ in good}
missing = [c for c in canon if c not in have]
extra = [n for n, _, _, _ in good if n.lower() not in canon]

print("\nmain levels (1-1 to 8-4): %d of 32 present" % (32 - len(missing)))
if missing:
    print("  missing: %s" % ", ".join(missing))
if extra:
    print("other maps present: %d" % len(extra))
    for n in extra:
        print("  %s" % n)

for n, why in bad:
    print("  !! %s: %s" % (n, why), file=sys.stderr)

sys.exit(1 if (bad or missing) else 0)
PY
}

fetch() {
  mkdir -p "$DIR"
  local fail=0 code out
  for w in 1 2 3 4 5 6 7 8; do for l in 1 2 3 4; do
    out="$DIR/mario-$w-$l.gif"
    if [ -s "$out" ]; then echo "have  mario-$w-$l.gif"; continue; fi
    echo -n "get   mario-$w-$l.gif ... "
    code=$(curl -fsS --retry 4 --retry-delay 2 --retry-all-errors -m 300 \
                -o "$out.part" -w "%{http_code}" "$BASE/mario-$w-$l.gif" 2>/dev/null)
    if [ "$code" = "200" ] && [ -s "$out.part" ] && \
       [ "$(head -c 3 "$out.part")" = "GIF" ]; then
      mv "$out.part" "$out"; echo "ok ($(stat -c%s "$out") bytes)"
    else
      rm -f "$out.part"; echo "FAILED (HTTP $code)"; fail=1
    fi
  done; done
  echo
  check || fail=1
  return $fail
}

case "${1:---check}" in
  --check|--report) check ;;
  --fetch)          fetch ;;
  *) echo "usage: $(basename "$0") [--check|--fetch]" >&2; exit 2 ;;
esac
