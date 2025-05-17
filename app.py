
# Streamlit MSTY Compounding Tool - Fixed Logic
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Tracker", layout="wide")
tabs = st.tabs(["Compounding Simulator", "Market Monitoring", "Cost Basis", "Hedging", "Export Center"])

# Compounding Tool
with tabs[0]:
    st.header("Compounding Simulator")

    col1, col2, col3, col4 = st.columns(4)
    init_invest = col1.number_input("Initial Investment ($)", value=100000)
    init_cost_basis = col2.number_input("Initial Purchase Cost Basis ($/share)", value=250.0)
    dividend_per_share = col3.number_input("Average Monthly Dividend ($/share)", value=5.0)
    avg_dividend_cost = col4.number_input("Avg Dividend Cost Per Share ($)", value=250.0)

    col5, col6, col7 = st.columns(3)
    account_type = col5.selectbox("Account Type", ["Taxable", "Non-Taxable", "Deferred"])
    fed_tax = col6.number_input("Federal Tax Rate (%)", value=20) if account_type == "Taxable" else 0
    state_tax = col7.number_input("State Tax Rate (%)", value=5) if account_type == "Taxable" else 0

    col8, col9 = st.columns(2)
    current_price = col8.number_input("Current MSTY Price ($)", value=400.0)
    dependents = col9.number_input("Dependents", value=0, step=1)

    defer_tax = st.checkbox("Defer Taxes to Oct 15 Extension")
    tax_month_due = 10 if defer_tax else 4
    months = st.slider("Number of Months", 1, 60, 12)
    run_button = st.button("Run Simulation")

    if run_button:
        tax_rate = (fed_tax + state_tax) / 100
        shares = init_invest / init_cost_basis
        cumulative_taxes = 0
        cumulative_shares = shares
        results = []

        for m in range(1, months + 1):
            dividend_income = shares * dividend_per_share
            taxes_owed = dividend_income * tax_rate if account_type == "Taxable" else 0
            cumulative_taxes += taxes_owed
            taxes_due = taxes_owed if m % 12 == tax_month_due else 0

            new_shares = dividend_income / avg_dividend_cost if account_type != "Non-Taxable" else 0
            if account_type == "Taxable" and not defer_tax and taxes_due > 0:
                new_shares = (dividend_income - taxes_due) / avg_dividend_cost

            reinvest_value = new_shares * current_price
            reinvest_cost = new_shares * avg_dividend_cost
            reinvest_profit = reinvest_value - reinvest_cost

            shares += new_shares
            cumulative_shares += new_shares

            results.append([
                m,
                round(dividend_income, 2),
                round(taxes_owed, 2),
                round(cumulative_taxes, 2),
                round(taxes_due, 2),
                round(new_shares, 4),
                round(cumulative_shares, 4),
                round(reinvest_profit, 2)
            ])

        df = pd.DataFrame(results, columns=[
            "Month", "Dividend Income", "Taxes Owed", "Cumulative Taxes",
            "Taxes Due", "New Shares Added", "Cumulative Shares", "Profit/Loss on Reinvestment"
        ])
        st.dataframe(df, use_container_width=True)

        st.markdown(f"**Initial Capital Invested:** ${init_invest:,.2f}")
        portfolio_value = cumulative_shares * current_price
        st.markdown(f"**Total Current Portfolio Value:** ${portfolio_value:,.2f}")
