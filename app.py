import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Tracker", layout="wide")
st.title("📊 MSTY Tracker")

tabs = st.tabs(["📊 Compounding Simulator", "📐 Cost Basis Tools"])

# Placeholder for Compounding tab
with tabs[0]:
    st.markdown("Coming soon: Compounding Simulator")

# Cost Basis Tools tab
with tabs[1]:
    st.header("📐 MSTY Cost Basis Calculator")

    if "blocks" not in st.session_state:
        st.session_state["blocks"] = []

    st.subheader("Add Purchase Block")
    shares = st.number_input("Number of Shares", min_value=1, value=100)
    price = st.number_input("Price per Share ($)", min_value=0.01, value=25.00)
    if st.button("Add Block"):
        st.session_state["blocks"].append({"Shares": shares, "Price": price})

    if st.session_state["blocks"]:
        df = pd.DataFrame(st.session_state["blocks"])
        df["Total Cost"] = df["Shares"] * df["Price"]
        total_shares = df["Shares"].sum()
        total_cost = df["Total Cost"].sum()
        avg_cost = total_cost / total_shares if total_shares > 0 else 0

        st.markdown("### Purchase History")
        st.dataframe(df)

        st.markdown("### Summary")
        st.success(f"Total Shares: {total_shares}")
        st.success(f"Total Cost: ${total_cost:,.2f}")
        st.success(f"Weighted Average Cost per Share: ${avg_cost:.2f}")

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "cost_basis_blocks.csv", "text/csv")
    else:
        st.info("No blocks added yet.")