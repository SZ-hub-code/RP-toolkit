"""Dose rate models for point gamma sources."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from typing import Mapping


def _load_gamma_constants() -> tuple[dict[str, float], dict[str, str]]:
    data_path = resources.files("rp_toolkit.data").joinpath("gamma_constants.json")
    with data_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    values: dict[str, float] = {}
    display_names: dict[str, str] = {}
    for name, value in raw.items():
        key = name.strip().lower()
        values[key] = float(value)
        display_names[key] = name
    return values, display_names


def _load_zone_thresholds() -> dict[str, float]:
    data_path = resources.files("rp_toolkit.data").joinpath("dose_limits.json")
    with data_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    values = raw.get("zone_thresholds_uSv_h", {})
    return {name: float(value) for name, value in values.items()}


_GAMMA_CONSTANTS, _DISPLAY_NAMES = _load_gamma_constants()

DEFAULT_ZONE_THRESHOLDS_U_SV_H = _load_zone_thresholds() or {
    "public_area": 2.5,
    "supervised_area": 7.5,
    "controlled_area": 25.0,
    "high_radiation_area": 100.0,
}


def available_nuclides() -> list[str]:
    """Return available nuclides for gamma constant lookup."""
    return [_DISPLAY_NAMES[key] for key in sorted(_DISPLAY_NAMES.keys())]


def gamma_constant(nuclide: str) -> float:
    """Gamma constant in uSv*m^2/(MBq*h) for a nuclide."""
    key = nuclide.strip().lower()
    if key not in _GAMMA_CONSTANTS:
        raise KeyError(
            f"Unknown nuclide '{nuclide}'. Available examples: {', '.join(available_nuclides()[:8])}"
        )
    return _GAMMA_CONSTANTS[key]


def inverse_square_scale(
    dose_rate_ref_u_sv_h: float,
    ref_distance_m: float,
    new_distance_m: float,
) -> float:
    """Scale dose rate by inverse square law from a known reference point."""
    if ref_distance_m <= 0 or new_distance_m <= 0:
        raise ValueError("Distances must be strictly positive.")
    if dose_rate_ref_u_sv_h < 0:
        raise ValueError("Dose rate must be non-negative.")
    return dose_rate_ref_u_sv_h * (ref_distance_m / new_distance_m) ** 2


def dose_rate_point_source(
    nuclide: str,
    activity_bq: float,
    distance_m: float,
    buildup_factor: float = 1.0,
    occupancy_factor: float = 1.0,
) -> float:
    """Point source dose rate at distance using gamma constant and 1/r^2 law."""
    if activity_bq < 0:
        raise ValueError("Activity must be non-negative.")
    if distance_m <= 0:
        raise ValueError("Distance must be strictly positive.")
    if buildup_factor <= 0 or occupancy_factor < 0:
        raise ValueError("Invalid buildup or occupancy factor.")

    gamma = gamma_constant(nuclide)
    activity_mbq = activity_bq / 1e6
    base_rate = gamma * activity_mbq / (distance_m**2)
    return base_rate * buildup_factor * occupancy_factor


def classify_zone(
    dose_rate_u_sv_h: float,
    thresholds_u_sv_h: Mapping[str, float] | None = None,
) -> str:
    """Classify an area from dose rate and configurable thresholds."""
    if dose_rate_u_sv_h < 0:
        raise ValueError("Dose rate must be non-negative.")

    thresholds = dict(thresholds_u_sv_h or DEFAULT_ZONE_THRESHOLDS_U_SV_H)
    zone = "below_public_threshold"
    for zone_name, threshold in sorted(thresholds.items(), key=lambda item: item[1]):
        if dose_rate_u_sv_h >= threshold:
            zone = zone_name
    return zone


@dataclass(frozen=True)
class DoseScenario:
    """Container for simple point-source dose rate calculations."""

    nuclide: str
    activity_bq: float
    distance_m: float
    buildup_factor: float = 1.0
    occupancy_factor: float = 1.0

    def dose_rate_uSv_h(self) -> float:
        """Dose rate at scenario distance in uSv/h."""
        return dose_rate_point_source(
            nuclide=self.nuclide,
            activity_bq=self.activity_bq,
            distance_m=self.distance_m,
            buildup_factor=self.buildup_factor,
            occupancy_factor=self.occupancy_factor,
        )

    def dose_rate_at(self, new_distance_m: float) -> float:
        """Dose rate at another distance using inverse square scaling."""
        return inverse_square_scale(self.dose_rate_uSv_h(), self.distance_m, new_distance_m)

    def zone(self, thresholds_u_sv_h: Mapping[str, float] | None = None) -> str:
        """Regulatory style zone classification from dose rate."""
        return classify_zone(self.dose_rate_uSv_h(), thresholds_u_sv_h)
