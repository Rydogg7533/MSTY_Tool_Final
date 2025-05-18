import streamlit as st
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

state_penalties = {
    "AL": 0.01, "AK": 0.005, "AZ": 0.01, "AR": 0.01, "CA": 0.05, "CO": 0.01, "CT": 0.01, "DE": 0.01, "FL": 0.01, "GA": 0.01,
    "HI": 0.02, "ID": 0.005, "IL": 0.02, "IN": 0.10, "IA": 0.006, "KS": 0.01, "KY": 0.02, "LA": 0.005, "ME": 0.01, "MD": 0.005,
    "MA": 0.01, "MI": 0.005, "MN": 0.005, "MS": 0.01, "MO": 0.05, "MT": 0.012, "NE": 0.05, "NV": 0.0075, "NH": 0.05, "NJ": 0.05,
    "NM": 0.02, "NY": 0.005, "NC": 0.10, "ND": 0.01, "OH": 0.005, "OK": 0.0125, "OR": 0.05, "PA": 0.05, "RI": 0.01, "SC": 0.005,
    "SD": 0.0125, "TN": 0.01, "TX": 0.01, "UT": 0.02, "VT": 0.01, "VA": 0.06, "WA": 0.01, "WV": 0.005, "WI": 0.01, "WY": 0.01
}

st.set_page_config(page_title="MSTY Compounding Simulator", layout="wide")
st.title("📊 MSTY Compounding Simulator")

initial_shares = st.number_input("Initial Share Count", min_value=0, value=1000)
initial_cost_basis = st.number_input("Initial Purchase Cost Basis ($)", min_value=0.0, value=25.00)
avg_div_per_share = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.0)
avg_reinvest_cost = st.number_input("Average Reinvestment Cost Per Share ($)", min_value=0.01, value=25.0)
fed_tax_rate = st.slider("Federal Tax Rate (%)", 0, 50, 20)
selected_state = st.selectbox("Select Your State", list(state_penalties.keys()))
state_tax_rate = st.slider("State Tax Rate (%)", 0, 20, 5)
account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Tax-Deferred"])
defer_taxes = st.checkbox("Defer Taxes to Oct 15 Extension Deadline")
withdrawal = st.number_input("Withdraw this Dollar Amount Monthly ($)", min_value=0.0, value=0.0)
dca = st.number_input("Add Capital Monthly (DCA) ($)", min_value=0.0, value=0.0)
current_price = st.number_input("Current MSTY Price ($)", value=45.0)
months = st.slider("Holding Period (Months)", 1, 360, 60)
view_mode = st.selectbox("How would you like to view the table?", ["Monthly", "Yearly", "Total"])
run_sim = st.button("Run Simulation")

if run_sim:
    shares = initial_shares
    state_penalty_rate = state_penalties[selected_state]
    start_date = datetime.today().replace(day=1)

    rows = []

    for i in range(months):
        date = start_date + relativedelta(months=i)
        year = date.year
        div_income = shares * avg_div_per_share
        gross_cash = div_income + dca

        monthly_tax = 0
        tax_paid = 0
        if account_type == "Taxable" and not defer_taxes:
            monthly_tax = div_income * (fed_tax_rate + state_tax_rate) / 100
            tax_paid = monthly_tax

        reinvest_amount = max(0, gross_cash - withdrawal - tax_paid)
        new_shares = reinvest_amount / avg_reinvest_cost if avg_reinvest_cost else 0
        shares += new_shares
        portfolio_value = shares * current_price

        rows.append({
            "Month": i + 1,
            "Year": year,
            "Date": date.strftime("%Y-%m-%d"),
            "Dividends": round(div_income, 2),
            "Taxes Withdrawn": round(tax_paid, 2),
            "Withdrawn": round(withdrawal, 2),
            "DCA": round(dca, 2),
            "Reinvested": round(reinvest_amount, 2),
            "New Shares": round(new_shares, 4),
            "Total Shares": round(shares, 4),
            "Portfolio Value": round(portfolio_value, 2)
        })

    df = pd.DataFrame(rows)

    if view_mode == "Monthly":
        view_df = df.copy()
    elif view_mode == "Yearly":
        view_df = df.groupby("Year").agg({
            "Dividends": "sum",
            "Taxes Withdrawn": "sum",
            "Withdrawn": "sum",
            "DCA": "sum",
            "Reinvested": "sum",
            "New Shares": "sum",
            "Total Shares": "last",
            "Portfolio Value": "last"
        }).reset_index()
    else:  # Total
        view_df = pd.DataFrame([{
            "Dividends": df["Dividends"].sum(),
            "Taxes Withdrawn": df["Taxes Withdrawn"].sum(),
            "Withdrawn": df["Withdrawn"].sum(),
            "DCA": df["DCA"].sum(),
            "Reinvested": df["Reinvested"].sum(),
            "New Shares": df["New Shares"].sum(),
            "Total Shares": df["Total Shares"].iloc[-1],
            "Portfolio Value": df["Portfolio Value"].iloc[-1]
        }])

    st.subheader("Simulation Results")
    st.dataframe(view_df)
    st.success(f"Total Final Shares: {shares:,.2f}")
    st.success(f"Final Portfolio Value: ${shares * current_price:,.2f}")