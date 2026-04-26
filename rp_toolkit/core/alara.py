"""ALARA-oriented utilities for exposure optimization."""

from __future__ import annotations

import math
from dataclasses import dataclass


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative.")


def integrated_dose(dose_rate_u_sv_h: float, time_h: float, occupancy_factor: float = 1.0) -> float:
    """Integrated dose in uSv over an exposure time."""
    _validate_non_negative("dose_rate_u_sv_h", dose_rate_u_sv_h)
    _validate_non_negative("time_h", time_h)
    _validate_non_negative("occupancy_factor", occupancy_factor)
    return dose_rate_u_sv_h * time_h * occupancy_factor


def allowed_time_for_dose_limit(
    dose_rate_u_sv_h: float,
    dose_limit_u_sv: float,
    occupancy_factor: float = 1.0,
) -> float:
    """Maximum allowed exposure time in hours for a dose limit."""
    _validate_non_negative("dose_rate_u_sv_h", dose_rate_u_sv_h)
    _validate_non_negative("dose_limit_u_sv", dose_limit_u_sv)
    _validate_non_negative("occupancy_factor", occupancy_factor)

    effective_rate = dose_rate_u_sv_h * occupancy_factor
    if effective_rate == 0:
        return float("inf")
    return dose_limit_u_sv / effective_rate


def optimize_distance_for_target_rate(
    reference_rate_u_sv_h: float,
    reference_distance_m: float,
    target_rate_u_sv_h: float,
) -> float:
    """Distance needed to meet a target dose rate from inverse-square law."""
    if reference_rate_u_sv_h <= 0:
        raise ValueError("reference_rate_u_sv_h must be strictly positive.")
    if reference_distance_m <= 0:
        raise ValueError("reference_distance_m must be strictly positive.")
    if target_rate_u_sv_h <= 0:
        raise ValueError("target_rate_u_sv_h must be strictly positive.")

    return reference_distance_m * math.sqrt(reference_rate_u_sv_h / target_rate_u_sv_h)


def collective_dose(
    dose_rate_u_sv_h: float,
    time_h: float,
    n_workers: int,
    occupancy_factor: float = 1.0,
) -> float:
    """Collective dose in person-uSv."""
    if n_workers < 0:
        raise ValueError("n_workers must be non-negative.")
    return integrated_dose(dose_rate_u_sv_h, time_h, occupancy_factor) * n_workers


@dataclass(frozen=True)
class AlaraScenario:
    """Scenario envelope for ALARA comparisons."""

    dose_rate_u_sv_h: float
    time_h: float
    occupancy_factor: float = 1.0

    def integrated_dose_u_sv(self) -> float:
        return integrated_dose(self.dose_rate_u_sv_h, self.time_h, self.occupancy_factor)


def compare_scenarios(baseline: AlaraScenario, optimized: AlaraScenario) -> dict[str, float]:
    """Return before/after metrics with reduction percentage."""
    before = baseline.integrated_dose_u_sv()
    after = optimized.integrated_dose_u_sv()
    reduction_pct = 0.0 if before == 0 else 100.0 * (before - after) / before

    return {
        "dose_before_uSv": before,
        "dose_after_uSv": after,
        "reduction_uSv": before - after,
        "reduction_pct": reduction_pct,
    }
