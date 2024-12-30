import streamlit as st
import pandas as pd
import yfinance as yf
import time

# Funktion för att lägga till suffix om nödvändigt
def apply_market_suffix(tickers, default_suffix=".ST"):
    processed_tickers = []
    for ticker in tickers:
        if "." not in ticker:  # Om det inte redan finns ett suffix, anta amerikansk aktie
            processed_tickers.append(ticker)
        else:  # Om suffix finns, behåll det
            processed_tickers.append(ticker)
    return processed_tickers

# Funktion för att hämta data från Yahoo Finance
def fetch_from_yahoo(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist_data = stock.history(period="1y")
        info = stock.info

        if hist_data.empty:
            st.warning(f"Yahoo Finance returnerade ingen data för {ticker}.")
            return None, None

        return hist_data, info
    except Exception as e:
        st.error(f"Fel vid hämtning från Yahoo Finance för {ticker}: {e}")
        return None, None

# Funktion för att hämta och analysera data
def fetch_stock_data(tickers):
    results = []
    for ticker in tickers:
        try:
            time.sleep(1)  # Fördröjning för att undvika rate limiting
            hist_data, info = fetch_from_yahoo(ticker)
            if hist_data is None or info is None:
                continue
            
            # Kontrollera om "Close" finns
            if "Close" in hist_data.columns:
                price_data = hist_data["Close"]
            else:
                st.warning(f"Ingen användbar kolumn hittades för {ticker}. Hoppar över.")
                continue

            # Beräkningar
            returns = price_data.pct_change()
            annual_volatility = returns.std() * (252 ** 0.5) * 100
            growth = ((price_data.iloc[-1] / price_data.iloc[0]) - 1) * 100

            # Hämta nyckeltal
            dividend_yield = info.get("dividendYield", 0) * 100  # Utdelningsandel i %
            pe_ratio = info.get("forwardPE", None)  # P/E-tal

            # Fyll i grundläggande information
            results.append({
                "Ticker": ticker,
                "Growth (%)": growth,
                "Volatility (%)": annual_volatility,
                "Dividend Yield (%)": dividend_yield,
                "P/E Ratio": pe_ratio,
            })
        except Exception as e:
            st.error(f"Fel vid analys för {ticker}: {e}")
    return pd.DataFrame(results)

# Poängsättningsmetod
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

# Funktion för att analysera och ge detaljerade rekommendationer
def analyze_and_recommend(data):
    data = data.dropna()  # Ta bort rader med NaN-värden

    avg_score = data["Total Score"].mean()
    recommendations = []
    for _, row in data.iterrows():
        arguments = []
        if row["Total Score"] > avg_score:
            arguments.append(f"Total poäng ({row['Total Score']:.2f}) är högre än genomsnittet ({avg_score:.2f}).")
        if row["Growth (%)"] > 0:
            arguments.append(f"Hög tillväxt ({row['Growth (%)']:.2f}%).")
        if row["Dividend Yield (%)"] > 0:
            arguments.append(f"Utdelningsandel på {row['Dividend Yield (%)']:.2f}%.")
        if row["P/E Ratio"] and row["P/E Ratio"] < 20:
            arguments.append(f"Lågt P/E-tal ({row['P/E Ratio']:.2f}), vilket indikerar en rimlig värdering.")

        recommendation_text = " ".join(arguments)
        recommendations.append({
            "Ticker": row["Ticker"],
            "Recommendation": "Rekommenderas" if arguments else "Ej rekommenderad",
            "Motivation": recommendation_text if arguments else "Inga starka skäl för investering."
        })

    return pd.DataFrame(recommendations)

# Funktion för att ge förslag på liknande eller bättre aktier
def suggest_similar(data, additional_data):
    combined_data = pd.concat([data, additional_data])
    best_score = combined_data["Total Score"].max()
    suggestions = additional_data[additional_data["Total Score"] >= best_score * 0.7]
    suggestions = suggestions.sort_values(by="Total Score", ascending=False)
    return suggestions

# Streamlit-applikation
st.set_page_config(page_title="Linus Capital Insights", layout="wide")

st.title("💼 Linus Capital Insights")

# Input för aktier
tickers_input = st.text_input("🔎 Ange aktiesymboler (kommaseparerade)", "AAPL, MSFT, KO, VOLV-B.ST, ERIC-B.ST")
tickers = [ticker.strip() for ticker in tickers_input.split(",")]

# Applicera marknadssuffix automatiskt
tickers = apply_market_suffix(tickers)

if st.button("Analysera"):
    data = fetch_stock_data(tickers)
    if not data.empty:
        data = calculate_scores(data)
        st.subheader("Dina Aktier")
        st.dataframe(data)

        st.subheader("📝 Rekommendationer")
        recommendations = analyze_and_recommend(data)
        st.dataframe(recommendations)

        # Förslag på nya aktier
        st.subheader("📈 Förslag på Nya Aktier")
        additional_tickers = ["GOOGL", "META", "NVDA", "JNJ", "PG"]  # Fördefinierad lista
        additional_data = fetch_stock_data(additional_tickers)
        if not additional_data.empty:
            additional_data = calculate_scores(additional_data)
            suggestions = suggest_similar(data, additional_data)
            st.dataframe(suggestions)
        else:
            st.warning("Kunde inte hämta data för fördefinierade aktier.")

        # Visualisering
        st.subheader("📊 Visualisering av Totalpoäng")
        st.bar_chart(data.set_index("Ticker")["Total Score"])
    else:
        st.error("Ingen data tillgänglig för analys.")
