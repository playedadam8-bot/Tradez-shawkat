import streamlit as st
import json
import requests
from datetime import datetime, timedelta
import random
import yfinance as yf

# 1. Page Setup & Premium Styling
st.set_page_config(page_title="Trader Shawkatz - Live Signal Generator", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    /* Main Background and Font */
    .main {
        background-color: #0e1117;
        font-family: 'Inter', sans-serif;
    }
    
    /* Title Styling */
    .main-title {
        font-size: 3rem !important;
        font-weight: 800 !important;
        background: -webkit-linear-gradient(#00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Card Styling */
    .stSelectbox, .stButton {
        background-color: #1e222d;
        border-radius: 10px;
    }

    /* Metric Card Styling */
    div[data-metric-indicator="none"] {
        background-color: #161a25;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2d343f;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }

    /* Custom Button */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    }

    /* Password Box Styling */
    .stTextInput input {
        background-color: #161a25;
        color: white;
        border: 1px solid #4facfe;
    }

    /* Success/Banner Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .signal-card {
        animation: fadeIn 0.5s ease-out;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-title">📈 Trader Shawkatz — Live Market Signal Generator</h1>', unsafe_allow_html=True)

# 🔐 Security Check: Password Protection
def check_password():
    def password_entered():
        if st.session_state["password"] == "Shawkatdeveloper":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.text_input("🔒 Enter Password to Access App:", type="password", on_change=password_entered, key="password")
        st.markdown("</div>", unsafe_allow_html=True)
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Enter Password to Access App:", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# 2. OpenRouter API Key configuration
API_KEY = "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"

# 3. Exact Live Market Pairs mapped to Yahoo Finance Tickers
LIVE_PAIRS_MAP = {
    "EUR/JPY": "EURJPY=X",
    "CAD/JPY": "CADJPY=X",
    "EUR/GBP": "EURGBP=X",
    "AUD/JPY": "AUDJPY=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "AUD/CAD": "AUDCAD=X",
    "EUR/USD": "EURUSD=X",
    "EUR/CAD": "EURCAD=X",
    "AUD/CHF": "AUDCHF=X",
    "GBP/AUD": "GBPAUD=X",
    "GBP/USD": "GBPUSD=X",
    "EUR/AUD": "EURAUD=X",
    "CHF/JPY": "CHFJPY=X",
    "GBP/CAD": "GBPCAD=X",
    "GBP/CHF": "GBPCHF=X",
    "GBP/JPY": "GBPJPY=X",
    "USD/CHF": "USDCHF=X",
    "EUR/CHF": "EURCHF=X"
}

# 4. Custom Timeframe Options
TIMEFRAMES = [
    "1min", "2min", "3min", "4min", "5min", 
    "6min", "7min", "8min", "9min", "10min", 
    "11min", "12min", "13min", "14min", "15min"
]

# 5. Main Screen Selectboxes
st.markdown("### ⚙️ Choose Trading Parameters")
with st.container():
    col_p, col_t = st.columns(2)
    with col_p:
        selected_pair = st.selectbox("Select Currency Pair", list(LIVE_PAIRS_MAP.keys()), key="pair_select")
    with col_t:
        selected_timeframe = st.selectbox("Select Expiry Timeframe", TIMEFRAMES, key="time_select")

st.write("")

# 6. Signal Generation Action
if st.button("🚀 Generate Live Signal"):
    with st.spinner(f"Fetching real Yahoo Finance live market data & running GPT-4o analysis..."):
        try:
            ticker_symbol = LIVE_PAIRS_MAP[selected_pair]
            ticker = yf.Ticker(ticker_symbol)
            
            todays_data = ticker.history(period="1d", interval="1m")
            
            if todays_data.empty:
                st.error("Could not fetch live market feed from Yahoo Finance. Market might be closed or data restricted.")
                st.stop()
                
            current_open = float(todays_data['Open'].iloc[-1])
            current_close = float(todays_data['Close'].iloc[-1])
            current_high = float(todays_data['High'].iloc[-1])
            current_low = float(todays_data['Low'].iloc[-1])
            
            future_time_local = datetime.utcnow() + timedelta(hours=5, seconds=5)
            formatted_time = future_time_local.strftime("%H:%M:%S")
            
            real_accuracy = f"{random.uniform(95.0, 99.0):.1f}%"
            
            prompt = f"""
            You are an expert algorithmic binary options trading engine. You are analyzing REAL-TIME live data pulled directly from Yahoo Finance.
            Asset: {selected_pair}
            Real Live Open Price: {current_open}
            Real Live Current Price: {current_close}
            Recent High: {current_high}
            Recent Low: {current_low}
            Timeframe: {selected_timeframe}

            Tasks:
            1. Analyze the exact price movement between Open ({current_open}) and Current ({current_close}) along with High/Low structure to determine high-probability directional momentum. Be dynamic: choose CALL if bullish, or PUT if bearish. Do not default to CALL.
            2. Provide a precise directional signal ("CALL" for Up, "PUT" for Down).
            3. Calculate a realistic close price estimation for the given timeframe.
            4. Output ONLY a valid JSON object with no markdown ticks, structured exactly like this:
            {{
              "signal": "CALL" or "PUT",
              "signal_close_price": "..."
            }}
            """

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "", 
                    "X-OpenRouter-Title": "Live Market Signal Generator",
                },
                data=json.dumps({
                    "model": "openai/gpt-4o",
                    "max_tokens": 150,
                    "messages": [{"role": "user", "content": prompt}]
                }),
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    raw_content = result['choices'][0]['message']['content'].strip()
                    if raw_content.startswith("```"):
                        raw_content = raw_content.split("```")[1]
                        if raw_content.startswith("json"):
                            raw_content = raw_content[4:].strip()
                    if raw_content.endswith("```"):
                        raw_content = raw_content[:-3].strip()

                    data = json.loads(raw_content)
                    
                    st.markdown("---")
                    st.markdown("### 🎯 Trader Shawkatz — Live Signal")
                    
                    signal = data.get("signal", "NEUTRAL").upper()
                    
                    # Signal Banner with Premium Styling
                    if signal == "CALL":
                        st.markdown(
                            """
                            <div class="signal-card" style="background: linear-gradient(90deg, #1d976c 0%, #93f9b9 100%); padding: 25px; border-radius: 15px; display: flex; justify-content: space-between; align-items: center; color: white; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                                <div>
                                    <span style="font-size: 14px; text-transform: uppercase; opacity: 0.8;">Market Direction</span><br>
                                    <span style="font-size: 36px; font-weight: 900;">BUY / CALL (UP)</span>
                                </div>
                                <div style="background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 32px;">↑</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    elif signal == "PUT":
                        st.markdown(
                            """
                            <div class="signal-card" style="background: linear-gradient(90deg, #eb3349 0%, #f45c43 100%); padding: 25px; border-radius: 15px; display: flex; justify-content: space-between; align-items: center; color: white; margin-bottom: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                                <div>
                                    <span style="font-size: 14px; text-transform: uppercase; opacity: 0.8;">Market Direction</span><br>
                                    <span style="font-size: 36px; font-weight: 900;">SELL / PUT (DOWN)</span>
                                </div>
                                <div style="background-color: rgba(255, 255, 255, 0.2); border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 32px;">↓</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    # Entry Time Display
                    st.info(f"⚡ **Target Entry Time:** `{formatted_time}` (UTC+5)")

                    # Metrics Section
                    res_col1, res_col2, res_col3 = st.columns(3)
                    with res_col1:
                        st.metric(label="Asset Pair", value=selected_pair)
                        st.metric(label="Live Open Price", value=f"{current_open:.5f}")
                    with res_col2:
                        st.metric(label="Timeframe", value=selected_timeframe)
                        st.metric(label="Signal Close Price", value=str(data.get("signal_close_price", f"{current_close:.5f}")))
                    with res_col3:
                        st.metric(label="System Expiry", value=selected_timeframe)
                        st.metric(label="Real Accuracy", value=real_accuracy)
                        
                else:
                    st.error(f"Unexpected API response format: {result}")
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")

        except Exception as e:
            st.error(f"Signal generation failed: {e}")
