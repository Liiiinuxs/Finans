def calculate_scores(data):
    data["Growth Score"] = data["Growth (%)"] / data["Growth (%)"].max() * 100
    data["Volatility Score"] = (1 - (data["Volatility (%)"] / data["Volatility (%)"].max())) * 100
    data["Dividend Score"] = data["Dividend Yield (%)"] / data["Dividend Yield (%)"].max() * 100
    data["P/E Score"] = (1 - (data["P/E Ratio"] / data["P/E Ratio"].max())) * 100

    data["Total Score"] = (
        data["Growth Score"] * 0.4 +
        data["Volatility Score"] * 0.3 +
        data["Dividend Score"] * 0.2 +
        data["P/E Score"] * 0.1
    )
    return data

def analyze_and_recommend(data):
    avg_score = data["Total Score"].mean()
    recommendations = []
    for _, row in data.iterrows():
        arguments = []
        if row["Total Score"] > avg_score:
            arguments.append(f"Total Score ({row['Total Score']:.2f}) är högre än genomsnittet ({avg_score:.2f}).")
        recommendations.append({
            "Ticker": row["Ticker"],
            "Recommendation": "Rekommenderas" if arguments else "Ej rekommenderad",
            "Motivation": " ".join(arguments) if arguments else "Inga starka skäl."
        })
    return pd.DataFrame(recommendations)
