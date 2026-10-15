#!/usr/bin/env bash
# Fetch the 32 Super Mario Bros. level maps into smb-parts/maps/.
#
# Needs ian-albert.com to be reachable. In a cloud session that means the
# environment's network policy must allow the host; see maps-source.md.
#
#   ./fetch-maps.sh            # fetch missing maps, then report dimensions
#   ./fetch-maps.sh --report   # report dimensions of what is already here
#
# Idempotent: a map already on disk is left alone.

set -uo pipefail

BASE="https://ian-albert.com/games/super_mario_bros_maps"
DIR="$(cd "$(dirname "$0")" && pwd)/maps"

levels() { for w in 1 2 3 4 5 6 7 8; do for l in 1 2 3 4; do echo "$w-$l"; done; done; }

# Width and height live in the GIF header: bytes 6-9, little-endian uint16 each.
# Reading them directly avoids a dependency on an imaging library.
report() {
  python3 -I - "$DIR" <<'PY'
import os, sys, struct
d = sys.argv[1]
rows, bad = [], []
for w in range(1, 9):
    for l in range(1, 5):
        name = "mario-%d-%d.gif" % (w, l)
        p = os.path.join(d, name)
        if not os.path.exists(p):
            bad.append((name, "missing")); continue
        with open(p, "rb") as f:
            head = f.read(10)
        if head[:3] != b"GIF":
            bad.append((name, "not a GIF (%r)" % head[:6])); continue
        pw, ph = struct.unpack("<HH", head[6:10])
        rows.append((name, pw, ph, os.path.getsize(p)))
if rows:
    print("%-16s %8s %7s %12s" % ("file", "width", "height", "bytes"))
    for name, pw, ph, size in rows:
        print("%-16s %8d %7d %12d" % (name, pw, ph, size))
    print("\n%d map(s); widest %d px, tallest %d px, %.1f MB total" % (
        len(rows), max(r[1] for r in rows), max(r[2] for r in rows),
        sum(r[3] for r in rows) / 1e6))
for name, why in bad:
    print("  !! %s: %s" % (name, why), file=sys.stderr)
sys.exit(1 if bad else 0)
PY
}

if [ "${1:-}" = "--report" ]; then report; exit $?; fi

mkdir -p "$DIR"
fail=0
for lv in $(levels); do
  out="$DIR/mario-$lv.gif"
  if [ -s "$out" ]; then echo "have  mario-$lv.gif"; continue; fi
  echo -n "get   mario-$lv.gif ... "
  code=$(curl -fsS --retry 4 --retry-delay 2 --retry-all-errors -m 300 \
              -o "$out.part" -w "%{http_code}" "$BASE/mario-$lv.gif" 2>/dev/null)
  if [ "$code" = "200" ] && [ -s "$out.part" ] && \
     [ "$(head -c 3 "$out.part")" = "GIF" ]; then
    mv "$out.part" "$out"; echo "ok ($(stat -c%s "$out") bytes)"
  else
    rm -f "$out.part"; echo "FAILED (HTTP $code)"; fail=1
  fi
done

echo
report || fail=1
exit $fail
