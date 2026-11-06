"""Provenance machinery.

Every simulation constant in `params.py` is declared as a `Param`, which carries not
only the value but *where it came from* and *how much was assumed*.  This keeps the
audit trail of `simulation_parameters.md` inside the code, so the two cannot drift.

Status tags (identical to the spec):

    S  Stated in the target article
    D  Derived from the article's own equations (reasoning in `note`)
    F  Read from a figure (marker positions, axes, sub-captions)
    A  Absent - the simulator needs it, the article does not supply it
    X  Introduced by this analysis; no counterpart in the article

Source tiers:

    1   The article states it
    2A  Forced by the article; value justifiable from external evidence
    2B  Forced by the article; nothing pins it -> declare and sweep
    3   Not forced by the article; a genuine assumption
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

STATUS_MEANING = {
    "S": "Stated in the article",
    "D": "Derived from the article's own equations",
    "F": "Read from a figure",
    "A": "Absent - needed, not supplied by the article",
    "X": "Introduced by this analysis; NOT the article's",
}

TIER_MEANING = {
    "1": "Stated in the article",
    "2A": "Forced by the article; justifiable from external evidence",
    "2B": "Forced by the article; arbitrary - declare and sweep",
    "3": "Assumption - not forced by the article",
}


@dataclass(frozen=True)
class Param:
    """One simulation constant plus its full provenance."""

    value: Any
    status: str                 # one of STATUS_MEANING
    tier: str                   # one of TIER_MEANING
    source: str                 # e.g. "L577", "[P] L207", "[DBP] :135", "-"
    note: str = ""
    alternatives: tuple = field(default=())   # other defensible values, for sweeps
    only_if: str = ""      # non-empty => used only under this condition, not by default

    def __post_init__(self) -> None:
        if self.status not in STATUS_MEANING:
            raise ValueError(f"unknown status {self.status!r}")
        if self.tier not in TIER_MEANING:
            raise ValueError(f"unknown tier {self.tier!r}")
        # An article-stated value cannot sit in a tier that means "not stated".
        if self.status == "S" and self.tier not in ("1",):
            raise ValueError(f"status S must be tier 1, got {self.tier}")
        if self.status == "X" and self.tier != "3":
            raise ValueError("status X must be tier 3")

    def __repr__(self) -> str:                # pragma: no cover - display only
        return f"Param({self.value!r}, {self.status}/{self.tier}, {self.source})"


def collect(module_cls) -> dict[str, Param]:
    """Return the `Param` attributes declared on a module-parameter class."""
    return {
        name: obj
        for name, obj in vars(module_cls).items()
        if isinstance(obj, Param)
    }
