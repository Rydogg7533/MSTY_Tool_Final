import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="MSTY Financial Suite", layout="wide")

tabs = st.tabs(["Compounding Simulator", "Market Monitoring", "Cost Basis Tools", "Hedging Tools", "Export Center"])

with tabs[0]:
    st.title("Compounding Simulator")

    col1, col2 = st.columns(2)
    with col1:
        initial_shares = st.number_input("Initial Share Count", value=1000)
        avg_reinvest_cost = st.number_input("Average Reinvestment Cost Per Share", value=25.0)
        dividend_per_share = st.number_input("Monthly Dividend Per Share", value=1.0)
        federal_tax_rate = st.number_input("Federal Tax Rate (%)", value=20.0)
        state_tax_rate = st.number_input("State Tax Rate (%)", value=5.0)
        dependents = st.number_input("Dependents", value=0, step=1)
        defer_taxes = st.checkbox("Defer Taxes to Oct 15 Extension")
        state = st.selectbox("Select Your State", ["CA", "TX", "NY", "FL", "Other"])
    with col2:
        dca = st.number_input("Monthly DCA Investment", value=0.0)
        monthly_withdrawal = st.number_input("Monthly Withdrawal Amount", value=0.0)
        account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Deferred"])
        view_by = st.selectbox("View By", ["Monthly", "Yearly", "Total"])

    if st.button("Run Simulation"):
        months = 12
        current_date = datetime.datetime.now()
        tax_due_date = datetime.datetime(current_date.year, 10, 15)
        if current_date > tax_due_date:
            tax_due_date = tax_due_date.replace(year=current_date.year + 1)

        data = []
        shares = initial_shares
        total_dividends = 0
        tax_balance = 0
        federal_penalty_rate = 0.5 / 100
        state_penalty_rate = 0.25 / 100

        for month in range(1, months + 1):
            dividend_income = shares * dividend_per_share
            if account_type == "Taxable":
                tax_owed = dividend_income * (federal_tax_rate + state_tax_rate) / 100
            else:
                tax_owed = 0
            taxes_due = 0
            fed_penalty = 0
            state_penalty = 0
            if defer_taxes and current_date + datetime.timedelta(days=month*30) > tax_due_date:
                fed_penalty = tax_balance * federal_penalty_rate
                state_penalty = tax_balance * state_penalty_rate
                taxes_due = min(dividend_income, tax_balance + fed_penalty + state_penalty)
                tax_balance = max(0, tax_balance + fed_penalty + state_penalty - taxes_due)
            else:
                taxes_due = tax_owed
                tax_balance += tax_owed

            net_dividends = dividend_income - taxes_due - monthly_withdrawal
            shares += (net_dividends + dca) / avg_reinvest_cost
            data.append([month, dividend_income, tax_owed, taxes_due, tax_balance, fed_penalty, state_penalty, shares])

        df = pd.DataFrame(data, columns=["Month", "Dividend Income", "Taxes Owed", "Taxes Due",
                                         "Cumulative Tax Balance", "Federal Penalty", "State Penalty",
                                         "Cumulative Shares"])
        st.dataframe(df)

with tabs[1]:
    st.title("Market Monitoring")
    st.info("Live options, covered call, and IV tracking will be shown here.")

with tabs[2]:
    st.title("Cost Basis Tools")
    st.info("Tools to calculate average cost basis and track your positions.")

with tabs[3]:
    st.title("Hedging Tools")
    st.info("Options and futures based strategies to hedge your MSTY holdings.")

with tabs[4]:
    st.title("Export Center")
    st.info("Export your simulations and reports to PDF or email.")