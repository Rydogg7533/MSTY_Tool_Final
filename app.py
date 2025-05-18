import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(page_title="MSTY Compounding Simulator", layout="wide")
st.title("📊 MSTY Compounding Simulator")

# User Inputs
initial_shares = st.number_input("Initial Share Count", min_value=0, value=1000)
initial_cost_basis = st.number_input("Initial Purchase Cost Basis ($)", min_value=0.0, value=25.00)
avg_div_per_share = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.0)
avg_reinvest_cost = st.number_input("Average Reinvestment Cost Per Share ($)", min_value=0.01, value=25.0)
fed_tax_rate = st.slider("Federal Tax Rate (%)", 0, 50, 20)
state = st.selectbox("Select Your State", ["CA", "TX", "NY", "FL", "Other"])
state_penalty_rates = {"CA": 0.05, "TX": 0.01, "NY": 0.05, "FL": 0.01, "Other": 0.03}
state_tax_rate = st.slider("State Tax Rate (%)", 0, 20, 5)
dependents = st.number_input("Number of Dependents", min_value=0, value=0)
account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Tax-Deferred"])
defer_taxes = st.checkbox("Defer Taxes to Oct 15 Extension Deadline")
withdrawal = st.number_input("Withdraw this Dollar Amount Monthly ($)", min_value=0.0, value=0.0)
dca = st.number_input("Add Capital Monthly (DCA) ($)", min_value=0.0, value=0.0)
current_price = st.number_input("Current MSTY Price ($)", value=45.0)
months = st.slider("Holding Period (Months)", 1, 360, 60)
run_sim = st.button("Run Simulation")

if run_sim:
    start_date = datetime.today().replace(day=1)
    shares = initial_shares
    cumulative_reinvested = 0
    cumulative_withdrawn = 0
    cumulative_dividends = 0
    cumulative_tax_owed = 0
    cumulative_tax_paid = 0
    cumulative_penalties = 0
    cumulative_shares_added = 0
    tax_balance = 0
    tax_due_date = datetime(start_date.year + 1, 10, 15)

    data = []
    for i in range(months):
        date = start_date + relativedelta(months=i)
        div_income = shares * avg_div_per_share
        gross_cash = div_income + dca
        tax_owed = 0 if account_type != "Taxable" else div_income * (fed_tax_rate + state_tax_rate) / 100
        tax_paid = 0
        fed_penalty = 0
        state_penalty = 0

        if defer_taxes and date < tax_due_date:
            tax_balance += tax_owed
        elif defer_taxes and date >= tax_due_date:
            fed_penalty = tax_balance * 0.03 / 12
            state_penalty = tax_balance * state_penalty_rates[state] / 12
            penalties = fed_penalty + state_penalty
            total_due = tax_balance + penalties
            tax_paid = min(gross_cash - withdrawal, total_due)
            tax_balance = max(0, total_due - tax_paid)
            cumulative_penalties += penalties
        elif not defer_taxes and account_type == "Taxable":
            tax_paid = tax_owed

        net_cash = max(0, gross_cash - withdrawal - tax_paid)
        new_shares = net_cash / avg_reinvest_cost if avg_reinvest_cost else 0
        shares += new_shares

        cumulative_reinvested += net_cash
        cumulative_withdrawn += withdrawal
        cumulative_dividends += div_income
        cumulative_tax_owed += tax_owed
        cumulative_tax_paid += tax_paid
        cumulative_shares_added += new_shares

        profit_loss = (current_price - avg_reinvest_cost) * new_shares if avg_reinvest_cost else 0

        data.append({
            "Date": date.strftime("%Y-%m-%d"),
            "Dividends": round(div_income, 2),
            "DCA": round(dca, 2),
            "Withdrawn": round(withdrawal, 2),
            "Taxes Owed": round(tax_owed, 2),
            "Taxes Paid": round(tax_paid, 2),
            "Tax Balance": round(tax_balance, 2),
            "Fed Penalty": round(fed_penalty, 2),
            "State Penalty": round(state_penalty, 2),
            "Reinvested": round(net_cash, 2),
            "New Shares": round(new_shares, 4),
            "Cumulative Shares Added": round(cumulative_shares_added, 4),
            "Total Shares": round(shares, 4),
            "Portfolio Value": round(shares * current_price, 2),
            "Profit/Loss on New Shares": round(profit_loss, 2)
        })

    df = pd.DataFrame(data)
    st.dataframe(df)
    st.success(f"Final Portfolio Value: ${shares * current_price:,.2f}")
    st.success(f"Total Shares: {shares:,.4f}")
    st.success(f"Initial Investment: ${initial_shares * initial_cost_basis:,.2f}")