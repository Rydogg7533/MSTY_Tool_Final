
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Tracker", layout="wide")

# Tab navigation
tabs = st.tabs(["Compounding Simulator", "Cost Basis Tracker", "Market Monitoring", "Options & Hedging", "Export Center"])

# TAB 1: COMPOUNDING SIMULATOR
with tabs[0]:
    st.header("MSTY Compounding Simulator")
    initial_shares = st.number_input("Initial Share Count", value=10000)
    avg_reinvestment_price = st.number_input("Avg Reinvestment Cost Per Share ($)", value=25.0)
    monthly_dividend = st.number_input("Monthly Dividend ($)", value=2.00)
    reinvest_dividends = st.checkbox("Reinvest Dividends?", value=True)
    monthly_withdrawal = st.number_input("Monthly Cash Withdrawal", value=0.0)
    months = st.slider("Simulation Length (Months)", 1, 120, 36)

    shares = [initial_shares]
    for month in range(1, months + 1):
        dividend_income = shares[-1] * monthly_dividend
        reinvest_amount = max(dividend_income - monthly_withdrawal, 0) if reinvest_dividends else 0
        new_shares = reinvest_amount / avg_reinvestment_price
        shares.append(shares[-1] + new_shares)

    df = pd.DataFrame({
        "Month": list(range(months + 1)),
        "Share Count": shares
    })
    st.line_chart(df.set_index("Month"))

# TAB 2: COST BASIS TRACKER
with tabs[1]:
    st.header("Cost Basis Tracker")
    st.markdown("Enter purchase records manually to track cost basis.")
    st.data_editor(pd.DataFrame({
        "Date": [""],
        "Shares": [0],
        "Price": [0.0]
    }), num_rows="dynamic", use_container_width=True)

# TAB 3: MARKET MONITORING
with tabs[2]:
    st.header("Live MSTY + MSTR Monitoring (Placeholder)")
    st.markdown("Real-time data integrations will appear here (prices, yield, macro factors).")

# TAB 4: OPTIONS & HEDGING TOOLS
with tabs[3]:
    st.header("Options & Hedging")
    st.markdown("Estimate contracts needed, simulate covered calls vs. protective puts, etc.")
    st.text_input("Number of MSTY Shares")
    st.text_input("MSTR Option Volume or Target Coverage %")

# TAB 5: EXPORT CENTER
with tabs[4]:
    st.header("Export Your Simulation")
    st.download_button("Download Compounding Table (CSV)", df.to_csv(index=False), file_name="msty_simulator.csv")
