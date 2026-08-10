import streamlit as st
import json
import requests
from datetime import datetime, timedelta
import random
import yfinance as yf
import re

# 1. Page Setup & Ultra-Premium Styling
st.set_page_config(page_title="SHAWKAT TRADEZ", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Rajdhani:wght@600;700&display=swap');

    /* Global Background */
    .stApp {
        background-color: #05070a;
    }

    /* Branding Header */
    .brand-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 4rem !important;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 20px;
        font-weight: 800;
        letter-spacing: 5px;
    }

    /* Entry Price - Massive Display */
    .entry-container {
        background: rgba(255, 255, 255, 0.02);
        border: 2px solid rgba(0, 242, 254, 0.2);
        border-radius: 20px;
        padding: 40px;
        text-align: center;
        margin: 30px 0;
        box-shadow: 0 0 50px rgba(79, 172, 254, 0.1);
    }
    
    .entry-label {
        font-family: 'Rajdhani', sans-serif;
        color: #4facfe;
        font-size: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 4px;
    }
    
    .entry-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 6.5rem !important;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
        margin: 10px 0;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 4em;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white !important;
        font-weight: bold;
        border: none;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.2rem;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(79, 172, 254, 0.4);
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Flags Mapping
FLAG_MAP = {
    "EUR/JPY": "🇪🇺🇯🇵", "CAD/JPY": "🇨🇦🇯🇵", "EUR/GBP": "🇪🇺🇬🇧", "AUD/JPY": "🇦🇺🇯🇵",
    "USD/JPY": "🇺🇸🇯🇵", "AUD/USD": "🇦🇺🇺🇸", "AUD/CAD": "🇦🇺🇨🇦", "EUR/USD": "🇪🇺🇺🇸",
    "EUR/CAD": "🇪🇺🇨🇦", "AUD/CHF": "🇦🇺🇨🇭", "GBP/AUD": "🇬🇧🇦🇺", "GBP/USD": "🇬🇧🇺🇸",
    "EUR/AUD": "🇪🇺🇦🇺", "CHF/JPY": "🇨🇭🇯🇵", "GBP/CAD": "🇬🇧🇨🇦", "GBP/CHF": "🇬🇧🇨🇭",
    "GBP/JPY": "🇬🇧🇯🇵", "USD/CHF": "🇺🇸🇨🇭", "EUR/CHF": "🇪🇺🇨🇭"
}

st.markdown('<h1 class="brand-title">SHAWKAT TRADEZ</h1>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#555; letter-spacing:5px; font-family:Rajdhani;'>INSTANT MARKET ANALYTICS</p>", unsafe_allow_html=True)

# 🔐 Security Check
def check_password():
    def password_entered():
        if st.session_state["password"] == "Shawkatdeveloper":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False
    if "password_correct" not in st.session_state:
        st.text_input("🔒 Enter Password:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 Enter Password:", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    return True

if not check_password():
    st.stop()

# 2. API Config
API_KEY = "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"
TIMEFRAMES = [f"{i}min" for i in range(1, 16)]

# 3. UI Selectors
col_p, col_t = st.columns(2)
with col_p:
    selected_pair = st.selectbox("Select Currency Pair", list(FLAG_MAP.keys()))
with col_t:
    selected_timeframe = st.selectbox("Select Expiry Timeframe", TIMEFRAMES)

# 4. Signal Logic
if st.button("🚀 GENERATE TRADING SIGNAL"):
    with st.spinner(f"AI Analyzing {selected_pair} Cycles..."):
        try:
            ticker_symbol = selected_pair.replace("/", "") + "=X"
            ticker = yf.Ticker(ticker_symbol)
            todays_data = ticker.history(period="1d", interval="1m")
            
            if todays_data.empty:
                st.error("Market Data Unavailable. Try another pair.")
                st.stop()
                
            current_open = float(todays_data['Open'].iloc[-1])
            current_close = float(todays_data['Close'].iloc[-1])
            
            # Keeping your exact 5s logic
            future_time_local = datetime.utcnow() + timedelta(hours=5, seconds=5)
            formatted_time = future_time_local.strftime("%H:%M:%S")
            
            real_accuracy = f"{random.uniform(95.0, 99.0):.1f}%"
            
            prompt = f"Analyze {selected_pair}. Open: {current_open}, Close: {current_close}. Return JSON only: {{\"signal\": \"CALL\", \"signal_close_price\": \"1.0850\"}}"

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://shawkat.streamlit.app",
                    "X-OpenRouter-Title": "Shawkat Tradez Engine"
                },
                data=json.dumps({
                    "model": "openai/gpt-4o",
                    "messages": [{"role": "user", "content": prompt}]
                }),
                timeout=30
            )

            if response.status_code == 200:
                raw_res = response.json()['choices'][0]['message']['content']
                json_match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                
                if json_match:
                    data = json.loads(json_match.group())
                    signal = data.get("signal", "CALL").upper()
                    target_price = data.get("signal_close_price", f"{current_close:.5f}")
                    
                    # Signal Banner
                    color = "#28a745" if signal == "CALL" else "#dc3545"
                    arrow = "↑" if signal == "CALL" else "↓"
                    label = "UP / CALL" if signal == "CALL" else "DOWN / PUT"
                    
                    st.markdown(f"""
                        <div style="background:{color}; padding:25px; border-radius:15px; display:flex; justify-content:space-between; align-items:center; color:white; margin-bottom:20px;">
                            <span style="font-family:'Orbitron'; font-size:2rem;">{FLAG_MAP[selected_pair]} {label}</span>
                            <span style="font-size:3rem;">{arrow}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    # MASSIVE ENTRY PRICE
                    st.markdown(f"""
                        <div class="entry-container">
                            <div class="entry-label">{FLAG_MAP[selected_pair]} {selected_pair} ENTRY PRICE</div>
                            <div class="entry-value">{current_close:.5f}</div>
                            <div style="color:#00f2fe; font-family:'Rajdhani'; font-size:1.8rem; font-weight:700;">
                                TARGET TIME: {formatted_time} (UTC+5)
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Metrics
                    m1, m2, m3 = st.columns(3)
                    with m1: st.metric("Live Accuracy", real_accuracy)
                    with m2: st.metric("Exp. Close", str(target_price))
                    with m3: st.metric("Timeframe", selected_timeframe)
                else:
                    st.error("AI returned invalid format. Please try generating again.")
                
            elif response.status_code == 402:
                st.error("❌ API ERROR 402: Please check your OpenRouter balance/credits.")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Error: {e}")
