import streamlit as st
from tabs.compounding_simulator import show_compounding_simulator
from tabs.cost_basis_tab import show_cost_basis_tab
from tabs.hedging_tool import show_hedging_tool

st.set_page_config(page_title="MSTY Financial Suite", layout="wide")

tab = st.sidebar.selectbox("Select a Tool", ["Compounding Simulator", "Cost Basis Tracker", "Hedging Tool"])

if tab == "Compounding Simulator":
    show_compounding_simulator()
elif tab == "Cost Basis Tracker":
    show_cost_basis_tab()
elif tab == "Hedging Tool":
    show_hedging_tool()
