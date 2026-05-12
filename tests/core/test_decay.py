import math

import pytest

from rp_toolkit.core.decay import decay_activity, integrated_activity


def test_activity_after_one_half_life() -> None:
    assert decay_activity(a0_bq=100.0, half_life_s=10.0, time_s=10.0) == pytest.approx(50.0)


def test_integrated_activity_is_positive() -> None:
    value = integrated_activity(a0_bq=200.0, half_life_s=30.0, time_s=60.0)
    assert value > 0


def test_stable_nuclide_integrated_activity_matches_a0_t() -> None:
    value = integrated_activity(a0_bq=5.0, half_life_s=math.inf, time_s=7.0)
    assert value == pytest.approx(35.0)
