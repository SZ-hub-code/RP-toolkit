"""Nuclear database helpers built on top of radioactivedecay."""

from __future__ import annotations

import math
from typing import Optional

import radioactivedecay as rd

AVOGADRO = 6.02214076e23
SECONDS_PER = {
    "s": 1,
    "min": 60,
    "h": 3600,
    "d": 86400,
    "y": 3.15576e7,
}

UNIT_LABELS = {
    "s": "seconds",
    "min": "minutes",
    "h": "hours",
    "d": "days",
    "y": "years",
}


class Nuclide:
    """Represent a nuclide and expose physical properties and calculations."""

    def __init__(self, name: str):
        self.name = name
        try:
            self._nuc = rd.Nuclide(name)
        except Exception as exc:  # pragma: no cover - library error shape may vary
            raise ValueError(
                f"Nuclide '{name}' not found. Use format 'Symbol-A' (example: 'Cs-137')."
            ) from exc

    @property
    def Z(self) -> int:
        """Atomic number (protons)."""
        return self._nuc.Z

    @property
    def A(self) -> int:
        """Mass number."""
        return self._nuc.A

    @property
    def N(self) -> int:
        """Neutron count."""
        return self.A - self.Z

    def half_life(self, unit: str = "s") -> float:
        """Half life in unit in {'s', 'min', 'h', 'd', 'y'}."""
        return self._nuc.half_life(unit)

    @property
    def decay_constant(self) -> float:
        """Decay constant in s^-1."""
        t_half = self.half_life("s")
        if t_half == float("inf"):
            return 0.0
        return math.log(2) / t_half

    @property
    def progeny(self) -> list[str]:
        """Daughter nuclides produced by decay."""
        return self._nuc.progeny()

    @property
    def decay_modes(self) -> list[str]:
        """Decay modes (beta-, beta+, alpha, EC, IT...)."""
        return self._nuc.decay_modes()

    @property
    def branching_fractions(self) -> list[float]:
        """Branching fractions for each decay mode."""
        return self._nuc.branching_fractions()

    def activity_after(self, t: float, unit: str = "d", a0_bq: float = 1e6) -> dict[str, float]:
        """Activity of parent and progeny after time t."""
        inventory = rd.Inventory({self.name: a0_bq}, "Bq")
        result = inventory.decay(t, unit).activities()
        return {str(k): float(v) for k, v in result.items()}

    def mass_from_activity(self, activity_bq: float, atomic_mass_u: Optional[float] = None) -> float:
        """Mass in grams matching an activity in Bq."""
        molar_mass = atomic_mass_u if atomic_mass_u else float(self.A)
        lam = self.decay_constant
        if lam == 0:
            return float("inf")
        return (activity_bq * molar_mass) / (lam * AVOGADRO)

    def activity_from_mass(self, mass_g: float, atomic_mass_u: Optional[float] = None) -> float:
        """Activity in Bq matching a mass in grams."""
        molar_mass = atomic_mass_u if atomic_mass_u else float(self.A)
        lam = self.decay_constant
        return lam * mass_g * AVOGADRO / molar_mass

    def n_half_lives(self, t: float, unit: str = "d") -> float:
        """Number of elapsed half-lives during t."""
        if unit not in SECONDS_PER:
            supported_units = ", ".join(sorted(SECONDS_PER))
            raise ValueError(f"Unsupported unit '{unit}'. Supported units: {supported_units}.")
        t_s = t * SECONDS_PER[unit]
        t_half_s = self.half_life("s")
        if t_half_s == float("inf"):
            return 0.0
        return t_s / t_half_s

    def remaining_fraction(self, t: float, unit: str = "d") -> float:
        """Remaining activity fraction after time t."""
        return 0.5 ** self.n_half_lives(t, unit)

    def summary(self) -> None:
        """Print a compact summary in terminal-friendly format."""
        t_best, unit_best = self._best_half_life_display()
        lam = self.decay_constant

        print("\n" + "=" * 45)
        print(f"  Nuclide: {self.name}")
        print("=" * 45)
        print(f"  Z = {self.Z}  |  A = {self.A}  |  N = {self.N}")
        print(f"  T1/2 = {t_best:.4g} {UNIT_LABELS.get(unit_best, unit_best)}")
        print(f"  Lambda = {lam:.4e} s^-1")
        print("  Decay modes:")
        for mode, bf, prog in zip(self.decay_modes, self.branching_fractions, self.progeny):
            print(f"    -> {mode:6s} ({bf * 100:.2f}%) -> {prog}")
        print("=" * 45 + "\n")

    def _best_half_life_display(self) -> tuple[float, str]:
        """Return a human-readable half-life unit/value pair."""
        t_s = self.half_life("s")
        if t_s == float("inf"):
            return float("inf"), "s"
        for unit in ["y", "d", "h", "min", "s"]:
            val = t_s / SECONDS_PER[unit]
            if val >= 1:
                return val, unit
        return t_s, "s"

    def __repr__(self) -> str:
        return f"<Nuclide {self.name} | T1/2={self.half_life('d'):.3g} d>"


class NucDB:
    """Main entry point to radioactivedecay nuclide database."""

    def __init__(self):
        self._data = rd.DEFAULTDATA
        self._all_nuclide_names = list(self._data.nuclide_dict.keys())

    @property
    def n_nuclides(self) -> int:
        """Total nuclides in database."""
        return len(self._all_nuclide_names)

    def get(self, name: str) -> Nuclide:
        """Return a Nuclide object from a name like Co-60."""
        return Nuclide(name)

    def search(
        self,
        decay_mode: Optional[str] = None,
        half_life_min_days: Optional[float] = None,
        half_life_max_days: Optional[float] = None,
        z_min: Optional[int] = None,
        z_max: Optional[int] = None,
        max_results: int = 20,
    ) -> list[Nuclide]:
        """Search nuclides with simple physical filters."""
        results: list[Nuclide] = []
        for name in self._all_nuclide_names:
            try:
                nuc = Nuclide(name)
                t_d = nuc.half_life("d")

                if decay_mode and decay_mode not in nuc.decay_modes:
                    continue
                if half_life_min_days is not None and t_d < half_life_min_days:
                    continue
                if half_life_max_days is not None and (t_d == float("inf") or t_d > half_life_max_days):
                    continue
                if z_min is not None and nuc.Z < z_min:
                    continue
                if z_max is not None and nuc.Z > z_max:
                    continue

                results.append(nuc)
            except Exception:
                continue

        results.sort(key=lambda nuclide: nuclide.half_life("s"))
        return results[:max_results]

    def compare(self, names: list[str]) -> None:
        """Print a comparison table for a list of nuclides."""
        print(f"\n{'Nuclide':<12} {'Z':>4} {'A':>4} {'T1/2':>18} {'Mode(s)':>25} {'Daughters':>20}")
        print("-" * 90)
        for name in names:
            try:
                nuc = Nuclide(name)
                t_val, t_unit = nuc._best_half_life_display()
                t_str = f"{t_val:.4g} {UNIT_LABELS.get(t_unit, t_unit)}"
                modes = ", ".join(nuc.decay_modes)
                progs = ", ".join(nuc.progeny)
                print(f"{nuc.name:<12} {nuc.Z:>4} {nuc.A:>4} {t_str:>18} {modes:>25} {progs:>20}")
            except ValueError as exc:
                print(f"{name:<12} - ERROR: {exc}")
        print()

    def __repr__(self) -> str:
        return f"<NucDB | {self.n_nuclides} nuclides>"
