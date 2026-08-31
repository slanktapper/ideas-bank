"""Turn a scan or photo of a tool into a Gridfinity bin with its negative."""

from .config import DEFAULTS, Tuning
from .model import BinSpec, auto_spec, build, export
from .trace import trace_photo, trace_scan

__all__ = [
    "DEFAULTS",
    "Tuning",
    "BinSpec",
    "auto_spec",
    "build",
    "export",
    "trace_scan",
    "trace_photo",
]
__version__ = "0.1.0"
