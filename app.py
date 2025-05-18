
import streamlit as st
from tabs.compounding_simulator import show_compounding_simulator
from tabs.cost_basis import show_cost_basis
from tabs.hedging_tool import show_hedging_tool

st.set_page_config(page_title="MSTY Tool Suite", layout="wide")
tab = st.sidebar.radio("Select a Tool", ["Compounding Simulator", "Cost Basis Tool", "Hedging Tool"])

if tab == "Compounding Simulator":
    show_compounding_simulator()
elif tab == "Cost Basis Tool":
    show_cost_basis()
elif tab == "Hedging Tool":
    show_hedging_tool()
