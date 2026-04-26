"""Matplotlib plots for dose profile and 2D isodose maps."""

from __future__ import annotations

from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np

from rp_toolkit.core.dose_rate import dose_rate_point_source, gamma_constant


def plot_dose_vs_distance(
    nuclide: str,
    activity_bq: float,
    distances_m: Iterable[float],
) -> tuple[plt.Figure, plt.Axes]:
    """Plot dose rate versus distance for a point source."""
    distances = np.array(list(distances_m), dtype=float)
    if np.any(distances <= 0):
        raise ValueError("All distances must be strictly positive.")

    rates = np.array([dose_rate_point_source(nuclide, activity_bq, float(d)) for d in distances])

    figure, axis = plt.subplots(figsize=(8, 4.8))
    axis.plot(distances, rates, linewidth=2.0)
    axis.set_xscale("log")
    axis.set_yscale("log")
    axis.set_xlabel("Distance (m)")
    axis.set_ylabel("Dose rate (uSv/h)")
    axis.set_title(f"Dose rate vs distance - {nuclide}")
    axis.grid(True, which="both", linestyle="--", linewidth=0.6, alpha=0.6)
    return figure, axis


def plot_isodose_2d(
    nuclide: str,
    activity_bq: float,
    extent_m: float = 5.0,
    resolution: int = 150,
    min_radius_m: float = 0.05,
) -> tuple[plt.Figure, plt.Axes]:
    """Plot a 2D isodose map in a horizontal plane around a point source."""
    if extent_m <= 0:
        raise ValueError("extent_m must be strictly positive.")
    if resolution < 20:
        raise ValueError("resolution must be >= 20.")

    axis_values = np.linspace(-extent_m, extent_m, resolution)
    x_grid, y_grid = np.meshgrid(axis_values, axis_values)
    radius = np.sqrt(x_grid**2 + y_grid**2)
    radius = np.clip(radius, min_radius_m, None)

    gamma = gamma_constant(nuclide)
    activity_mbq = activity_bq / 1e6
    dose_map = gamma * activity_mbq / (radius**2)

    figure, axis = plt.subplots(figsize=(6, 6))
    contour = axis.contourf(x_grid, y_grid, dose_map, levels=20, cmap="viridis")
    cbar = figure.colorbar(contour, ax=axis)
    cbar.set_label("Dose rate (uSv/h)")

    axis.set_xlabel("x (m)")
    axis.set_ylabel("y (m)")
    axis.set_title(f"Isodose map - {nuclide}")
    axis.set_aspect("equal")
    return figure, axis
