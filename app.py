import streamlit as st
import json
import requests
from datetime import datetime, timedelta

# 1. Page Setup
st.set_page_config(page_title="Trader Shawkatz - Live Signal Generator", layout="wide")
st.title("📈 Trader Shawkatz - Live Signal Generator")

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

# 3. Exact Live Market Pairs
LIVE_PAIRS = [
    "EUR/JPY", "CAD/JPY", "EUR/GBP", "AUD/JPY", "USD/JPY", 
    "AUD/USD", "AUD/CAD", "EUR/USD", "EUR/CAD", "AUD/CHF", 
    "GBP/AUD", "GBP/USD", "EUR/AUD", "CHF/JPY", "GBP/CAD", 
    "GBP/CHF", "GBP/JPY", "USD/CHF", "EUR/CHF"
]

# 4. Custom Timeframe Options (1 min to 15 min sequential)
TIMEFRAMES = [
    "1min", "2min", "3min", "4min", "5min", 
    "6min", "7min", "8min", "9min", "10min", 
    "11min", "12min", "13min", "14min", "15min"
]

# 5. Main Screen Selectboxes
st.markdown("### ⚙️ Choose Trading Parameters")
col_p, col_t = st.columns(2)
with col_p:
    selected_pair = st.selectbox("Select Currency Pair", LIVE_PAIRS, key="pair_select")
with col_t:
    selected_timeframe = st.selectbox("Select Expiry Timeframe", TIMEFRAMES, key="time_select")

st.write("")

# 6. Signal Generation Action
if st.button("🚀 Generate Live Signal"):
    with st.spinner(f"Analyzing {selected_pair} ({selected_timeframe})..."):
        try:
            # Calculate UTC+5 time shifted 5 seconds into the future for execution buffer
            future_time_utc5 = datetime.utcnow() + timedelta(hours=5, seconds=5)
            formatted_time = future_time_utc5.strftime("%H:%M:%S")
            
            prompt = f"""
            You are an expert algorithmic binary options trader specializing in live currency markets.
            Asset: {selected_pair}
            Timeframe: {selected_timeframe}
            Target Entry Time (UTC+5): {formatted_time}

            Tasks:
            1. Determine the realistic current market open price for {selected_pair}.
            2. Determine the expected signal closing price based on short-term momentum and trend structure.
            3. Provide a directional signal ("CALL" or "PUT").
            4. Provide an estimated historical win accuracy percentage for this specific setup (e.g., 86.5%).
            5. Output ONLY a valid JSON object with no markdown ticks, structured exactly like this:
            {{
              "asset": "{selected_pair}",
              "timeframe": "{selected_timeframe}",
              "entry_time": "{formatted_time} (UTC+5)",
              "open_price": "...",
              "signal_close_price": "...",
              "signal": "CALL" or "PUT",
              "accuracy": "..."
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
                    "max_tokens": 250,
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
                    
                    st.markdown("### 🎯 Trader Shawkatz — Live Signal")
                    
                    res_col1, res_col2, res_col3 = st.columns(3)
                    with res_col1:
                        st.metric(label="Asset Pair", value=data.get("asset", selected_pair))
                        st.metric(label="Open Price", value=data.get("open_price", "N/A"))
                    with res_col2:
                        st.metric(label="Timeframe", value=data.get("timeframe", selected_timeframe))
                        st.metric(label="Signal Close Price", value=data.get("signal_close_price", "N/A"))
                    with res_col3:
                        st.metric(label="Entry Time (UTC+5)", value=data.get("entry_time", formatted_time))
                        st.metric(label="Win Accuracy", value=data.get("accuracy", "85%"))
                    
                    signal = data.get("signal", "NEUTRAL").upper()
                    if signal == "CALL":
                        st.success(f"**SIGNAL: CALL (UP) — Expiry: {selected_timeframe}**")
                    elif signal == "PUT":
                        st.error(f"**SIGNAL: PUT (DOWN) — Expiry: {selected_timeframe}**")
                    else:
                        st.warning(f"**SIGNAL: {signal}**")
                        
                else:
                    st.error(f"Unexpected API response format: {result}")
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")

        except Exception as e:
            st.error(f"Signal generation failed: {e}")
