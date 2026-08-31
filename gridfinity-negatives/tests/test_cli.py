"""End-to-end: the commands a person actually types."""
import cv2
import numpy as np
import pytest

from gridfinity_negatives.cli import main


@pytest.fixture
def scan(tmp_path):
    from conftest import synthetic_tool
    img = synthetic_tool(110.0, 30.0, 300)
    p = tmp_path / "tool.png"
    cv2.imwrite(str(p), img)
    from PIL import Image
    im = Image.open(p); im.save(p, dpi=(300, 300))
    return p


def test_trace_reports_without_writing_cad(scan, capsys, tmp_path):
    assert main(["trace", str(scan), "--depth", "10"]) == 0
    out = capsys.readouterr().out
    assert "Tool bounds" in out and "Would build" in out
    assert not list(tmp_path.glob("*.stl"))


def test_build_writes_all_three_outputs(scan, tmp_path):
    out = tmp_path / "o"
    assert main(["build", str(scan), "--depth", "10", "--out", str(out),
                 "--name", "t"]) == 0
    assert (out / "t.stl").stat().st_size > 1000
    assert (out / "t.step").stat().st_size > 1000
    assert (out / "t-preview.png").stat().st_size > 1000


def test_build_honours_forced_size(scan, tmp_path):
    out = tmp_path / "o"
    assert main(["build", str(scan), "--depth", "10", "--size", "4x2",
                 "--out", str(out), "--name", "t", "--no-preview"]) == 0
    import cadquery as cq
    bb = cq.importers.importStep(str(out / "t.step")).vals()[0].BoundingBox()
    assert bb.xlen == pytest.approx(4 * 42 - 0.5, abs=0.01)
    assert bb.ylen == pytest.approx(2 * 42 - 0.5, abs=0.01)


def test_bad_size_argument_is_rejected(scan, tmp_path, capsys):
    rc = main(["build", str(scan), "--size", "big", "--out", str(tmp_path)])
    assert rc == 2
    assert "LxW" in capsys.readouterr().err


def test_mat_command_writes_a_printable_mat(tmp_path):
    p = tmp_path / "mat.png"
    assert main(["mat", "--out", str(p), "--dpi", "300"]) == 0
    img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    assert img.shape[0] == pytest.approx(297 * 300 / 25.4, abs=2)
    from gridfinity_negatives.calibrate import Mat, rectify
    # The mat we generate must be detectable by our own detector.
    flat = rectify(cv2.cvtColor(img, cv2.COLOR_GRAY2BGR), Mat(), 8.0)
    assert flat is not None
