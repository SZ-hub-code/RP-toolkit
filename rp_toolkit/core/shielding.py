"""Gamma attenuation and shielding utilities."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from importlib import resources


def _load_attenuation_data() -> dict[str, dict[str, float]]:
    data_path = resources.files("rp_toolkit.data").joinpath("attenuation_coeff.json")
    with data_path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    return {
        material.lower(): {str(energy): float(mu) for energy, mu in coeffs.items()}
        for material, coeffs in raw.items()
    }


_ATTENUATION_DATA = _load_attenuation_data()


def available_materials() -> list[str]:
    """List materials available in attenuation dataset."""
    return sorted(_ATTENUATION_DATA.keys())


def attenuation_coefficient(material: str, energy_mev: float) -> float:
    """Return linear attenuation coefficient mu (m^-1) at nearest tabulated energy."""
    if energy_mev <= 0:
        raise ValueError("energy_mev must be strictly positive.")

    mat_key = material.strip().lower()
    if mat_key not in _ATTENUATION_DATA:
        raise KeyError(f"Unknown material '{material}'. Available: {', '.join(available_materials())}")

    points = {float(energy): mu for energy, mu in _ATTENUATION_DATA[mat_key].items()}
    nearest_energy = min(points, key=lambda point: abs(point - energy_mev))
    return points[nearest_energy]


def transmission_factor(mu_m_inv: float, thickness_m: float, buildup_factor: float = 1.0) -> float:
    """Transmission fraction B*exp(-mu*x)."""
    if mu_m_inv < 0:
        raise ValueError("mu_m_inv must be non-negative.")
    if thickness_m < 0:
        raise ValueError("thickness_m must be non-negative.")
    if buildup_factor <= 0:
        raise ValueError("buildup_factor must be strictly positive.")

    return buildup_factor * math.exp(-mu_m_inv * thickness_m)


def attenuated_dose_rate(
    input_dose_rate_u_sv_h: float,
    mu_m_inv: float,
    thickness_m: float,
    buildup_factor: float = 1.0,
) -> float:
    """Output dose rate after shielding."""
    if input_dose_rate_u_sv_h < 0:
        raise ValueError("input_dose_rate_u_sv_h must be non-negative.")
    return input_dose_rate_u_sv_h * transmission_factor(mu_m_inv, thickness_m, buildup_factor)


def hvl(mu_m_inv: float) -> float:
    """Half-value layer in meters."""
    if mu_m_inv <= 0:
        return float("inf")
    return math.log(2.0) / mu_m_inv


def tvl(mu_m_inv: float) -> float:
    """Tenth-value layer in meters."""
    if mu_m_inv <= 0:
        return float("inf")
    return math.log(10.0) / mu_m_inv


def required_thickness(
    mu_m_inv: float,
    attenuation_factor: float,
    buildup_factor: float = 1.0,
) -> float:
    """Required thickness to achieve a target attenuation ratio D_in / D_out."""
    if mu_m_inv <= 0:
        return float("inf")
    if attenuation_factor <= 1:
        return 0.0
    if buildup_factor <= 0:
        raise ValueError("buildup_factor must be strictly positive.")

    numerator = math.log(attenuation_factor) + math.log(buildup_factor)
    return max(0.0, numerator / mu_m_inv)


@dataclass(frozen=True)
class ShieldingScenario:
    """Simple shielding scenario object."""

    material: str
    energy_mev: float
    thickness_m: float
    buildup_factor: float = 1.0

    def mu(self) -> float:
        return attenuation_coefficient(self.material, self.energy_mev)

    def transmission(self) -> float:
        return transmission_factor(self.mu(), self.thickness_m, self.buildup_factor)
