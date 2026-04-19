import streamlit as st
from agent import process
import time
import re

st.set_page_config(page_title="RescuePulse Med AI", layout="wide")

# -------- UI STYLE -------- #
st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}
.stChatMessage {
    background-color: #111827;
    border-radius: 12px;
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 RescuePulse Med AI")
st.caption("Autonomous Multi-Agent Emergency Assistant")

# -------- FUNCTIONS -------- #
def detect_blood_info(text):
    blood = re.search(r'\b(A|B|AB|O)[+-]\b', text.upper())
    qty = re.search(r'(\d+)\s*(L|ML|ltr)', text.lower())

    return (blood.group() if blood else None,
            qty.group() if qty else None)


def find_blood_source(blood):
    hospitals = [
        {"name": "City Hospital", "blood": ["O+", "A+"], "distance": "2 km"},
        {"name": "Red Cross Center", "blood": ["B+", "O+"], "distance": "5 km"},
        {"name": "Apollo Hospital", "blood": ["AB+", "O-"], "distance": "3 km"}
    ]
    return [h for h in hospitals if blood in h["blood"]]


def alert(msg):
    st.sidebar.error(f"🚨 Doctor Alert: {msg}")

# -------- MEMORY -------- #
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------- SHOW CHAT -------- #
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# -------- INPUT -------- #
user = st.chat_input("Enter patient condition...")

if user:
    st.session_state.messages.append({"role": "user", "content": user})

    with st.chat_message("user"):
        st.markdown(user)

    result = process(user)

    # -------- RESPONSE -------- #
    if result["severity"] == "CRITICAL":
        alert(user)

        blood, qty = detect_blood_info(user)

        if blood:
            resource = f"🩸 {blood} blood requested"
            if qty:
                resource += f" ({qty})"
        elif "blood" in user.lower():
            resource = "🩸 Blood requested"
        elif "accident" in user.lower():
            resource = "🚑 Emergency support requested"
        else:
            resource = "📡 Monitoring"

        reply = f"""🚨 **CRITICAL CASE**

**Condition:** {result['diagnosis']}  
**Confidence:** {int(result['confidence']*100)}%

⚠️ Doctor notified  
{resource}
"""

    elif result["severity"] == "MODERATE":
        reply = f"""⚠️ **MODERATE CASE**

{result['diagnosis']}  
Confidence: {int(result['confidence']*100)}%
"""

    else:
        reply = f"""✅ **LOW PRIORITY**

{result['diagnosis']}  
Confidence: {int(result['confidence']*100)}%
"""

    explain = f"""
### 🧠 Reasoning
Severity: **{result['severity']}**
Confidence: **{int(result['confidence']*100)}%**
"""

    full = reply + explain
    st.session_state.messages.append({"role": "assistant", "content": full})

    # -------- TYPING -------- #
    with st.chat_message("assistant"):
        box = st.empty()
        txt = ""
        for c in full:
            txt += c
            box.markdown(txt)
            time.sleep(0.01)

    # -------- BLOOD TRACKING -------- #
    blood, qty = detect_blood_info(user)

    if blood:
        sources = find_blood_source(blood)
        st.subheader("🩸 Blood Tracking")

        for s in sources:
            st.info(f"""
🏥 {s['name']}
📍 {s['distance']}
🩸 {blood}
📦 Dispatching
⏱ ETA 10–15 mins
""")

# -------- ALERT PANEL -------- #
st.divider()
st.subheader("🚨 Alerts")

for m in st.session_state.messages:
    if "CRITICAL" in m["content"]:
        st.error("🚨 Critical detected")

# -------- SIDEBAR -------- #
with st.sidebar:
    st.title("System")
    st.write("✔ Multi-Agent AI")
    st.write("✔ Emergency Detection")
    st.write("✔ Resource Tracking")
    st.warning("Doctor must confirm")