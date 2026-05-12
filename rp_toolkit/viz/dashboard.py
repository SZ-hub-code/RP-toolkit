"""Reusable Streamlit UI blocks for RP toolkit pages."""

from __future__ import annotations

import streamlit as st

from rp_toolkit.core.dose_rate import available_nuclides


def section_header(title: str, subtitle: str = "") -> None:
    """Render a page section title and optional subtitle."""
    st.subheader(title)
    if subtitle:
        st.caption(subtitle)


def source_scenario_inputs(default_nuclide: str = "cs-137") -> dict[str, float | str]:
    """Render standard source input widgets and return values."""
    nuclides = available_nuclides()
    default_key = default_nuclide.strip().lower()
    default_index = next(
        (index for index, nuclide in enumerate(nuclides) if nuclide.lower() == default_key),
        0,
    )

    nuclide = st.selectbox("Nuclide", options=nuclides, index=default_index)
    activity_bq = st.number_input("Activity (Bq)", min_value=0.0, value=1e9, step=1e8, format="%.3e")
    distance_m = st.number_input("Distance (m)", min_value=0.01, value=1.0, step=0.1)
    occupancy = st.slider("Occupancy factor", min_value=0.0, max_value=1.0, value=1.0, step=0.05)

    return {
        "nuclide": nuclide,
        "activity_bq": float(activity_bq),
        "distance_m": float(distance_m),
        "occupancy_factor": float(occupancy),
    }


def dose_metrics(rate_u_sv_h: float, integrated_u_sv: float) -> None:
    """Render key metric cards for source calculations."""
    col1, col2 = st.columns(2)
    col1.metric("Dose rate", f"{rate_u_sv_h:,.3f} uSv/h")
    col2.metric("Integrated dose", f"{integrated_u_sv:,.3f} uSv")
