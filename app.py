import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Tracker", layout="wide")

tabs = st.tabs(["📈 Compounding Simulator", "📊 Market Monitoring", "📉 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"])

with tabs[0]:
    st.header("📈 Compounding Simulator")
    shares = st.number_input("Initial Share Count", value=1000)
    price_per_share = st.number_input("Average Share Price", value=300.0)
    dividend_per_share = st.number_input("Monthly Dividend per Share", value=5.0)
    tax_rate = st.number_input("Federal Tax Rate (%)", value=20.0) / 100
    state_tax_rate = st.number_input("State Tax Rate (%)", value=5.0) / 100
    dependents = st.number_input("Dependents", value=0)
    defer_tax = st.checkbox("Defer Taxes to Oct 15 Extension")
    months = st.number_input("Projection Months", value=12)
    view_by = st.selectbox("View By", ["Monthly", "Yearly", "Total"])

    if st.button("Run Simulation"):
        df = pd.DataFrame(columns=[
            "Month", "Dividend Income", "Taxes Owed", "Cumulative Taxes Owed",
            "New Shares", "Cumulative Shares Added"
        ])
        cumulative_dividends = 0
        cumulative_taxes = 0
        cumulative_shares = 0
        current_shares = shares

        for month in range(1, int(months)+1):
            dividend_income = current_shares * dividend_per_share
            tax = 0 if defer_tax else dividend_income * (tax_rate + state_tax_rate)
            cumulative_taxes += 0 if defer_tax else tax
            reinvestable = dividend_income if defer_tax else dividend_income - tax
            new_shares = reinvestable / price_per_share
            cumulative_shares += new_shares
            current_shares += new_shares
            df.loc[month] = [
                month, round(dividend_income, 2), round(tax, 2), round(cumulative_taxes, 2),
                round(new_shares, 4), round(cumulative_shares, 4)
            ]

        st.dataframe(df.reset_index(drop=True), use_container_width=True)

with tabs[1]:
    st.header("📊 Market Monitoring")
    st.info("Live options, covered call, and IV tracking will be shown here.")

with tabs[2]:
    st.header("📉 Cost Basis Tools")
    st.info("Weighted cost tracking calculator will be developed here.")

with tabs[3]:
    st.header("🛡️ Hedging Tools")
    st.info("Live options pricing and coverage calculator will go here.")

with tabs[4]:
    st.header("📤 Export Center")
    st.info("PDF and email export functions will be activated here.")
