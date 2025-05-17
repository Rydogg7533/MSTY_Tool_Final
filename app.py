
from flask import Flask, jsonify

app = Flask(__name__)

def calculate_profit_loss(ending_share_count, market_price_per_share, total_invested):
    return (ending_share_count * market_price_per_share) - total_invested

def generate_cumulative_shares(initial_shares, monthly_new_shares):
    cumulative = [initial_shares]
    for shares in monthly_new_shares:
        cumulative.append(cumulative[-1] + shares)
    return cumulative

@app.route("/")
def index():
    initial_shares = 10000
    monthly_new_shares = [200 for _ in range(12)]
    market_price = 30
    total_invested = 275000

    cumulative_shares = generate_cumulative_shares(initial_shares, monthly_new_shares)
    months = ["Start"] + [f"Month {i}" for i in range(1, 13)]
    new_shares = [initial_shares] + monthly_new_shares

    share_data = [
        {"month": months[i], "new_shares": new_shares[i], "cumulative_shares": cumulative_shares[i]}
        for i in range(len(months))
    ]

    final_shares = cumulative_shares[-1]
    profit = calculate_profit_loss(final_shares, market_price, total_invested)

    return jsonify({
        "share_growth": share_data,
        "ending_shares": final_shares,
        "market_price": market_price,
        "total_invested": total_invested,
        "profit_loss": profit
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
