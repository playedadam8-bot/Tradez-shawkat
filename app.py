import streamlit as st
import json
import requests
from datetime import datetime

# 1. Page Setup
st.set_page_config(page_title="Trader Shawkatz - Live Market Signal Generator", layout="wide")
st.title("📈 Trader Shawkatz - Live Market Signal Generator (Non-OTC)")

# 🔐 Security Check: Password Protection
def check_password():
    def password_entered():
        if st.session_state["password"] == "Shawkatdeveloper":
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 Enter Password to Access App:", type="password", on_change=password_entered, key="password")
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

# 3. Exact Live Market Pairs (Non-OTC filtered from your provided list)
LIVE_PAIRS = [
    "EUR/JPY", "CAD/JPY", "EUR/GBP", "AUD/JPY", "USD/JPY", 
    "AUD/USD", "AUD/CAD", "EUR/USD", "EUR/CAD", "AUD/CHF", 
    "GBP/AUD", "GBP/USD", "EUR/AUD", "CHF/JPY", "GBP/CAD", 
    "GBP/CHF", "GBP/JPY", "USD/CHF", "EUR/CHF"
]

# 4. Custom Timeframe Options (1 min to 15 min sequential as requested)
TIMEFRAMES = [
    "1min", "2min", "3min", "4min", "5min", 
    "6min", "7min", "8min", "9min", "10min", 
    "11min", "12min", "13min", "14min", "15min"
]

# 5. Sidebar Controls with Fully Interactive Selectboxes
st.sidebar.header("⚙️ Live Market Control Panel")
selected_pair = st.sidebar.selectbox("Select Live Currency Pair", LIVE_PAIRS, key="pair_select")
selected_timeframe = st.sidebar.selectbox("Select Expiry Timeframe", TIMEFRAMES, key="time_select")

# 6. Main UI
st.subheader(f"Selected Asset: **{selected_pair}** | Expiry Timeframe: **{selected_timeframe}**")
st.info("Click the button below to generate a real-time signal via OpenRouter AI for your selected live asset and timeframe without needing screenshots.")

if st.button("🚀 Generate Live Signal"):
    with st.spinner(f"Analyzing live market data for {selected_pair} ({selected_timeframe})..."):
        try:
            current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            
            prompt = f"""
            You are an expert algorithmic binary options trader specializing in live currency markets.
            Asset: {selected_pair}
            Timeframe: {selected_timeframe}
            Current UTC Time: {current_time}

            Tasks:
            1. Analyze the expected short-term market momentum, trend behavior, and typical technical conditions for {selected_pair} at the {selected_timeframe} timeframe.
            2. Provide a directional signal ("CALL" or "PUT").
            3. Output ONLY a valid JSON object with no markdown ticks, structured exactly like this:
            {{
              "asset": "{selected_pair}",
              "timeframe": "{selected_timeframe}",
              "analysis_time": "{current_time} UTC",
              "signal": "CALL" or "PUT",
              "reason": "Detailed technical explanation based on live market price action and momentum."
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
                    "max_tokens": 350,
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
                    
                    st.markdown("### 🎯 Trader Shawkatz — Live Signal Output")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(label="Asset Pair", value=data.get("asset", selected_pair))
                    with col2:
                        st.metric(label="Timeframe", value=data.get("timeframe", selected_timeframe))
                    with col3:
                        st.metric(label="Timestamp", value=data.get("analysis_time", current_time))
                    
                    signal = data.get("signal", "NEUTRAL").upper()
                    if signal == "CALL":
                        st.success(f"**SIGNAL: CALL (UP) — Expiry: {selected_timeframe}**")
                    elif signal == "PUT":
                        st.error(f"**SIGNAL: PUT (DOWN) — Expiry: {selected_timeframe}**")
                    else:
                        st.warning(f"**SIGNAL: {signal}**")
                        
                    st.info(f"**Technical Reasoning:** {data.get('reason', 'No reason provided.')}")
                else:
                    st.error(f"Unexpected API response format: {result}")
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")

        except Exception as e:
            st.error(f"Signal generation failed: {e}")
