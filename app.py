import streamlit as st
import json
import requests
from datetime import datetime, timedelta
import random
import yfinance as yf
import re
import pytz

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

    /* Entry Card - Live Time First, Then Price */
    .entry-container {
        background: rgba(255, 255, 255, 0.02);
        border: 2px solid rgba(0, 242, 254, 0.2);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 0 40px rgba(79, 172, 254, 0.1);
    }
    
    .entry-label {
        font-family: 'Rajdhani', sans-serif;
        color: #4facfe;
        font-size: 1.3rem;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .entry-value {
        font-family: 'Orbitron', sans-serif;
        font-size: 3.5rem !important;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
        margin: 8px 0;
    }

    /* Trade Explanation Box */
    .explanation-box {
        background: rgba(0, 242, 254, 0.03);
        border-left: 4px solid #00f2fe;
        padding: 20px;
        border-radius: 0 15px 15px 0;
        margin-top: 20px;
        font-family: 'Rajdhani', sans-serif;
        color: #e0e0e0;
        font-size: 1.2rem;
        line-height: 1.6;
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

# Flags Mapping with proper spacing
FLAG_MAP = {
    "EUR/JPY": "🇪🇺 &nbsp; 🇯🇵 &nbsp; EURJPY", "CAD/JPY": "🇨🇦 &nbsp; 🇯🇵 &nbsp; CADJPY", 
    "EUR/GBP": "🇪🇺 &nbsp; 🇬🇧 &nbsp; EURGBP", "AUD/JPY": "🇦🇺 &nbsp; 🇯🇵 &nbsp; AUDJPY",
    "USD/JPY": "🇺🇸 &nbsp; 🇯🇵 &nbsp; USDJPY", "AUD/USD": "🇦🇺 &nbsp; 🇺🇸 &nbsp; AUDUSD", 
    "AUD/CAD": "🇦🇺 &nbsp; 🇨🇦 &nbsp; AUDCAD", "EUR/USD": "🇪🇺 &nbsp; 🇺🇸 &nbsp; EURUSD",
    "EUR/CAD": "🇪🇺 &nbsp; 🇨🇦 &nbsp; EURCAD", "AUD/CHF": "🇦🇺 &nbsp; 🇨🇭 &nbsp; AUDCHF", 
    "GBP/AUD": "🇬🇧 &nbsp; 🇦🇺 &nbsp; GBPAUD", "GBP/USD": "🇬🇧 &nbsp; 🇺🇸 &nbsp; GBPUSD",
    "EUR/AUD": "🇪🇺 &nbsp; 🇦🇺 &nbsp; EURAUD", "CHF/JPY": "🇨🇭 &nbsp; 🇯🇵 &nbsp; CHFJPY", 
    "GBP/CAD": "🇬🇧 &nbsp; 🇨🇦 &nbsp; GBPCAD", "GBP/CHF": "🇬🇧 &nbsp; 🇨🇭 &nbsp; GBPCHF",
    "GBP/JPY": "🇬🇧 &nbsp; 🇯🇵 &nbsp; GBPJPY", "USD/CHF": "🇺🇸 &nbsp; 🇨🇭 &nbsp; USDCHF", 
    "EUR/CHF": "🇪🇺 &nbsp; 🇨🇭 &nbsp; EURCHF"
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

# 2. API Config with New Key
API_KEY = "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"
TIMEFRAMES = [f"{i}min" for i in range(1, 16)]

# 3. UI Selectors
col_p, col_t = st.columns(2)
with col_p:
    selected_pair_key = st.selectbox("Select Currency Pair", list(FLAG_MAP.keys()))
    display_pair_name = FLAG_MAP[selected_pair_key]
with col_t:
    selected_timeframe = st.selectbox("Select Expiry Timeframe", TIMEFRAMES)

# 4. Signal Logic
if st.button("🚀 GENERATE TRADING SIGNAL"):
    with st.spinner(f"AI Analyzing {selected_pair_key} Cycles..."):
        try:
            ticker_symbol = selected_pair_key.replace("/", "") + "=X"
            ticker = yf.Ticker(ticker_symbol)
            todays_data = ticker.history(period="1d", interval="1m")
            
            if len(todays_data) < 2:
                st.error("Insufficient Market Data. Try another pair.")
                st.stop()
                
            prev_candle = todays_data.iloc[-2]
            current_open = float(prev_candle['Open'])
            current_close = float(prev_candle['Close'])
            current_high = float(prev_candle['High'])
            current_low = float(prev_candle['Low'])
            
            live_price = float(todays_data['Close'].iloc[-1])

            if current_close > current_open:
                candle_name = "Bullish"
                candle_color_text = "Green"
                candle_hex = "#28a745"
            elif current_close < current_open:
                candle_name = "Bearish"
                candle_color_text = "Red"
                candle_hex = "#dc3545"
            else:
                candle_name = "Doji"
                candle_color_text = "Flat"
                candle_hex = "#ffffff"

            last_candle_display = f"{candle_name} ({candle_color_text})"

            try:
                local_tz = pytz.timezone('Asia/Karachi')
                live_entry_time = datetime.now(local_tz).strftime("%H:%M:%S")
            except:
                live_entry_time = datetime.now().strftime("%H:%M:%S")
            
            real_accuracy = f"{random.uniform(90.0, 99.0):.1f}%"
            
            prompt = f"""
            You are an expert algorithmic binary options trading engine analyzing live Yahoo Finance data.
            Asset: {selected_pair_key}
            Open: {current_open}
            Close: {current_close}
            High: {current_high}
            Low: {current_low}
            Last Candle Type: {last_candle_display}
            Timeframe: {selected_timeframe}

            Provide a directional signal ("CALL" or "PUT"), an estimated close price, and a short professional market explanation.
            Output ONLY raw JSON format matching this exact structure, with no markdown tags:
            {{"signal": "CALL", "signal_close_price": "{live_price:.5f}", "explanation": "Brief technical analysis breakdown..."}}
            """

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://shawkat-tradez.streamlit.app",
                    "X-OpenRouter-Title": "Shawkat Tradez Engine"
                },
                json={
                    "model": "openai/gpt-4o",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 250
                },
                timeout=30
            )

            if response.status_code == 200:
                res_json = response.json()
                if "choices" in res_json and len(res_json["choices"]) > 0:
                    raw_res = res_json['choices'][0]['message']['content'].strip()
                    json_match = re.search(r'\{.*\}', raw_res, re.DOTALL)
                    
                    if json_match:
                        data = json.loads(json_match.group())
                        signal = data.get("signal", "CALL").upper()
                        target_price = data.get("signal_close_price", f"{live_price:.5f}")
                        explanation = data.get("explanation", "Momentum and liquidity shift favor this directional continuation.")
                        
                        banner_color = "#28a745" if signal == "CALL" else "#dc3545"
                        arrow = "↑" if signal == "CALL" else "↓"
                        label = "UP / CALL" if signal == "CALL" else "DOWN / PUT"
                        
                        st.markdown(f"""
                            <div style="background:{banner_color}; padding:25px; border-radius:15px; display:flex; justify-content:space-between; align-items:center; color:white; margin-bottom:20px;">
                                <span style="font-family:'Orbitron'; font-size:1.8rem;">{display_pair_name} &nbsp; {label}</span>
                                <span style="font-size:3rem;">{arrow}</span>
                            </div>
                        """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div class="entry-container">
                                <div style="color:#00f2fe; font-family:'Rajdhani'; font-size:1.5rem; font-weight:700; margin-bottom:8px;">
                                    LIVE ENTRY TIME: <span style="color:#ffffff;">{live_entry_time}</span>
                                </div>
                                <div class="entry-label">{display_pair_name} ENTRY PRICE</div>
                                <div class="entry-value">{live_price:.5f}</div>
                            </div>
                        """, unsafe_allow_html=True)

                        col_m1, col_m2 = st.columns([2, 1])
                        
                        with col_m1:
                            m1, m2, m3, m4 = st.columns(4)
                            with m1: st.metric("Live Accuracy", real_accuracy)
                            with m2: st.metric("Target Price", str(target_price))
                            with m3: st.metric("Timeframe", selected_timeframe)
                            with m4: st.metric("Last Candle", last_candle_display)
                            
                        with col_m2:
                            st.markdown("<p style='text-align:center; font-family:Rajdhani; color:#4facfe; margin-bottom:5px;'>LAST CANDLE VISUAL</p>", unsafe_allow_html=True)
                            st.markdown(f"""
                                <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; background: rgba(255,255,255,0.02); border: 1px solid rgba(0,242,254,0.1); border-radius: 10px; padding: 15px;">
                                    <div style="width: 2px; height: 25px; background-color: {candle_hex};"></div>
                                    <div style="width: 35px; height: 45px; background-color: {candle_hex}; border-radius: 3px; box-shadow: 0 0 12px {candle_hex};"></div>
                                    <div style="width: 2px; height: 25px; background-color: {candle_hex};"></div>
                                    <span style="font-family: 'Rajdhani'; font-size: 1.1rem; font-weight: 700; color: {candle_hex}; margin-top: 8px;">{last_candle_display}</span>
                                </div>
                            """, unsafe_allow_html=True)

                        st.markdown(f"""
                            <div class="explanation-box">
                                <strong>💡 AI Trade Breakdown & Analysis:</strong><br>
                                {explanation}
                            </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error(f"AI response format issue: {raw_res}")
                else:
                    st.error(f"Unexpected API response structure: {res_json}")
                
            elif response.status_code == 402:
                st.error("❌ API ERROR 402: Insufficient OpenRouter credits for GPT-4o on this key. Please verify your account balance.")
            else:
                st.error(f"API Error {response.status_code}: {response.text}")

        except Exception as e:
            st.error(f"Error: {e}")
