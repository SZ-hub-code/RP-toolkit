"""Streamlit page for radioactive decay chain exploration."""

import pandas as pd
import streamlit as st

from rp_toolkit.core.decay import decay_chain_activities

st.set_page_config(page_title="Decay Chain", layout="wide")
st.subheader("Decay Chain")
st.caption("Parent and progeny activities after a given time")

col1, col2, col3 = st.columns(3)
with col1:
    parent = st.text_input("Parent nuclide", value="Cs-137")
with col2:
    a0_bq = st.number_input("Initial activity (Bq)", min_value=0.0, value=1e6, step=1e5, format="%.3e")
with col3:
    time_value = st.number_input("Time", min_value=0.0, value=30.0, step=1.0)

unit = st.selectbox("Unit", options=["s", "min", "h", "d", "y"], index=3)

try:
    activities = decay_chain_activities(parent, float(a0_bq), float(time_value), unit)
    dataframe = pd.DataFrame(
        [{"nuclide": nuclide, "activity_bq": value} for nuclide, value in activities.items()]
    ).sort_values("activity_bq", ascending=False)
    st.dataframe(dataframe, use_container_width=True)
except Exception as exc:
    st.error(f"Unable to compute decay chain: {exc}")
