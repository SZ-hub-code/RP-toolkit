import math

import pytest

from rp_toolkit.core.shielding import attenuated_dose_rate, hvl, required_thickness, transmission_factor


def test_hvl_formula() -> None:
    mu = 10.0
    assert hvl(mu) == pytest.approx(math.log(2.0) / mu)


def test_attenuation_at_hvl_is_half_without_buildup() -> None:
    mu = 10.0
    dose_out = attenuated_dose_rate(100.0, mu, hvl(mu), buildup_factor=1.0)
    assert dose_out == pytest.approx(50.0)


def test_transmission_with_zero_thickness_equals_buildup() -> None:
    assert transmission_factor(mu_m_inv=5.0, thickness_m=0.0, buildup_factor=1.2) == pytest.approx(1.2)


def test_required_thickness_matches_closed_form_without_buildup() -> None:
    mu = 8.0
    attenuation = 10.0
    assert required_thickness(mu, attenuation, buildup_factor=1.0) == pytest.approx(math.log(attenuation) / mu)


def test_required_thickness_increases_with_buildup_factor() -> None:
    mu = 8.0
    attenuation = 10.0
    without_buildup = required_thickness(mu, attenuation, buildup_factor=1.0)
    with_buildup = required_thickness(mu, attenuation, buildup_factor=1.5)

    assert with_buildup > without_buildup
    assert with_buildup == pytest.approx((math.log(attenuation) + math.log(1.5)) / mu)
