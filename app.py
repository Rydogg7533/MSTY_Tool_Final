
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="MSTY Stock Monitoring & Simulation Suite", layout="wide")
st.title("📈 MSTY Stock Monitoring & Simulation Suite")

tabs = st.tabs([
    "📊 Compounding Simulator",
    "📉 Market Monitoring",
    "📂 Cost Basis Tools",
    "🛡️ Hedging Tools",
    "📤 Export Center"
])

# --- Compounding Simulator ---
with tabs[0]:
    st.header("📊 Compounding Simulator")
    account_type = st.selectbox("Account Type", ["Taxable", "Non-Taxable", "Deferred"])
    dependents = st.number_input("Dependents", min_value=0, value=0, step=1)
    defer_taxes = st.checkbox("Defer Taxes to Oct 15 Extension")

    fed_tax = state_tax = 0
    if account_type == "Taxable":
        fed_tax = st.number_input("Federal Tax Rate (%)", 0.0, 50.0, 20.0)
        state_tax = st.number_input("State Tax Rate (%)", 0.0, 20.0, 5.0)

    initial_investment = st.number_input("Initial Investment Amount ($)", value=100000.0)
    initial_price = st.number_input("Initial Purchase Cost Basis ($)", value=50.0)
    reinvest_price = st.number_input("Average Reinvestment Cost Per Share ($)", value=55.0)
    dps = st.number_input("Monthly Dividend Per Share ($)", value=0.75)
    months = st.slider("Simulation Duration (Months)", 1, 120, 12)
    current_price = st.number_input("Current Price of MSTY ($)", value=60.0)

    if st.button("Run Simulation"):
        shares = initial_investment / initial_price
        cumulative_taxes_owed = 0
        cumulative_new_shares = 0
        results = []
        tax_due_month = 9 if defer_taxes else 3  # October or April

        for m in range(1, months + 1):
            dividend_income = shares * dps
            tax_owed = dividend_income * ((fed_tax + state_tax) / 100) if account_type == "Taxable" else 0
            cumulative_taxes_owed += tax_owed
            tax_due = cumulative_taxes_owed if (account_type == "Taxable" and m % 12 == tax_due_month) else 0
            if tax_due > 0:
                cumulative_taxes_owed = 0

            reinvestable = dividend_income - (tax_owed if not defer_taxes else 0)
            new_shares = reinvestable / reinvest_price
            shares += new_shares
            cumulative_new_shares += new_shares
            reinvest_cost = new_shares * reinvest_price
            reinvest_value = new_shares * current_price
            reinvest_profit = reinvest_value - reinvest_cost

            results.append([
                m,
                round(dividend_income, 2),
                round(tax_owed, 2),
                round(cumulative_taxes_owed, 2),
                round(tax_due, 2),
                round(new_shares, 4),
                round(cumulative_new_shares, 4),
                round(reinvest_profit, 2),
                round(shares, 2),
                round(shares * current_price, 2)
            ])

        df = pd.DataFrame(results, columns=[
            "Month", "Dividend Income", "Taxes Owed", "Cumulative Taxes Owed",
            "Taxes Due", "New Shares", "Cumulative Shares", "Profit/Loss on Reinvestment",
            "Total Shares", "Portfolio Value"
        ])
        st.dataframe(df, use_container_width=True)
        st.markdown(f"**Initial Investment:** ${initial_investment:,.2f}")
        st.markdown(f"**Total Portfolio Value:** ${shares * current_price:,.2f}")

# --- Market Monitoring ---
with tabs[1]:
    st.header("📉 Market Monitoring")
    mstr = yf.Ticker("MSTR")
    hist = mstr.history(period="3mo")
    hist["IV Simulated"] = (hist["High"] - hist["Low"]) / hist["Close"]
    fig = px.line(hist, y="IV Simulated", title="Simulated Implied Volatility (MSTR)")
    st.plotly_chart(fig)

# --- Cost Basis Tools ---
with tabs[2]:
    st.header("📂 Cost Basis Tools")
    shares = st.number_input("Enter total shares", value=1000)
    prices = st.text_area("Enter cost basis (comma-separated)", "50,55,60")
    try:
        price_list = list(map(float, prices.split(",")))
        avg_basis = sum(price_list) / len(price_list)
        st.success(f"Weighted Average Cost Basis: ${avg_basis:.2f}")
    except:
        st.error("Please enter valid numbers separated by commas.")

# --- Hedging Tools ---
with tabs[3]:
    st.header("🛡️ Hedging Tools")
    shares_to_hedge = st.number_input("Shares to Hedge", value=1000)
    strike_price = st.number_input("Strike Price", value=55.0)
    option_price = st.number_input("Option Cost per Share", value=3.0)
    exit_price = st.number_input("Exit Price", value=40.0)
    contracts = shares_to_hedge // 100
    total_cost = contracts * 100 * option_price
    hedge_value = contracts * 100 * (strike_price - exit_price)
    st.write(f"Contracts Needed: {contracts}")
    st.write(f"Total Hedge Cost: ${total_cost}")
    st.write(f"Payout if Dropped to Exit: ${hedge_value}")

# --- Export Center ---
with tabs[4]:
    st.header("📤 Export Center")
    st.info("PDF and Email features coming soon.")
