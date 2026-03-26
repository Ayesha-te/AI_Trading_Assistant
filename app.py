import streamlit as st
import requests
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage
import openai

# Load API keys
openai.api_key = st.secrets["OPENAI_API_KEY"]
alpha_vantage_api_key = st.secrets["ALPHA_VANTAGE_API_KEY"]

# Streamlit UI config
st.set_page_config(page_title="📈 AI Trading Assistant", layout="centered")
st.title("📊 AI Trading Assistant")
st.markdown("Get **real-time stock prices** and **AI-powered trading insights**.")

# Stock input
stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA)", "AAPL").upper()

if st.button("🔍 Get AI Insight"):
    with st.spinner("Fetching stock data..."):
        try:
            # Fetch stock data from Alpha Vantage
            url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=1min&apikey={alpha_vantage_api_key}"
            response = requests.get(url)
            data = response.json()
            latest_time = list(data["Time Series (1min)"].keys())[0]
            latest_data = data["Time Series (1min)"][latest_time]
            current_price = latest_data["1. open"]

            st.success(f"📉 {stock_symbol} is currently **${current_price}** (as of {latest_time})")

            # LangChain: Set up LLM and prompt
            llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7, openai_api_key=openai.api_key)
            prompt = ChatPromptTemplate.from_template(
                "The current price of {symbol} is ${price}. Provide a concise yet smart trading insight (buy/sell/hold), with reasoning and risk advice."
            )
            final_prompt = prompt.format_messages(symbol=stock_symbol, price=current_price)

            with st.spinner("Generating AI trading insight..."):
                result = llm(final_prompt)
                st.subheader("🤖 AI Trading Insight")
                st.markdown(result.content)

        except Exception as e:
            st.error("Something went wrong fetching data or generating insights.")
            st.exception(e)
