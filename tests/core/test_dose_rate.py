import pytest

from rp_toolkit.core.dose_rate import dose_rate_point_source, inverse_square_scale


def test_inverse_square_law_exact_case() -> None:
    assert inverse_square_scale(100.0, 1.0, 2.0) == pytest.approx(25.0)


def test_point_source_rate_is_positive() -> None:
    rate = dose_rate_point_source("Cs-137", 1e9, 1.0)
    assert rate > 0


def test_dose_rate_distance_change_matches_scaling() -> None:
    rate_1m = dose_rate_point_source("Cs-137", 1e9, 1.0)
    rate_2m = dose_rate_point_source("Cs-137", 1e9, 2.0)
    assert rate_2m == pytest.approx(inverse_square_scale(rate_1m, 1.0, 2.0))
