import requests
import streamlit as st
from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


st.set_page_config(page_title="AI Trading Assistant", layout="centered")
st.title("📊 AI Trading Assistant")
st.markdown("Get real-time stock prices and AI-powered trading insights.")

alpha_vantage_api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]
stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)", "AAPL").upper()

if st.button("🔍 Get AI Insight"):
    with st.spinner("Fetching stock data..."):
        try:
            url = (
                "https://www.alphavantage.co/query"
                f"?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=1min&apikey={alpha_vantage_api_key}"
            )
            data = requests.get(url, timeout=30).json()
            latest_time = list(data["Time Series (1min)"].keys())[0]
            latest_data = data["Time Series (1min)"][latest_time]
            current_price = latest_data["1. open"]

            st.success(f"📉 {stock_symbol} is currently **${current_price}** (as of {latest_time})")

            prompt = (
                f"The current price of {stock_symbol} is ${current_price}. "
                "Provide a concise trading insight with a buy, sell, or hold view, "
                "plus reasoning and risk advice. Make it educational, not financial advice."
            )
            result = get_client().chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": "You are a cautious market analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
            )
            st.subheader("🤖 AI Trading Insight")
            st.markdown(result.choices[0].message.content or "")

        except Exception as e:
            st.error("Something went wrong fetching data or generating insights.")
            st.exception(e)
