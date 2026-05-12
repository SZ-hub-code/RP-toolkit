import pytest

from rp_toolkit.core.nuc_db import Nuclide


def test_n_half_lives_rejects_unsupported_unit() -> None:
    nuclide = Nuclide("Cs-137")
    with pytest.raises(ValueError, match="Unsupported unit 'week'"):
        nuclide.n_half_lives(1.0, unit="week")
