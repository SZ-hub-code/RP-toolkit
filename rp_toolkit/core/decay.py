"""Radioactive decay helpers and chain calculations."""

from __future__ import annotations

import math
from dataclasses import dataclass

import radioactivedecay as rd

SECONDS_PER = {
    "s": 1.0,
    "min": 60.0,
    "h": 3600.0,
    "d": 86400.0,
    "y": 365.25 * 86400.0,
}


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative.")


def to_seconds(time_value: float, unit: str) -> float:
    """Convert a duration to seconds."""
    if unit not in SECONDS_PER:
        raise ValueError(f"Unsupported unit '{unit}'.")
    _validate_non_negative("time_value", time_value)
    return time_value * SECONDS_PER[unit]


def decay_activity(a0_bq: float, half_life_s: float, time_s: float) -> float:
    """Activity at time t from A(t)=A0*exp(-lambda*t)."""
    _validate_non_negative("a0_bq", a0_bq)
    _validate_non_negative("time_s", time_s)
    if half_life_s <= 0 and not math.isinf(half_life_s):
        raise ValueError("half_life_s must be > 0 or infinity.")
    if math.isinf(half_life_s):
        return a0_bq

    lam = math.log(2.0) / half_life_s
    return a0_bq * math.exp(-lam * time_s)


def integrated_activity(a0_bq: float, half_life_s: float, time_s: float) -> float:
    """Integral of activity over [0, t] in Bq*s."""
    _validate_non_negative("a0_bq", a0_bq)
    _validate_non_negative("time_s", time_s)
    if half_life_s <= 0 and not math.isinf(half_life_s):
        raise ValueError("half_life_s must be > 0 or infinity.")
    if math.isinf(half_life_s):
        return a0_bq * time_s

    lam = math.log(2.0) / half_life_s
    return a0_bq * (1.0 - math.exp(-lam * time_s)) / lam


def activity_to_atoms(activity_bq: float, half_life_s: float) -> float:
    """Convert activity (Bq) to atom count using A=lambda*N."""
    _validate_non_negative("activity_bq", activity_bq)
    if half_life_s <= 0 or math.isinf(half_life_s):
        raise ValueError("half_life_s must be finite and > 0.")
    lam = math.log(2.0) / half_life_s
    return activity_bq / lam


def atoms_to_activity(n_atoms: float, half_life_s: float) -> float:
    """Convert atom count to activity (Bq) using A=lambda*N."""
    _validate_non_negative("n_atoms", n_atoms)
    if half_life_s <= 0 or math.isinf(half_life_s):
        raise ValueError("half_life_s must be finite and > 0.")
    lam = math.log(2.0) / half_life_s
    return lam * n_atoms


def decay_chain_activities(
    parent_nuclide: str,
    a0_bq: float,
    time_value: float,
    unit: str = "d",
) -> dict[str, float]:
    """Return parent/progeny activities after a decay time."""
    _validate_non_negative("a0_bq", a0_bq)
    _validate_non_negative("time_value", time_value)

    inventory = rd.Inventory({parent_nuclide: a0_bq}, "Bq")
    activities = inventory.decay(time_value, unit).activities()
    return {str(nuclide): float(activity) for nuclide, activity in activities.items()}


@dataclass(frozen=True)
class DecaySnapshot:
    """Single snapshot for chain activity bookkeeping."""

    time_value: float
    unit: str
    activities_bq: dict[str, float]

    @property
    def total_activity_bq(self) -> float:
        return sum(self.activities_bq.values())


def snapshot_decay_chain(
    parent_nuclide: str,
    a0_bq: float,
    time_value: float,
    unit: str = "d",
) -> DecaySnapshot:
    """Build a typed snapshot object from chain decay computation."""
    activities = decay_chain_activities(parent_nuclide, a0_bq, time_value, unit)
    return DecaySnapshot(time_value=time_value, unit=unit, activities_bq=activities)
