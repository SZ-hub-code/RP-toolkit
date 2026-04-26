"""CSV readers for field measurements and lab exports."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


COLUMN_ALIASES = {
    "timestamp": "timestamp",
    "date": "timestamp",
    "datetime": "timestamp",
    "location": "location",
    "site": "location",
    "nuclide": "nuclide",
    "isotope": "nuclide",
    "activity_bq": "activity_bq",
    "activity": "activity_bq",
    "distance_m": "distance_m",
    "distance": "distance_m",
    "dose_rate": "dose_rate_uSv_h",
    "dose_rate_usv_h": "dose_rate_uSv_h",
    "dose_rate_uh": "dose_rate_uSv_h",
    "dose_u_sv_h": "dose_rate_uSv_h",
}


REQUIRED_COLUMNS = {"dose_rate_uSv_h"}


def _normalize_column_name(name: str) -> str:
    normalized = name.strip().lower().replace(" ", "_")
    return COLUMN_ALIASES.get(normalized, normalized)


def validate_measurements_schema(dataframe: pd.DataFrame) -> None:
    """Validate minimum schema and basic value constraints."""
    missing = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

    if (dataframe["dose_rate_uSv_h"] < 0).any():
        raise ValueError("Dose rate values must be non-negative.")

    if "distance_m" in dataframe.columns and (dataframe["distance_m"] <= 0).any():
        raise ValueError("distance_m values must be strictly positive.")

    if "activity_bq" in dataframe.columns and (dataframe["activity_bq"] < 0).any():
        raise ValueError("activity_bq values must be non-negative.")


def read_measurements_csv(file_path: str | Path, sep: str = ",", decimal: str = ".") -> pd.DataFrame:
    """Load and normalize measurement CSV with lightweight schema checks."""
    dataframe = pd.read_csv(file_path, sep=sep, decimal=decimal)
    dataframe = dataframe.rename(columns={col: _normalize_column_name(col) for col in dataframe.columns})

    if "timestamp" in dataframe.columns:
        dataframe["timestamp"] = pd.to_datetime(dataframe["timestamp"], errors="coerce")

    validate_measurements_schema(dataframe)
    return dataframe
