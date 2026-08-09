import streamlit as st
import json
import requests
from PIL import Image
import io
import base64

# 1. Page Setup
st.set_page_config(page_title="Trader Shawkatz - Advanced Multi-Asset Signal Generator", layout="wide")

# App Title
st.title("👁️ Trader Shawkatz - Multi-Asset & Multi-Timeframe Signal Generator")

# 🔐 Security Check: Password Protection
def check_password():
    """Returns `True` if the user entered the correct password."""
    def password_entered():
        if st.session_state["password"] == "Shawkatdeveloper":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "🔒 Enter Password to Access App:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔒 Enter Password to Access App:", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# 2. OpenRouter Configuration
API_KEY = "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"

# 3. Asset and Timeframe Options Definition
CURRENCIES = [
    "USD/PKR (OTC)", "USD/COP (OTC)", "NZD/JPY (OTC)", "USD/ARS (OTC)", "USD/INR (OTC)", 
    "USD/DZD (OTC)", "USD/IDR (OTC)", "EUR/NZD (OTC)", "GBP/NZD (OTC)", "USD/BDT (OTC)", 
    "USD/NGN (OTC)", "CAD/CHF (OTC)", "USD/EGP (OTC)", "USD/ZAR (OTC)", "NZD/CAD (OTC)", 
    "NZD/USD (OTC)", "NZD/CHF (OTC)", "USD/MXN (OTC)", "USD/PHP (OTC)", "AUD/NZD (OTC)", 
    "USD/BRL (OTC)", "EUR/JPY (OTC)", "CAD/JPY (OTC)", "EUR/GBP (OTC)", "AUD/JPY (OTC)", 
    "USD/JPY (OTC)", "AUD/USD (OTC)", "AUD/CAD (OTC)", "EUR/USD (OTC)", "EUR/CAD (OTC)", 
    "AUD/CHF (OTC)", "GBP/AUD (OTC)", "GBP/USD (OTC)", "EUR/AUD (OTC)", "CHF/JPY (OTC)", 
    "GBP/CAD (OTC)", "GBP/CHF (OTC)", "GBP/JPY (OTC)", "USD/CHF (OTC)", "EUR/CHF (OTC)"
]

CRYPTO = [
    "Ripple (OTC)", "Cosmos (OTC)", "Bitcoin Cash (OTC)", "Chainlink (OTC)", "Zcash (OTC)", 
    "Litecoin (OTC)", "Bitcoin (OTC)", "Ethereum (OTC)", "Ethereum Classic (OTC)", "Dash (OTC)", 
    "Trump (OTC)", "Toncoin (OTC)", "Solana (OTC)", "Polkadot (OTC)", "Binance Coin (OTC)", 
    "Avalanche (OTC)", "Axie Infinity (OTC)"
]

COMMODITIES = [
    "USCrude (OTC)", "UKBrent (OTC)", "Silver (OTC)", "Gold (OTC)"
]

ALL_ASSETS = CURRENCIES + CRYPTO + COMMODITIES

TIMEFRAMES = [
    "5s", "10s", "15s", "20s", "30s", "45s", 
    "1min", "2min", "3min", "5min", "10min", "15min"
]

# 4. Sidebar Selectors for Custom Pair & Timeframe Override
st.sidebar.header("⚙️ Signal Generator Settings")
selected_category = st.sidebar.selectbox("Select Asset Category", ["All Assets", "Currencies", "Crypto", "Commodities"])

if selected_category == "Currencies":
    category_list = CURRENCIES
elif selected_category == "Crypto":
    category_list = CRYPTO
elif selected_category == "Commodities":
    category_list = COMMODITIES
else:
    category_list = ALL_ASSETS

target_asset = st.sidebar.selectbox("Choose Target Asset", category_list)
target_timeframe = st.sidebar.selectbox("Choose Expiration / Chart Timeframe", TIMEFRAMES, index=6) # Default 1min

# 5. Main UI Layout
uploaded_file = st.file_uploader("Upload Quotex Chart Screenshot", type=["jpg", "png", "jpeg"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption=f"Chart Preview — Selected Pair: {target_asset} [{target_timeframe}]", use_container_width=True)

    if st.button("🚀 Analyze & Generate Precision Signal"):
        with st.spinner("AI is analyzing indicators across selected timeframe & asset..."):
            try:
                buffered = io.BytesIO()
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffered, format="JPEG")
                base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

                prompt = f"""
                You are an expert algorithmic binary options trader analyzing a trading chart screenshot.
                Target Asset Selected by Trader: {target_asset}
                Target Expiry / Candle Timeframe: {target_timeframe}
                
                Tasks:
                1. Read the current clock timestamp visible on the screenshot interface.
                2. Verify or extract the live asset price.
                3. Analyze candlesticks, momentum, and visible technical indicators (such as Bollinger Bands, Moving Averages, RSI).
                4. Tailor your prediction specifically for a {target_timeframe} expiration setup on {target_asset}.
                5. Provide a precise execution safety entry target (e.g. 2 seconds before candle completion if trading standard minute intervals, or optimized entry for short-term bursts).
                6. Output ONLY a valid JSON object with no markdown ticks, structured exactly like this:
                {{
                  "asset": "{target_asset}",
                  "timeframe": "{target_timeframe}",
                  "live_price": "...",
                  "chart_time": "...",
                  "entry_target": "Exact entry timestamp or countdown rule",
                  "signal": "CALL" or "PUT",
                  "reason": "Detailed technical explanation based on indicators and trend structure."
                }}
                """

                response = requests.post(
                  url="https://openrouter.ai/api/v1/chat/completions",
                  headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "", 
                    "X-OpenRouter-Title": "Chart Analyzer", 
                  },
                  data=json.dumps({
                    "model": "openai/gpt-4o",
                    "max_tokens": 450,
                    "messages": [
                      {
                        "role": "user",
                        "content": [
                          {
                            "type": "text",
                            "text": prompt
                          },
                          {
                            "type": "image_url",
                            "image_url": {
                              "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                          }
                        ]
                      }
                    ]
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
                        
                        st.markdown("### 🎯 Trader Shawkatz — Precision Signal Setup")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric(label="Asset Pair", value=data.get("asset", target_asset))
                            st.metric(label="Live Price", value=data.get("live_price", "N/A"))
                        with col2:
                            st.metric(label="Timeframe", value=data.get("timeframe", target_timeframe))
                            st.metric(label="Chart Timestamp", value=data.get("chart_time", "N/A"))
                        with col3:
                            st.metric(label="⚡ Target Entry", value=data.get("entry_target", "N/A"))
                        
                        signal = data.get("signal", "NEUTRAL").upper()
                        if signal == "CALL":
                            st.success(f"**SIGNAL: CALL (UP) — Expiry: {target_timeframe}**")
                        elif signal == "PUT":
                            st.error(f"**SIGNAL: PUT (DOWN) — Expiry: {target_timeframe}**")
                        else:
                            st.warning(f"**SIGNAL: {signal}**")
                            
                        st.info(f"**Technical Reasoning:** {data.get('reason', 'No reason provided.')}")
                        
                    else:
                        st.error(f"Unexpected API Response: {result}")
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")

            except Exception as e:
                st.error(f"Analysis failed: {e}")
