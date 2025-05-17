
# Streamlit app with enhanced compounding simulator
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MSTY Tracker", layout="wide")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📈 Compounding Simulator", "📊 Market Monitoring", "💰 Cost Basis Tools", "🛡️ Hedging Tools", "📤 Export Center"])

with tab1:
    st.header("📈 Enhanced Compounding Simulator")
    col1, col2, col3 = st.columns(3)
    with col1:
        initial_shares = st.number_input("Initial Shares Owned", value=10000)
        avg_share_cost = st.number_input("Weighted Average Cost Per Share ($)", value=200.0)
        dca = st.number_input("Monthly Capital Addition ($)", value=0.0)
    with col2:
        monthly_div = st.number_input("Average Monthly Dividend Per Share ($)", value=2.0)
        reinvest_price = st.number_input("Reinvestment Share Price ($)", value=250.0)
        withdrawal = st.number_input("Monthly Withdrawal ($)", value=0.0)
    with col3:
        fed_tax = st.number_input("Federal Tax Rate (%)", value=15.0) / 100
        state_tax = st.number_input("State Tax Rate (%)", value=5.0) / 100
        tax_deferred = st.checkbox("Defer Taxes to October Extension Deadline")
        dependents = st.number_input("Number of Dependents", value=0)

    duration_months = st.slider("Simulation Duration (Months)", 1, 360, 12)
    view_option = st.selectbox("View Results By", ["Monthly", "Yearly", "Total"])
    run_sim = st.button("Run Simulation")

    if run_sim:
        results = []
        shares = initial_shares
        cost_basis = initial_shares * avg_share_cost
        reinvested = 0.0
        total_dca = 0.0
        deferred_taxes = 0.0

        for month in range(1, duration_months + 1):
            dividend_income = shares * monthly_div
            total_dca += dca
            if not tax_deferred:
                taxes = (dividend_income + dca) * (fed_tax + state_tax)
                net_income = dividend_income - taxes - withdrawal
            else:
                net_income = dividend_income - withdrawal
                deferred_taxes += (dividend_income + dca) * (fed_tax + state_tax)

            new_shares = (net_income + dca) / reinvest_price
            reinvested += new_shares
            shares += new_shares

            results.append({
                "Month": month,
                "Shares": round(shares, 2),
                "Dividends": round(dividend_income, 2),
                "New Shares": round(new_shares, 2),
                "Total DCA": round(total_dca, 2),
                "Deferred Taxes": round(deferred_taxes, 2) if tax_deferred else 0.0
            })

        df = pd.DataFrame(results)
        if view_option == "Yearly":
            df = df[df["Month"] % 12 == 0]
        elif view_option == "Total":
            df = pd.DataFrame([{
                "Final Shares": round(shares, 2),
                "Total Dividends": round(df["Dividends"].sum(), 2),
                "Total DCA": round(total_dca, 2),
                "Deferred Taxes Due": round(deferred_taxes, 2) if tax_deferred else 0.0
            }])
        st.dataframe(df)

# Placeholders for other tabs
for tab in [tab2, tab3, tab4, tab5]:
    with tab:
        st.info("This section will be fully developed and integrated next.")
