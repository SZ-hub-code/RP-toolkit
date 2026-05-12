"""Streamlit entry point for RP toolkit."""

import streamlit as st

st.set_page_config(page_title="RP Toolkit", layout="wide")

st.title("RP Toolkit")
st.caption("Radioprotection calculations: source dose, shielding and decay chains.")

st.markdown(
    """
Bienvenue dans RP Toolkit.

Utilisez la barre laterale de Streamlit pour ouvrir les pages:

1. Source calculator
2. Shielding
3. Decay chain
"""
)

st.info("Commande de lancement: streamlit run app/main.py")
