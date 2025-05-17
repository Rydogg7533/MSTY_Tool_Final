import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import yfinance as yf
from fpdf import FPDF
import base64
from io import BytesIO

st.set_page_config(page_title="MSTY Tracker", layout="wide")
st.title("📊 MSTY Tracker App – Fully Functional")

tabs = st.tabs([
    "📈 Compounding Simulator",
    "📉 Market Monitoring",
    "📐 Cost Basis Tools",
    "🛡️ Hedging Tools",
    "📤 Export Center"
])

# Tab 1: Compounding Simulator
with tabs[0]:
    st.header("📈 Compounding Simulator")
    with st.form("sim_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            total_shares = st.number_input("Total Share Count", min_value=1, value=10000)
        with col2:
            avg_monthly_dividend = st.number_input("Monthly Dividend per Share ($)", min_value=0.01, value=2.0)
        with col3:
            months = st.slider("Projection Duration (Months)", 1, 120, 36)

        col4, col5, col6 = st.columns(3)
        with col4:
            tax_rate = st.number_input("Tax Rate (%)", min_value=0.0, max_value=50.0, value=30.0)
        with col5:
            dependents = st.number_input("Number of Dependents", min_value=0, max_value=20, value=0)
        with col6:
            defer_taxes = st.checkbox("Defer Taxes to October Extension")

        run_sim = st.form_submit_button("Run Simulation")

    if run_sim:
        tax_credit = 500
        effective_tax = max(0.0, tax_rate - (dependents * tax_credit / (total_shares * avg_monthly_dividend * 12)) * 100)
        monthly_tax_rate = effective_tax / 100 / 12
        shares, shares_def = total_shares, total_shares
        deferred_taxes = 0
        results = []

        for month in range(1, months + 1):
            div = avg_monthly_dividend * shares
            div_def = avg_monthly_dividend * shares_def

            if defer_taxes and month <= 9:
                reinvest, reinvest_def = div, div_def
                tax_paid = 0
                deferred_taxes += div * monthly_tax_rate
            else:
                reinvest = div * (1 - monthly_tax_rate)
                reinvest_def = div_def * (1 - monthly_tax_rate)
                tax_paid = div * monthly_tax_rate

            shares += reinvest / avg_monthly_dividend
            shares_def += reinvest_def / avg_monthly_dividend

            results.append({
                "Month": month,
                "Shares (Apr Tax)": round(shares),
                "Shares (Oct Tax)": round(shares_def),
                "Dividends": round(div, 2),
                "Tax Paid": round(tax_paid, 2),
                "Deferred Taxes": round(deferred_taxes if month == 10 else 0, 2)
            })

        df = pd.DataFrame(results)
        st.dataframe(df)
        fig, ax = plt.subplots()
        df.plot(x="Month", y=["Shares (Apr Tax)", "Shares (Oct Tax)"], ax=ax)
        st.pyplot(fig)

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

# Tab 3: Cost Basis
with tabs[2]:
    st.header("📐 Cost Basis Tools")
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