import pytest

from rp_toolkit.viz.plots import plot_isodose_2d


def test_plot_isodose_2d_rejects_negative_activity() -> None:
    with pytest.raises(ValueError, match="Activity must be non-negative."):
        plot_isodose_2d("Cs-137", activity_bq=-1.0)
