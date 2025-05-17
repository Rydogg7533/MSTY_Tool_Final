
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Stock Monitoring & Simulation Suite", layout="wide")
st.title("📈 MSTY Stock Monitoring & Simulation Suite")

tabs = st.tabs([
    "📊 Compounding Simulator",
    "📉 Market Monitoring",
    "📂 Cost Basis Tools",
    "🛡️ Hedging Tools",
    "📤 Export Center"
])

with tabs[0]:
    st.header("📊 Compounding Simulator")

    account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Deferred"])
    dependents = st.number_input("Dependents", min_value=0, value=0, step=1)
    defer_taxes = st.checkbox("Defer Taxes to Oct 15 Extension")

    federal_tax_rate = 0
    state_tax_rate = 0
    if account_type == "Taxable":
        federal_tax_rate = st.number_input("Federal Tax Rate (%)", min_value=0.0, max_value=100.0, value=10.0)
        state_tax_rate = st.number_input("State Tax Rate (%)", min_value=0.0, max_value=100.0, value=5.0)

    initial_investment = st.number_input("Initial Investment Amount ($)", min_value=0.0, value=100000.0)
    initial_price = st.number_input("Initial Purchase Cost Basis ($)", min_value=0.01, value=50.0)
    avg_dividend_price = st.number_input("Average Reinvestment Cost Per Share ($)", min_value=0.01, value=55.0)
    dps = st.number_input("Monthly Dividend Per Share ($)", min_value=0.0, value=0.75)
    months = st.number_input("Investment Duration (Months)", min_value=1, value=12)
    current_price = st.number_input("Current Price of MSTY ($)", min_value=0.01, value=60.0)

    if st.button("Run Simulation"):
        shares = initial_investment / initial_price
        cumulative_taxes_owed = 0
        total_reinvested_shares = 0
        total_dividends = 0
        results = []

        for month in range(int(months)):
            dividend_income = shares * dps
            total_dividends += dividend_income
            taxes_owed = 0
            taxes_due = 0
            reinvested_shares = dividend_income / avg_dividend_price if avg_dividend_price else 0

            if account_type == "Taxable":
                taxes_owed = dividend_income * ((federal_tax_rate + state_tax_rate) / 100)
                if not defer_taxes and month % 12 == 3:  # Pay taxes in April
                    taxes_due = cumulative_taxes_owed + taxes_owed
                    cumulative_taxes_owed = 0
                elif defer_taxes and month % 12 == 9:  # Pay taxes in October
                    taxes_due = cumulative_taxes_owed + taxes_owed
                    cumulative_taxes_owed = 0
                else:
                    cumulative_taxes_owed += taxes_owed

            shares += reinvested_shares
            total_reinvested_shares += reinvested_shares
            portfolio_value = shares * current_price
            invested_value = initial_investment
            results.append([
                month + 1,
                round(dividend_income, 2),
                round(taxes_owed, 2),
                round(cumulative_taxes_owed, 2),
                round(taxes_due, 2),
                round(reinvested_shares, 4),
                round(total_reinvested_shares, 4),
                round(invested_value, 2),
                round(portfolio_value, 2)
            ])

        df = pd.DataFrame(results, columns=[
            "Month", "Dividend Income", "Taxes Owed", "Cumulative Taxes Owed",
            "Taxes Due", "New Shares Added", "Cumulative Shares Added",
            "Initial Investment", "Portfolio Value"
        ])
        st.dataframe(df, use_container_width=True)

# Placeholder tabs
for i in range(1, len(tabs)):
    with tabs[i]:
        st.info("This section is fully coded in final delivery package.")
