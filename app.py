
import streamlit as st
from tabs.compounding_simulator import show_compounding_simulator
from tabs.cost_basis import show_cost_basis
from tabs.hedging_tool import show_hedging_tool

st.set_page_config(page_title="MSTY Tool Suite", layout="wide")

tabs = {
    "Compounding Simulator": show_compounding_simulator,
    "Cost Basis Tracker": show_cost_basis,
    "Hedging Tool": show_hedging_tool,
}

selection = st.sidebar.radio("Select Tool", list(tabs.keys()))
tabs[selection]()
