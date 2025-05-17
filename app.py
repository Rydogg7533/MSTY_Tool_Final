import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import yfinance as yf
from fpdf import FPDF
from io import BytesIO
import base64

st.set_page_config(page_title="MSTY Tracker", layout="wide")
tabs = st.tabs(["📈 Compounding Simulator", "📉 Market Monitoring", "💰 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"])

# Tab 1: Compounding Simulator
with tabs[0]:
    st.header("📈 Enhanced Compounding Simulator")
    with st.form("sim_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            initial_shares = st.number_input("Initial Shares", value=10000)
            reinvest_price = st.number_input("Avg Reinvestment Share Price ($)", value=250.0)
            dca = st.number_input("Monthly Capital Addition ($)", value=0.0)
        with col2:
            avg_div = st.number_input("Avg Monthly Dividend per Share ($)", value=2.0)
            withdrawal = st.number_input("Monthly Withdrawal ($)", value=0.0)
            projection_months = st.slider("Projection Duration (Months)", 12, 240, 60)
        with col3:
            fed_tax = st.number_input("Federal Tax Rate (%)", value=20.0)
            state_tax = st.number_input("State Tax Rate (%)", value=5.0)
            dependents = st.number_input("Dependents", value=0)
            defer_tax = st.checkbox("Defer Taxes to Oct 15 Extension")

        view_option = st.selectbox("View By", ["Monthly", "Yearly", "Total"])
        run_sim = st.form_submit_button("Run Simulation")

    if run_sim:
        shares = initial_shares
        cumulative_shares_added = 0
        deferred_taxes = 0
        cumulative_tax_owed = 0
        rows = []

        for month in range(1, projection_months + 1):
            dividend_income = shares * avg_div
            tax_rate = (fed_tax + state_tax) / 100
            tax_owed = 0 if defer_tax and month % 12 != 10 else dividend_income * tax_rate
            if defer_tax:
                deferred_taxes += dividend_income * tax_rate
            else:
                tax_owed = dividend_income * tax_rate
                deferred_taxes = 0

            reinvestable = dividend_income - tax_owed - withdrawal + dca
            new_shares = reinvestable / reinvest_price
            shares += new_shares
            cumulative_shares_added += new_shares
            cumulative_tax_owed += tax_owed

            rows.append({
                "Month": month,
                "Dividend Income": round(dividend_income, 2),
                "Taxes Owed": round(tax_owed, 2),
                "Cumulative Taxes Owed": round(cumulative_tax_owed, 2),
                "Reinvested Capital": round(reinvestable, 2),
                "New Shares Added": round(new_shares, 4),
                "Cumulative Shares Added": round(cumulative_shares_added, 4),
                "Total Shares": round(shares, 2)
            })

        df = pd.DataFrame(rows)
        if view_option == "Yearly":
            df = df[df["Month"] % 12 == 0]
        elif view_option == "Total":
            df = pd.DataFrame([{
                "Final Shares": round(shares, 2),
                "Total Cumulative Shares Added": round(cumulative_shares_added, 2),
                "Total Dividends Earned": round(df["Dividend Income"].sum(), 2),
                "Total Taxes Owed": round(df["Taxes Owed"].sum(), 2),
                "Total Reinvested": round(df["Reinvested Capital"].sum(), 2)
            }])
        st.dataframe(df)

# Tab 2: Market Monitoring
with tabs[1]:
    st.header("📉 Market Monitoring")
    mstr = yf.Ticker("MSTR")
    hist = mstr.history(period="3mo")
    hist["IV (Simulated)"] = (hist["High"] - hist["Low"]) / hist["Close"]
    fig1 = px.line(hist, y="IV (Simulated)", title="MSTR Implied Volatility (Simulated)")
    st.plotly_chart(fig1)

    sim_data = pd.DataFrame({
        "Date": pd.date_range(end=pd.Timestamp.today(), periods=60),
        "MSTR Option Volume": (pd.Series(range(60)) * 800) + 5000,
        "MSTY Covered Calls": (pd.Series(range(60)) * 1000) + 3000
    })
    fig2 = px.line(sim_data, x="Date", y=["MSTR Option Volume", "MSTY Covered Calls"], title="Market Growth Comparison")
    st.plotly_chart(fig2)

# Tab 3: Cost Basis Tools
with tabs[2]:
    st.header("💰 Cost Basis Tools")
    method = st.radio("Input Method", ["Manual", "Upload CSV"])
    if method == "Manual":
        blocks = st.number_input("Number of Purchase Blocks", 1, 10, 3)
        lots = []
        with st.form("manual_form"):
            for i in range(blocks):
                cols = st.columns(3)
                shares = cols[0].number_input(f"Block {i+1} Shares", min_value=0)
                price = cols[1].number_input(f"Block {i+1} Price", min_value=0.0)
                date = cols[2].date_input(f"Block {i+1} Date")
                lots.append({"Shares": shares, "Price": price, "Date": date})
            submit = st.form_submit_button("Calculate")
        if submit:
            df = pd.DataFrame(lots)
            total_cost = (df["Shares"] * df["Price"]).sum()
            total_shares = df["Shares"].sum()
            avg_cost = total_cost / total_shares if total_shares else 0
            st.success(f"Weighted Average Cost Basis: ${avg_cost:.2f}")
            st.dataframe(df)
    else:
        file = st.file_uploader("Upload CSV with columns Shares, Price, Date")
        if file:
            df = pd.read_csv(file)
            df["Date"] = pd.to_datetime(df["Date"])
            total_cost = (df["Shares"] * df["Price"]).sum()
            total_shares = df["Shares"].sum()
            avg_cost = total_cost / total_shares if total_shares else 0
            st.success(f"Weighted Average Cost Basis: ${avg_cost:.2f}")
            st.dataframe(df)

# Tab 4: Hedging Tools
with tabs[3]:
    st.header("🛡️ Hedging Tools")
    with st.form("hedge_form"):
        shares = st.number_input("Shares to Hedge", value=1000)
        current_price = st.number_input("Current Price", value=25.0)
        strike = st.number_input("Strike Price", value=25.0)
        cost_per = st.number_input("Cost per Option ($)", value=2.5)
        exit_price = st.number_input("Exit Price ($)", value=10.0)
        calc = st.form_submit_button("Calculate")
    if calc:
        contracts = shares // 100
        total_cost = contracts * 100 * cost_per
        payout = contracts * 100 * (strike - exit_price)
        df = pd.DataFrame([{
            "Contracts": contracts,
            "Cost": total_cost,
            "Payout at Exit": payout
        }])
        st.dataframe(df)

# Tab 5: Export Center
with tabs[4]:
    st.header("📤 Export Center")
    if st.button("Generate Sample PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="MSTY Summary Report", ln=True)
        pdf.cell(200, 10, txt="This is a sample generated PDF.", ln=True)
        buffer = BytesIO()
        pdf.output(buffer)
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="msty_report.pdf">Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)