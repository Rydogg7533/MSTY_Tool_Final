import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="MSTY Compounding Simulator", layout="wide")
st.title("📈 MSTY Compounding Simulator")

# Input parameters
col1, col2, col3 = st.columns(3)
with col1:
    total_shares = st.number_input("Total Share Count", min_value=1, value=10000)
with col2:
    avg_monthly_dividend = st.number_input("Average Monthly Dividend per Share ($)", min_value=0.0, value=2.00, step=0.01)
with col3:
    months = st.slider("Projection Duration (Months)", 1, 120, 36)

col4, col5, col6 = st.columns(3)
with col4:
    annual_tax_rate = st.number_input("Federal + State Tax Rate (%)", min_value=0.0, max_value=50.0, value=30.0, step=0.5)
with col5:
    dependents = st.number_input("Number of Dependents", min_value=0, max_value=20, value=0)
with col6:
    defer_taxes = st.checkbox("Defer Taxes Until Extension Deadline (October)")

# Adjust tax rate based on dependents
tax_credit_per_dependent = 500
effective_tax_rate = max(0.0, annual_tax_rate - (dependents * tax_credit_per_dependent / (total_shares * avg_monthly_dividend * 12)) * 100)

# Run simulation
projection_data = []
projection_deferred = []
shares = shares_def = total_shares
monthly_tax_rate = effective_tax_rate / 100 / 12
deferred_taxes = 0

for month in range(1, months + 1):
    monthly_dividends = avg_monthly_dividend * shares
    monthly_dividends_def = avg_monthly_dividend * shares_def

    if defer_taxes and month <= 9:
        reinvested = monthly_dividends
        reinvested_def = monthly_dividends_def
        deferred_taxes += monthly_dividends * monthly_tax_rate
        tax_paid = 0
    else:
        reinvested = monthly_dividends * (1 - monthly_tax_rate)
        reinvested_def = monthly_dividends_def * (1 - monthly_tax_rate)
        tax_paid = monthly_dividends * monthly_tax_rate

    reinvested_shares = reinvested / avg_monthly_dividend
    reinvested_shares_def = reinvested_def / avg_monthly_dividend

    shares += reinvested_shares
    shares_def += reinvested_shares_def

    projection_data.append({
        "Month": month,
        "Shares": round(shares),
        "Dividends": round(monthly_dividends, 2),
        "Reinvested": round(reinvested, 2),
        "Taxes Paid": round(tax_paid, 2),
        "Shares if Deferred": round(shares_def),
        "Deferred Taxes": round(deferred_taxes if month == 10 else 0, 2)
    })

df = pd.DataFrame(projection_data)
st.dataframe(df)

fig, ax = plt.subplots()
df.plot(x="Month", y=["Shares", "Shares if Deferred"], ax=ax)
plt.title("Projected Share Growth")
st.pyplot(fig)