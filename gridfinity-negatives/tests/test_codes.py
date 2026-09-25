"""The location code scheme.

A wrong code is invisible until the bins are printed and unfixable after, so
the parser is strict and the CLI spells every code back out in words.
"""
import pytest

from gridfinity_negatives.codes import Location, is_valid, parse

# Every code the scheme was defined with.
REAL_CODES = [
    ("KWL1N1T", "1st north column", "1st drawer from the top"),
    ("KWL1N2T", "1st north column", "2nd drawer from the top"),
    ("KSL1W1T", "1st west column", "1st drawer from the top"),
    ("KSL2W1T", "2nd west column", "1st drawer from the top"),
    ("KEL1S1T", "1st south column", "1st drawer from the top"),
    ("KEL1S2T", "1st south column", "2nd drawer from the top"),
    ("KEL1N1T", "1st north column", "1st drawer from the top"),
    ("KEL2N1T", "2nd north column", "1st drawer from the top"),
]


@pytest.mark.parametrize("code,column,drawer", REAL_CODES)
def test_real_codes_parse_and_describe(code, column, drawer):
    loc = parse(code)
    assert loc.code == code, "round trip changed the code"
    described = loc.describe()
    assert column in described, described
    assert drawer in described, described


def test_the_digit_carries_position_not_the_letter():
    """KWL1N2T is the drawer below KWL1N1T -- both still measured from the top."""
    a, b = parse("KWL1N1T"), parse("KWL1N2T")
    assert a.drawer_ref == b.drawer_ref == "T"
    assert b.drawer_n == a.drawer_n + 1
    assert (a.room, a.wall, a.section, a.column_n, a.column_dir) == \
           (b.room, b.wall, b.section, b.column_n, b.column_dir)


def test_lowercase_is_normalised():
    assert parse("kwl1n1t").code == "KWL1N1T"


@pytest.mark.parametrize("bad", [
    "KWL1N1",      # missing the drawer reference
    "KWL1N1TT",    # too long
    "KXL1N1T",     # X is not a compass wall
    "KWL1N1X",     # X is not top or bottom
    "KWLN1T",      # column has no number
    "",
    "not a code",
])
def test_malformed_codes_are_rejected(bad):
    assert not is_valid(bad)
    with pytest.raises(ValueError, match="not a location code"):
        parse(bad)


def test_rejection_names_an_example():
    with pytest.raises(ValueError, match="KWL1N1T"):
        parse("nonsense")


def test_multi_digit_positions_work():
    """A column 10 or a drawer 12 must not break the parse."""
    loc = parse("KWL10N12T")
    assert loc.column_n == 10 and loc.drawer_n == 12
    assert loc.code == "KWL10N12T"
