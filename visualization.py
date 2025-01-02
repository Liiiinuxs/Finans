import plotly.express as px

def visualize_risk_reward(data):
    fig = px.scatter(
        data,
        x="Volatility (%)",
        y="Growth (%)",
        size="Total Score",
        color="Dividend Yield (%)",
        hover_name="Ticker",
        title="Risk vs. Reward"
    )
    return fig
