from pathlib import Path

import pytest

from rp_toolkit.io.csv_reader import read_measurements_csv


def test_csv_reader_normalizes_dose_rate_column(tmp_path: Path) -> None:
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text("timestamp,dose_rate,distance\n2026-01-01 12:00,1.5,2.0\n", encoding="utf-8")

    dataframe = read_measurements_csv(csv_path)

    assert "dose_rate_uSv_h" in dataframe.columns
    assert dataframe.loc[0, "dose_rate_uSv_h"] == 1.5
    assert dataframe.loc[0, "distance_m"] == 2.0


def test_csv_reader_rejects_duplicate_columns_after_normalization(tmp_path: Path) -> None:
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text("dose_rate,distance,distance_m\n1.5,2.0,2.5\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Column normalization produced duplicate columns:"):
        read_measurements_csv(csv_path)
