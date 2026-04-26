from pathlib import Path

from rp_toolkit.io.csv_reader import read_measurements_csv


def test_csv_reader_normalizes_dose_rate_column(tmp_path: Path) -> None:
    csv_path = tmp_path / "measurements.csv"
    csv_path.write_text("timestamp,dose_rate,distance\n2026-01-01 12:00,1.5,2.0\n", encoding="utf-8")

    dataframe = read_measurements_csv(csv_path)

    assert "dose_rate_uSv_h" in dataframe.columns
    assert dataframe.loc[0, "dose_rate_uSv_h"] == 1.5
    assert dataframe.loc[0, "distance_m"] == 2.0
