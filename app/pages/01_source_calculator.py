"""Streamlit page for point source dose calculations."""

import numpy as np
import streamlit as st

from rp_toolkit.core.alara import integrated_dose
from rp_toolkit.core.dose_rate import DoseScenario
from rp_toolkit.viz.dashboard import dose_metrics, section_header, source_scenario_inputs
from rp_toolkit.viz.plots import plot_dose_vs_distance

st.set_page_config(page_title="Source Calculator", layout="wide")
section_header("Source Calculator", "Dose rate from gamma constants and inverse-square law")

inputs = source_scenario_inputs(default_nuclide="cs-137")
exposure_time_h = st.number_input("Exposure time (h)", min_value=0.0, value=1.0, step=0.5)

scenario = DoseScenario(
    nuclide=str(inputs["nuclide"]),
    activity_bq=float(inputs["activity_bq"]),
    distance_m=float(inputs["distance_m"]),
    occupancy_factor=float(inputs["occupancy_factor"]),
)

rate = scenario.dose_rate_uSv_h()
dose = integrated_dose(rate, float(exposure_time_h))
dose_metrics(rate, dose)

st.markdown(f"**Zone classification:** {scenario.zone()}")

distances = np.logspace(-1, 1.5, 120)
figure, _ = plot_dose_vs_distance(scenario.nuclide, scenario.activity_bq, distances)
st.pyplot(figure, use_container_width=True)
