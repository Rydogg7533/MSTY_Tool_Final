import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="MSTY Hedging Tool", layout="wide")
st.title("🛡️ MSTY Hedging Tool with MSTR Correlation")

st.header("Step 1: Define MSTY Price Range")
msty_top = st.number_input("MSTY Peak Price ($)", min_value=0.0, value=38.0)
msty_bottom = st.number_input("MSTY Target Drop Price ($)", min_value=0.0, value=25.0)

st.header("Step 2: Estimated MSTR Range Based on Correlation")
# Example ratio (normally derived from data)
example_ratio = 30  # e.g., MSTR price is ~30x MSTY price
st.markdown(f"Using a historical MSTR/MSTY ratio of **{example_ratio}:1**")

mstr_top = round(msty_top * example_ratio, 2)
mstr_bottom = round(msty_bottom * example_ratio, 2)

st.success(f"Estimated MSTR Top Price: ${mstr_top}")
st.success(f"Estimated MSTR Bottom (Hedge Target): ${mstr_bottom}")

st.header("Step 3: Live MSTR Put Options for Recommended Strike")

try:
    ticker = yf.Ticker("MSTR")
    expiry = ticker.options[-1]  # Latest expiration
    options_chain = ticker.option_chain(expiry)
    puts = options_chain.puts
    target_puts = puts[puts['strike'] >= mstr_bottom]

    if not target_puts.empty:
        recommended_put = target_puts.iloc[0]
        strike_price = recommended_put['strike']
        premium = recommended_put['lastPrice']
        st.success(f"Recommended Strike: ${strike_price:.2f}  |  Premium: ${premium:.2f}  |  Expiry: {expiry}")
    else:
        st.warning("No available puts found at or below your target.")
        strike_price = mstr_bottom
        premium = st.number_input("Manual Option Premium ($)", value=20.0)
except Exception as e:
    st.error("Could not fetch live MSTR option data. Manual input required.")
    strike_price = mstr_bottom
    premium = st.number_input("Manual Option Premium ($)", value=20.0)

st.header("Step 4: Calculate Hedge Cost")
shares = st.number_input("Total MSTY Shares to Hedge", min_value=0, value=1000)
contracts_needed = (shares + 99) // 100
cost = contracts_needed * premium * 100
cashout = shares * msty_bottom
downside = shares * (msty_top - msty_bottom)

st.write(f"**Contracts Needed:** {contracts_needed}")
st.write(f"**Total Cost of Hedge:** ${cost:,.2f}")
st.write(f"**Downside Protected:** ${downside:,.2f}")
st.write(f"**Cash Out at MSTY ${msty_bottom}:** ${cashout:,.2f}")