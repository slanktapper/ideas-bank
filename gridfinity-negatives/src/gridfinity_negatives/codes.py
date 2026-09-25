"""The location code scheme.

A code says where a bin belongs, so an interchangeable bin that leaves its
drawer can be put back. Seven characters, coarse to fine:

    K W L 1N 1T
    │ │ │ │  └─ drawer: 1st from the Top
    │ │ │ └──── column: 1st North
    │ │ └────── section: Lower
    │ └──────── wall: West
    └────────── room: Kitchen

The digit carries the position and the letter the reference direction, so the
drawer below KWL1N1T is KWL1N2T, not KWL1N1B.

Validation exists because the cost of a typo is asymmetric: a wrong code is
invisible until 84 bins are printed, and unfixable afterwards.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

CODE_RE = re.compile(
    r"^(?P<room>[A-Z])"
    r"(?P<wall>[NSEW])"
    r"(?P<section>[A-Z])"
    r"(?P<col_n>\d+)(?P<col_dir>[NSEW])"
    r"(?P<drw_n>\d+)(?P<drw_ref>[TB])$"
)

COMPASS = {"N": "north", "S": "south", "E": "east", "W": "west"}
SECTIONS = {"L": "lower", "U": "upper", "M": "middle"}
ROOMS = {"K": "kitchen", "G": "garage", "W": "workshop", "O": "office"}
REFERENCE = {"T": "from the top", "B": "from the bottom"}


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


@dataclass(frozen=True)
class Location:
    room: str
    wall: str
    section: str
    column_n: int
    column_dir: str
    drawer_n: int
    drawer_ref: str

    @property
    def code(self) -> str:
        return (
            f"{self.room}{self.wall}{self.section}"
            f"{self.column_n}{self.column_dir}{self.drawer_n}{self.drawer_ref}"
        )

    def describe(self) -> str:
        """Spell the code out, so a typo is obvious before anything is printed."""
        return (
            f"{ROOMS.get(self.room, self.room + '?').title()}, "
            f"{COMPASS[self.wall]} wall, "
            f"{SECTIONS.get(self.section, self.section + '?')} section, "
            f"{_ordinal(self.column_n)} {COMPASS[self.column_dir]} column, "
            f"{_ordinal(self.drawer_n)} drawer {REFERENCE[self.drawer_ref]}"
        )


def parse(code: str) -> Location:
    """Parse a location code, or explain precisely why it is not one."""
    code = code.strip().upper()
    m = CODE_RE.match(code)
    if not m:
        raise ValueError(
            f"{code!r} is not a location code. Expected room, wall (NSEW), "
            "section, column number + direction, drawer number + T/B -- "
            "for example KWL1N1T."
        )
    g = m.groupdict()
    return Location(
        room=g["room"], wall=g["wall"], section=g["section"],
        column_n=int(g["col_n"]), column_dir=g["col_dir"],
        drawer_n=int(g["drw_n"]), drawer_ref=g["drw_ref"],
    )


def is_valid(code: str) -> bool:
    try:
        parse(code)
        return True
    except ValueError:
        return False
