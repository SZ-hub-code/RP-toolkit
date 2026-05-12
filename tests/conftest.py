"""Shared pytest fixtures for RP toolkit tests."""

import pytest

from rp_toolkit.core.dose_rate import DoseScenario


@pytest.fixture
def cs137_scenario() -> DoseScenario:
    return DoseScenario(nuclide="Cs-137", activity_bq=1e9, distance_m=1.0)


@pytest.fixture
def rel_tol() -> float:
    return 1e-6
