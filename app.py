import streamlit as st

st.set_page_config(page_title="MSTY Compounding Simulator", layout="wide")
st.title("Compounding Simulator")

current_price = st.number_input("Current MSTY Price ($)", value=45.0)
st.write(f"The current MSTY price is: ${current_price}")
