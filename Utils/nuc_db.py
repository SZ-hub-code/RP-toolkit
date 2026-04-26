"""
nuc_db.py — RP-Toolkit Nuclear Database
========================================
Wrapper autour de la librairie `radioactivedecay` (IAEA/NNDC data, ~1500 nucléides).

Usage rapide :
    from nuc_db import NucDB
    db = NucDB()
    cs137 = db.get("Cs-137")
    cs137.summary()
    cs137.activity_after(30, "y")
    db.search(half_life_max_days=10, decay_mode="β-")
"""

import radioactivedecay as rd
import math
from typing import Optional


# ─────────────────────────────────────────────
#  Constantes
# ─────────────────────────────────────────────
AVOGADRO = 6.02214076e23   # mol⁻¹
SECONDS_PER = {
    "s":  1,
    "min": 60,
    "h":  3600,
    "d":  86400,
    "y":  3.15576e7,
}

UNIT_LABELS = {"s": "secondes", "min": "minutes", "h": "heures", "d": "jours", "y": "années"}


# ─────────────────────────────────────────────
#  Classe Nucléide
# ─────────────────────────────────────────────
class Nuclide:
    """
    Représente un nucléide et expose ses propriétés physiques + calculs RP.

    Paramètres
    ----------
    name : str
        Nom du nucléide au format 'Symbol-A' (ex: 'Cs-137', 'Co-60', 'I-131').
    """

    def __init__(self, name: str):
        self.name = name
        try:
            self._nuc = rd.Nuclide(name)
        except Exception:
            raise ValueError(
                f"Nucléide '{name}' introuvable. Vérifier le format 'Symbol-A' (ex: 'Cs-137')."
            )

    # ── Propriétés de base ──────────────────────────────────

    @property
    def Z(self) -> int:
        """Numéro atomique (nombre de protons)."""
        return self._nuc.Z

    @property
    def A(self) -> int:
        """Nombre de masse."""
        return self._nuc.A

    @property
    def N(self) -> int:
        """Nombre de neutrons."""
        return self.A - self.Z

    def half_life(self, unit: str = "s") -> float:
        """
        Période radioactive T½.

        unit : 's' | 'min' | 'h' | 'd' | 'y'
        """
        return self._nuc.half_life(unit)

    @property
    def decay_constant(self) -> float:
        """Constante de désintégration λ en s⁻¹ (λ = ln2 / T½)."""
        t_half = self.half_life("s")
        if t_half == float("inf"):
            return 0.0
        return math.log(2) / t_half

    @property
    def progeny(self) -> list[str]:
        """Liste des nucléides fils produits lors de la désintégration."""
        return self._nuc.progeny()

    @property
    def decay_modes(self) -> list[str]:
        """Modes de désintégration (β-, β+, α, EC, IT…)."""
        return self._nuc.decay_modes()

    @property
    def branching_fractions(self) -> list[float]:
        """Fractions d'embranchement correspondant à chaque mode."""
        return self._nuc.branching_fractions()

    # ── Calculs RP ──────────────────────────────────────────

    def activity_after(self, t: float, unit: str = "d", A0_Bq: float = 1e6) -> dict:
        """
        Calcule l'activité du nucléide père + tous ses fils après un temps t.

        Paramètres
        ----------
        t      : durée écoulée
        unit   : unité de t ('s','min','h','d','y')
        A0_Bq  : activité initiale du père en Bq

        Retourne un dict {nucléide: activité_Bq}.
        """
        inv = rd.Inventory({self.name: A0_Bq}, "Bq")
        result = inv.decay(t, unit).activities()
        return {str(k): float(v) for k, v in result.items()}

    def mass_from_activity(self, A_Bq: float, atomic_mass_u: Optional[float] = None) -> float:
        """
        Masse (en grammes) correspondant à une activité donnée.

        m = A × M / (λ × Nₐ)

        Paramètres
        ----------
        A_Bq         : activité en Bq
        atomic_mass_u: masse atomique en u (défaut ≈ A)
        """
        M = atomic_mass_u if atomic_mass_u else float(self.A)
        lam = self.decay_constant
        if lam == 0:
            return float("inf")
        return (A_Bq * M) / (lam * AVOGADRO)

    def activity_from_mass(self, mass_g: float, atomic_mass_u: Optional[float] = None) -> float:
        """
        Activité (en Bq) correspondant à une masse donnée.

        A = λ × m × Nₐ / M
        """
        M = atomic_mass_u if atomic_mass_u else float(self.A)
        lam = self.decay_constant
        return lam * mass_g * AVOGADRO / M

    def n_half_lives(self, t: float, unit: str = "d") -> float:
        """Nombre de périodes écoulées pendant le temps t."""
        t_s = t * SECONDS_PER[unit]
        t_half_s = self.half_life("s")
        if t_half_s == float("inf"):
            return 0.0
        return t_s / t_half_s

    def remaining_fraction(self, t: float, unit: str = "d") -> float:
        """Fraction d'activité restante après le temps t (entre 0 et 1)."""
        return 0.5 ** self.n_half_lives(t, unit)

    # ── Affichage ───────────────────────────────────────────

    def summary(self) -> None:
        """Affiche un résumé des propriétés du nucléide."""
        t_best, unit_best = self._best_half_life_display()
        lam = self.decay_constant

        print(f"\n{'═'*45}")
        print(f"  Nucléide : {self.name}")
        print(f"{'═'*45}")
        print(f"  Z = {self.Z}  |  A = {self.A}  |  N = {self.N}")
        print(f"  T½ = {t_best:.4g} {UNIT_LABELS.get(unit_best, unit_best)}")
        print(f"  λ  = {lam:.4e} s⁻¹")
        print(f"  Modes de désintégration :")
        for mode, bf, prog in zip(self.decay_modes, self.branching_fractions, self.progeny):
            print(f"    → {mode:6s}  ({bf*100:.2f}%)  ➜  {prog}")
        print(f"{'═'*45}\n")

    def _best_half_life_display(self):
        """Choisit l'unité la plus lisible pour T½."""
        t_s = self.half_life("s")
        if t_s == float("inf"):
            return float("inf"), "s"
        for unit in ["y", "d", "h", "min", "s"]:
            val = t_s / SECONDS_PER[unit]
            if val >= 1:
                return val, unit
        return t_s, "s"

    def __repr__(self):
        return f"<Nuclide {self.name} | T½={self.half_life('d'):.3g} j>"


# ─────────────────────────────────────────────
#  Classe NucDB (base de données)
# ─────────────────────────────────────────────
class NucDB:
    """
    Interface principale vers la base de données nucléaires (~1512 nucléides).

    Exemple
    -------
    db = NucDB()
    db.get("Cs-137").summary()
    db.search(decay_mode="α", half_life_min_days=1, half_life_max_days=365)
    """

    def __init__(self):
        self._data = rd.DEFAULTDATA
        self._all_nuclide_names = list(self._data.nuclide_dict.keys())

    @property
    def n_nuclides(self) -> int:
        """Nombre de nucléides dans la base."""
        return len(self._all_nuclide_names)

    def get(self, name: str) -> Nuclide:
        """Retourne un objet Nuclide pour le nom donné (ex: 'Co-60')."""
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
        """
        Recherche dans la base selon des critères physiques.

        Paramètres
        ----------
        decay_mode          : filtre sur le mode ('β-', 'β+', 'α', 'EC', 'IT', 'SF')
        half_life_min_days  : T½ minimum en jours
        half_life_max_days  : T½ maximum en jours
        z_min / z_max       : plage de numéro atomique Z
        max_results         : nombre max de résultats retournés

        Retourne
        --------
        Liste d'objets Nuclide triés par T½ croissante.
        """
        results = []
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

        results.sort(key=lambda n: n.half_life("s"))
        return results[:max_results]

    def compare(self, names: list[str]) -> None:
        """Affiche un tableau comparatif de plusieurs nucléides."""
        print(f"\n{'Nucléide':<12} {'Z':>4} {'A':>4} {'T½':>18} {'Mode(s)':>25} {'Fils':>20}")
        print("─" * 90)
        for name in names:
            try:
                nuc = Nuclide(name)
                t_val, t_unit = nuc._best_half_life_display()
                t_str = f"{t_val:.4g} {UNIT_LABELS.get(t_unit, t_unit)}"
                modes = ", ".join(nuc.decay_modes)
                progs = ", ".join(nuc.progeny)
                print(f"{nuc.name:<12} {nuc.Z:>4} {nuc.A:>4} {t_str:>18} {modes:>25} {progs:>20}")
            except ValueError as e:
                print(f"{name:<12} — ERREUR: {e}")
        print()

    def __repr__(self):
        return f"<NucDB | {self.n_nuclides} nucléides (IAEA/NNDC)>"
