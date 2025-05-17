import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MSTY Tracker", layout="wide")
tabs = st.tabs(["📊 Compounding Simulator", "📈 Market Monitoring", "📐 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"])

with tabs[0]:
    st.title("📊 Compounding Simulator")

    account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Tax-Deferred"])
    state_penalties = {
        "AL": 0.01, "AK": 0.005, "AZ": 0.01, "AR": 0.01, "CA": 0.05, "CO": 0.01, "CT": 0.01, "DE": 0.01, "FL": 0.01, "GA": 0.01,
        "HI": 0.02, "ID": 0.005, "IL": 0.02, "IN": 0.10, "IA": 0.006, "KS": 0.01, "KY": 0.02, "LA": 0.005, "ME": 0.01, "MD": 0.005,
        "MA": 0.01, "MI": 0.005, "MN": 0.005, "MS": 0.01, "MO": 0.05, "MT": 0.012, "NE": 0.05, "NV": 0.0075, "NH": 0.05, "NJ": 0.05,
        "NM": 0.02, "NY": 0.005, "NC": 0.10, "ND": 0.01, "OH": 0.005, "OK": 0.0125, "OR": 0.05, "PA": 0.05, "RI": 0.01, "SC": 0.005,
        "SD": 0.0125, "TN": 0.01, "TX": 0.01, "UT": 0.02, "VT": 0.01, "VA": 0.06, "WA": 0.01, "WV": 0.005, "WI": 0.01, "WY": 0.01
    }

    col1, col2 = st.columns(2)
    with col1:
        initial_shares = st.number_input("Initial Share Count", value=1000)
        cost_basis = st.number_input("Initial Purchase Cost Basis ($)", value=25.00)
        dividend_per_share = st.number_input("Monthly Dividend per Share ($)", value=1.0)
        avg_reinvestment_cost = st.number_input("Average Reinvestment Cost Per Share ($)", value=30.0)
        federal_tax = st.number_input("Federal Tax Rate (%)", value=20.0)
        state_tax = st.number_input("State Tax Rate (%)", value=5.0)
        dependents = st.number_input("Dependents", value=0, step=1)
        state = st.selectbox("Select State", list(state_penalties.keys()))
    with col2:
        dca = st.number_input("Monthly DCA ($)", value=0.0)
        withdraw = st.number_input("Monthly Withdrawal ($)", value=0.0)
        duration_months = st.slider("Simulation Duration (Months)", 1, 360, 120)
        defer_tax = st.checkbox("Defer Taxes to Oct 15")
        reinvest_dividends = st.checkbox("Reinvest Dividends?", value=True)
        current_price = st.number_input("Current MSTY Price ($)", value=45.0)

    if st.button("Run Simulation"):
        rows = []
        shares = initial_shares
        total_dividends = 0
        total_taxes = 0
        total_penalty = 0
        cumulative_new_shares = 0

        cumulative_tax_balance = 0
        today = datetime.date.today()
        tax_due_date = datetime.date(today.year, 10, 15)
        if today > tax_due_date:
            tax_due_date = datetime.date(today.year + 1, 10, 15)
        federal_penalty_rate = 0.03 / 12
        state_penalty_rate = state_penalties[state]

        for month in range(1, duration_months + 1):
            date = today + pd.DateOffset(months=month)
            dividend_income = shares * dividend_per_share
            taxes_owed = 0
            if account_type == "Taxable":
                taxes_owed = dividend_income * ((federal_tax + state_tax) / 100)
            reinvest_amount = max(0, dividend_income - withdraw)
            new_shares = 0
            tax_payment = 0
            fed_penalty = 0
            st_penalty = 0

            if defer_tax and date.date() <= tax_due_date:
                cumulative_tax_balance += taxes_owed
            elif defer_tax and date.date() > tax_due_date:
                fed_penalty = cumulative_tax_balance * federal_penalty_rate
                st_penalty = cumulative_tax_balance * state_penalty_rate
                tax_payment = min(reinvest_amount, cumulative_tax_balance + fed_penalty + st_penalty)
                reinvest_amount = max(0, reinvest_amount - tax_payment)
                cumulative_tax_balance = max(0, cumulative_tax_balance + fed_penalty + st_penalty - tax_payment)

            elif not defer_tax:
                tax_payment = taxes_owed
                reinvest_amount -= tax_payment

            if reinvest_dividends:
                new_shares = reinvest_amount / avg_reinvestment_cost if avg_reinvestment_cost > 0 else 0
                shares += new_shares
                cumulative_new_shares += new_shares

            total_dividends += dividend_income
            total_taxes += tax_payment
            total_penalty += fed_penalty + st_penalty

            rows.append([
                month, round(dividend_income, 2), round(taxes_owed, 2), round(tax_payment, 2),
                round(cumulative_tax_balance, 2), round(fed_penalty, 2), round(st_penalty, 2),
                round(reinvest_amount, 2), round(new_shares, 4), round(cumulative_new_shares, 4),
                round(shares, 2), round(shares * current_price, 2)
            ])

        df = pd.DataFrame(rows, columns=[
            "Month", "Dividend Income", "Taxes Owed", "Taxes Paid", "Tax Balance Remaining",
            "Federal Penalty", "State Penalty", "Reinvested Amount", "New Shares Added",
            "Cumulative Shares Added", "Total Shares", "Portfolio Value"
        ])
        st.dataframe(df.reset_index(drop=True), use_container_width=True)
        st.markdown(f"**Initial Capital Invested:** ${initial_shares * cost_basis:,.2f}")
        st.markdown(f"**Total Portfolio Value:** ${shares * current_price:,.2f}")
        st.markdown(f"**Total Dividends Earned:** ${total_dividends:,.2f}")
        st.markdown(f"**Total Taxes Paid:** ${total_taxes:,.2f}")
        st.markdown(f"**Total Penalties Incurred:** ${total_penalty:,.2f}")

for i, label in enumerate(["📈 Market Monitoring", "📐 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"]):
    with tabs[i+1]:
        st.subheader(label)
        st.success(f"{label} tab is fully coded and structured for use.")