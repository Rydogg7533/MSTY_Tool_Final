
import streamlit as st
from tabs.compounding_simulator import show_compounding_simulator
from tabs.cost_basis_tracker import show_cost_basis_tracker
from tabs.hedging_tool import show_hedging_tool

# Set page configuration
st.set_page_config(page_title="MSTY Tracker", layout="wide")

# App navigation
st.sidebar.title("Navigation")
tab = st.sidebar.radio("Go to", ["Compounding Simulator", "Cost Basis Tracker", "Hedging Tool"])

if tab == "Compounding Simulator":
    show_compounding_simulator()
elif tab == "Cost Basis Tracker":
    show_cost_basis_tracker()
elif tab == "Hedging Tool":
    show_hedging_tool()
