import streamlit as st
import pandas as pd
from chatbot.chatbot import build_chatbot
from config.constants import COLOR_BULL, COLOR_BEAR
from data.cleaner import load_tesla_data_from_csv
from utils.metrics import calculate_metrics
from charts.charts import create_lightweight_chart, create_additional_charts
from ui.style import set_custom_style

# Set up Streamlit page
st.set_page_config(page_title="Tesla Trading Dashboard", page_icon="📈", layout="wide")
set_custom_style()

def main():
    st.markdown('<h1 class="main-header">📊 Tesla Trading Dashboard</h1>', unsafe_allow_html=True)

    menu = st.sidebar.radio("📌 Select Section", ["📈 Dashboard", "🤖 Chatbot"])

    uploaded_file = st.sidebar.file_uploader("Upload Tesla CSV", type=['csv'])
    show_volume = st.sidebar.checkbox("Show Volume", value=True)
    show_signals = st.sidebar.checkbox("Show Trading Signals", value=True)
    show_support_resistance = st.sidebar.checkbox("Show Support/Resistance", value=True)

    if uploaded_file is None:
        st.warning("📂 Please upload a Tesla CSV file to begin analysis")
        return

    df = load_tesla_data_from_csv(uploaded_file)
    if df is None:
        st.error("❌ Failed to load or clean the data.")
        return

    if menu == "📈 Dashboard":
        metrics = calculate_metrics(df)
        create_lightweight_chart(df, show_volume, show_signals, show_support_resistance)
        create_additional_charts(df)

    elif menu == "🤖 Chatbot":
        st.subheader("🤖 Ask Questions About Tesla Stock Data")
        col1, col2 = st.columns([2, 3])

        with col1:
            st.markdown("### Sample Prompts")
            st.write("- How many LONG signal days in 2023?")
            st.write("- What was the average volume in January?")
            st.write("- What is the highest resistance level?")

        with col2:
            question = st.text_input("🔍 Ask a question:", "What is the highest resistance level?")
            if question:
                with st.spinner("Thinking..."):
                    chatbot = build_chatbot(df)
                    response = chatbot.invoke({"query": question})
                    st.success("Answer:")
                    st.write(response["result"])

if __name__ == "__main__":
    main()
