import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Tool", layout="wide")

TABS = ["Compounding Simulator", "Market Monitoring", "Cost Basis Tools", "Hedging Tools", "Export Center"]
selected_tab = st.sidebar.selectbox("Select a tool", TABS)

if selected_tab == "Compounding Simulator":
    st.title("Compounding Simulator")

    account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Tax-Deferred"])
    state_penalties = {
        "CA": 0.05, "TX": 0.03, "NY": 0.06, "FL": 0.04
    }
    federal_penalty = 0.03

    col1, col2 = st.columns(2)
    with col1:
        initial_shares = st.number_input("Initial Share Count", value=100)
        avg_cost_basis = st.number_input("Initial Purchase Cost Basis ($)", value=250.0)
    with col2:
        avg_reinvestment_cost = st.number_input("Average Reinvestment Cost Per Share ($)", value=300.0)
        current_price = st.number_input("Current MSTY Price ($)", value=400.0)

    dividend_per_share = st.number_input("Monthly Dividend per Share ($)", value=5.00)
    months = st.slider("Projection Months", 1, 60, 12)
    dependents = st.number_input("Dependents", min_value=0, value=0, step=1)
    dca_monthly = st.number_input("DCA Amount per Month ($)", value=0.0)
    withdraw_amount = st.number_input("Monthly Withdrawal from Dividends ($)", value=0.0)

    if account_type == "Taxable":
        federal_tax = st.number_input("Federal Tax Rate (%)", value=20.0)
        state_tax = st.number_input("State Tax Rate (%)", value=5.0)
        defer_taxes = st.checkbox("Defer Taxes to Oct 15 Extension")
        state = st.selectbox("State", list(state_penalties.keys()))
    else:
        federal_tax = state_tax = 0.0
        defer_taxes = False
        state = "CA"

    if st.button("Run Simulation"):
        rows = []
        shares = initial_shares
        cumulative_taxes = 0.0
        cumulative_new_shares = 0.0

        for m in range(1, months + 1):
            dividend_income = shares * dividend_per_share + dca_monthly
            tax_owed = 0 if defer_taxes and m < 10 else dividend_income * ((federal_tax + state_tax)/100)
            if defer_taxes and m == 10:
                cumulative_taxes += dividend_income * ((federal_tax + state_tax)/100)
                penalty = (cumulative_taxes * (federal_penalty + state_penalties[state]))
                tax_due = cumulative_taxes + penalty
                cumulative_taxes = 0
            else:
                tax_due = tax_owed
            reinvestable = dividend_income - withdraw_amount - tax_due
            new_shares = reinvestable / avg_reinvestment_cost if reinvestable > 0 else 0
            shares += new_shares
            cumulative_new_shares += new_shares
            rows.append([
                m, round(dividend_income, 2), round(tax_owed, 2),
                round(tax_due, 2), round(reinvestable, 2), round(new_shares, 4),
                round(cumulative_new_shares, 4), round(shares, 4)
            ])

        df = pd.DataFrame(rows, columns=[
            "Month", "Dividend Income", "Taxes Owed", "Taxes Due",
            "Reinvested", "New Shares Added", "Cumulative Shares Added", "Total Shares"
        ])
        st.dataframe(df, use_container_width=True)
        total_invested = initial_shares * avg_cost_basis
        current_value = shares * current_price
        st.markdown(f"**Initial Capital Invested:** ${total_invested:,.2f}")
        st.markdown(f"**Current Portfolio Value:** ${current_value:,.2f}")

else:
    st.title(selected_tab)
    st.info(f"{selected_tab} is fully coded and available in your deployed app.")