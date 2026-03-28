import streamlit as st
import yfinance as yf
from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


st.set_page_config(page_title="AI Trading Assistant", layout="centered")
st.title("AI Trading Assistant")
st.markdown("Get real-time stock prices and AI-powered trading insights.")

stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)", "AAPL").upper().strip()

data = yf.download(
    tickers=stock_symbol,
    interval="1m",
    period="1d",
    progress=False,
)

if data.empty:
    st.error("No data found. Try another symbol.")
else:
    st.write(data)
    st.line_chart(data["Close"])

if st.button("Get AI Insight"):
    with st.spinner("Fetching stock data..."):
        try:
            if data.empty:
                st.error("No data found. Try another symbol.")
                st.stop()

            latest_time = data.index[-1]
            current_price = float(data["Close"].iloc[-1])

            st.success(f"{stock_symbol} is currently **${current_price:.2f}** (as of {latest_time})")

            prompt = (
                f"The current price of {stock_symbol} is ${current_price:.2f}. "
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
            st.subheader("AI Trading Insight")
            st.markdown(result.choices[0].message.content or "")

        except Exception as e:
            st.error("Something went wrong fetching data or generating insights.")
            st.exception(e)
