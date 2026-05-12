"""Streamlit page for shielding attenuation calculations."""

import streamlit as st

from rp_toolkit.core.shielding import (
    attenuated_dose_rate,
    attenuation_coefficient,
    available_materials,
    hvl,
    required_thickness,
    tvl,
)

st.set_page_config(page_title="Shielding", layout="wide")
st.subheader("Shielding")
st.caption("Attenuation with linear coefficient, HVL and TVL")

col1, col2 = st.columns(2)

with col1:
    input_rate = st.number_input("Input dose rate (uSv/h)", min_value=0.0, value=100.0)
    material = st.selectbox("Material", options=available_materials())
    energy_mev = st.number_input("Photon energy (MeV)", min_value=0.01, value=0.662, step=0.05)

with col2:
    thickness_m = st.number_input("Thickness (m)", min_value=0.0, value=0.05, step=0.01)
    buildup = st.number_input("Buildup factor", min_value=0.1, value=1.0, step=0.1)
    target_attenuation = st.number_input("Target attenuation ratio Din/Dout", min_value=1.0, value=10.0)

mu = attenuation_coefficient(material, float(energy_mev))
output_rate = attenuated_dose_rate(float(input_rate), mu, float(thickness_m), float(buildup))

metric1, metric2, metric3 = st.columns(3)
metric1.metric("mu (m^-1)", f"{mu:.3f}")
metric2.metric("Output dose rate", f"{output_rate:.3f} uSv/h")
metric3.metric("Required thickness", f"{required_thickness(mu, float(target_attenuation), float(buildup)):.4f} m")

st.write(f"HVL: {hvl(mu):.4f} m")
st.write(f"TVL: {tvl(mu):.4f} m")
