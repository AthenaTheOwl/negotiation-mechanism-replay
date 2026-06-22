"""Stable package surface for Negotiation Mechanism Replay."""

from __future__ import annotations

import sys
from pathlib import Path


_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from negotiation_mechanism_replay.model import (  # noqa: E402
    CrossApplication,
    Equilibrium,
    IncentiveEntry,
    LeakageEntry,
    ReplayReport,
    ReplayValidationError,
    load_report,
)
from negotiation_mechanism_replay.scoring import score_cross_applications  # noqa: E402

__all__ = [
    "CrossApplication",
    "Equilibrium",
    "IncentiveEntry",
    "LeakageEntry",
    "ReplayReport",
    "ReplayValidationError",
    "load_report",
    "score_cross_applications",
]
