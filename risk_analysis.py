def risk_analysis(data):
    data["Sharpe Ratio"] = (data["Growth (%)"] - 2) / data["Volatility (%)"]
    data["Value at Risk (VaR)"] = data["Volatility (%)"] * 1.65
    return data
