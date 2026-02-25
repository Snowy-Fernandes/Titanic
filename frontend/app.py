# frontend/app.py
import streamlit as st
import requests
import base64
from datetime import datetime

# BACKEND URL - keep as your deployed Render backend
BACKEND = "https://titanic-backend-emeb.onrender.com"

st.set_page_config(
    page_title="Titanic AI Chatbot",
    layout="wide",
    page_icon="🚢",
    initial_sidebar_state="expanded",
)

# ── State defaults ────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    st.session_state.history = []

dark = st.session_state.dark_mode

# ── Color tokens ─────────────────────────────────────────────────────
if dark:
    PAGE_BG = "#09090f"
    GRID_COLOR = "rgba(255,255,255,0.025)"
    GLASS_BG = "rgba(255,255,255,0.04)"
    GLASS_BORDER = "rgba(255,255,255,0.08)"
    GLASS_BLUR = "20px"
    TEXT = "#f0f0f8"
    TEXT_DIM = "rgba(240,240,248,0.38)"
    USER_BG = "linear-gradient(135deg,#3b6cff 0%,#7c3aed 100%)"
    USER_TEXT = "#fff"
    BOT_BG = "rgba(255,255,255,0.05)"
    BOT_BORDER = "rgba(255,255,255,0.09)"
    BOT_TEXT = "#e4e4f0"
    ACCENT = "#3b6cff"
    ACCENT2 = "#7c3aed"
    SIDEBAR_BG = "rgba(9,9,15,0.97)"
    BTN_BG = "rgba(255,255,255,0.04)"
    BTN_HOVER_BG = "rgba(59,108,255,0.12)"
    BTN_HOVER_BD = "rgba(59,108,255,0.35)"
    INPUT_BG = "rgba(14,14,24,0.97)"
    INPUT_BORDER = "rgba(255,255,255,0.10)"
    GLOW = "rgba(59,108,255,0.18)"
    TOGGLE_LABEL = "🌙 Dark"
    DIVIDER = "rgba(255,255,255,0.07)"
    TAG_BG = "rgba(59,108,255,0.12)"
    TAG_COLOR = "#7aa2ff"
    BAR_BG = "rgba(10,10,18,0.96)"
    BAR_BORDER = "rgba(255,255,255,0.07)"
    SEND_SHADOW = "0 0 22px rgba(59,108,255,0.50)"
else:
    PAGE_BG = "#f4f6fb"
    GRID_COLOR = "rgba(0,0,0,0.025)"
    GLASS_BG = "rgba(255,255,255,0.80)"
    GLASS_BORDER = "rgba(0,0,0,0.07)"
    GLASS_BLUR = "20px"
    TEXT = "#111128"
    TEXT_DIM = "rgba(17,17,40,0.42)"
    USER_BG = "linear-gradient(135deg,#3b6cff 0%,#7c3aed 100%)"
    USER_TEXT = "#fff"
    BOT_BG = "rgba(255,255,255,0.90)"
    BOT_BORDER = "rgba(0,0,0,0.07)"
    BOT_TEXT = "#111128"
    ACCENT = "#3b6cff"
    ACCENT2 = "#7c3aed"
    SIDEBAR_BG = "rgba(244,246,251,0.97)"
    BTN_BG = "rgba(0,0,0,0.03)"
    BTN_HOVER_BG = "rgba(59,108,255,0.08)"
    BTN_HOVER_BD = "rgba(59,108,255,0.30)"
    INPUT_BG = "rgba(255,255,255,0.98)"
    INPUT_BORDER = "rgba(0,0,0,0.10)"
    GLOW = "rgba(59,108,255,0.12)"
    TOGGLE_LABEL = "☀️ Light"
    DIVIDER = "rgba(0,0,0,0.06)"
    TAG_BG = "rgba(59,108,255,0.08)"
    TAG_COLOR = "#3b6cff"
    BAR_BG = "rgba(248,249,255,0.97)"
    BAR_BORDER = "rgba(0,0,0,0.07)"
    SEND_SHADOW = "0 0 18px rgba(59,108,255,0.35)"

# ── Inject CSS ────────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

.stApp {{
    background-color: {PAGE_BG} !important;
    background-image:
        linear-gradient(0deg, {GRID_COLOR} 1px, transparent 1px),
        linear-gradient(90deg, {GRID_COLOR} 1px, transparent 1px) !important;
    background-size: 40px 40px !important;
    background-attachment: fixed !important;
    font-family: 'Sora', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {TEXT};
}}
#MainMenu, footer, header {{visibility:hidden;}}

.block-container {{
    max-width: 780px !important;
    padding: 1.5rem 1.25rem 2rem !important;
}}

/* glass card, header, messages, sidebar, input bar etc. – preserved from original */
.glass {{
    background: {GLASS_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 1.5rem;
    backdrop-filter: blur({GLASS_BLUR});
    -webkit-backdrop-filter: blur({GLASS_BLUR});
    padding: 1.5rem 1.5rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 0 rgba(255,255,255,0.05) inset,
                0 20px 60px rgba(0,0,0,0.25),
                0 0 0 1px {GLASS_BORDER};
    position: relative;
    overflow: hidden;
}}

.chat-header {{
    text-align: center;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid {DIVIDER};
    margin-bottom: 1.25rem;
}}
.chat-header-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px; height: 52px;
    border-radius: 16px;
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
    font-size: 1.5rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 8px 24px {GLOW};
}}
.chat-header h1 {{
    font-family: 'Sora', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: {TEXT};
    margin: 0 0 0.25rem;
    letter-spacing: -0.03em;
    line-height: 1.2;
}}
.chat-header-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.68rem;
    font-weight: 500;
    color: {TAG_COLOR};
    background: {TAG_BG};
    border-radius: 100px;
    padding: 0.2rem 0.65rem;
    letter-spacing: 0.03em;
    font-family: 'JetBrains Mono', monospace;
}}
.msg-row {{
    display: flex;
    margin-bottom: 1.1rem;
    align-items: flex-start;
    gap: 0.6rem;
    animation: slide-up 0.25s ease both;
}}
.msg-row.user {{ flex-direction: row-reverse; }}

.msg-avatar {{
    width: 32px; height: 32px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; flex-shrink: 0; margin-top: 2px;
    font-weight: 700;
}}
.msg-avatar.user-av {{ background: linear-gradient(135deg, {ACCENT}, {ACCENT2}); color: #fff; box-shadow: 0 4px 12px {GLOW}; }}
.msg-avatar.bot-av {{ background: {BOT_BG}; border: 1px solid {BOT_BORDER}; font-size: 0.9rem; }}

.msg-bubble {{ padding: 0.7rem 1rem; border-radius: 1rem; font-size: 0.83rem; line-height: 1.65; max-width: 78%; position: relative; }}
.msg-bubble.user-msg {{ background: {USER_BG}; color: {USER_TEXT}; border-bottom-right-radius: 0.3rem; box-shadow: 0 4px 20px {GLOW}; font-weight: 400; }}
.msg-bubble.bot-msg {{ background: {BOT_BG}; color: {BOT_TEXT}; border: 1px solid {BOT_BORDER}; border-bottom-left-radius: 0.3rem; backdrop-filter: blur(10px); }}

section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid {GLASS_BORDER} !important;
}}
section[data-testid="stSidebar"] * {{ color: {TEXT} !important; font-family: 'Sora', sans-serif !important; }}

.stChatInput {{
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 9999 !important;
    padding: 1rem 2rem 1.35rem !important;
    background: {BAR_BG} !important;
    border-top: 1px solid {BAR_BORDER} !important;
    backdrop-filter: blur(28px) !important;
}}
.stChatInput > div {{ background: {INPUT_BG} !important; border: 1.5px solid {INPUT_BORDER} !important; border-radius: 1.1rem !important; max-width: 860px !important; margin: 0 auto !important; }}
.stChatInput textarea {{ color: {TEXT} !important; font-family: 'Sora', sans-serif !important; font-size: 0.86rem !important; }}

.stImage > img {{ border-radius: 0.85rem !important; border: 1px solid {GLASS_BORDER} !important; box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important; margin-top: 0.5rem !important; }}

hr {{ border-color: {DIVIDER} !important; margin: 0.75rem 0 !important; }}
</style>
""",
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:0.5rem;margin-bottom:0.15rem;'>"
        f"<div style='width:28px;height:28px;border-radius:8px;background:linear-gradient(135deg,{ACCENT},{ACCENT2});"
        f"display:flex;align-items:center;justify-content:center;font-size:0.85rem;flex-shrink:0;'>🚢</div>"
        f"<span style='font-size:0.9rem;font-weight:700;letter-spacing:-0.02em;'>Titanic Chatbot</span></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:0.69rem;color:{TEXT_DIM} !important;margin:0 0 1rem 0;padding-left:2px;'>LangChain · HuggingFace</p>",
        unsafe_allow_html=True,
    )

    st.markdown(f"<p class='sidebar-section-label'>Theme</p>", unsafe_allow_html=True)
    # keep using st.toggle if available in your Streamlit version; behaves like a boolean toggle
    try:
        toggle_val = st.toggle(TOGGLE_LABEL, value=dark, key="theme_toggle")
    except Exception:
        # fallback if st.toggle not available in some Streamlit versions
        toggle_val = st.checkbox(TOGGLE_LABEL, value=dark, key="theme_toggle_fallback")

    if toggle_val:
        if not dark:
            st.session_state.dark_mode = True
            st.rerun()
    else:
        if dark:
            st.session_state.dark_mode = False
            st.rerun()

    st.divider()

    st.markdown(
        f"<p class='sidebar-section-label'>Quick prompts</p>", unsafe_allow_html=True
    )

    examples = [
        "What percentage of passengers were male?",
        "Show me a histogram of passenger ages",
        "What was the average ticket fare?",
        "How many passengers embarked from each port?",
        "What is the survival rate by gender?",
        "How many passengers in each class?",
        "What is the survival rate by class?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}"):
            st.session_state.history.append(
                {"role": "user", "text": ex, "time": datetime.now().strftime("%H:%M")}
            )
            try:
                resp = requests.post(BACKEND, json={"question": ex}, timeout=60)
                data = resp.json()
            except Exception as e:
                data = {"answer": f"⚠ Cannot reach the backend. ({e})", "plot": None}
            st.session_state.history.append(
                {
                    "role": "bot",
                    "text": data["answer"],
                    "plot": data.get("plot"),
                    "time": datetime.now().strftime("%H:%M"),
                }
            )
            st.rerun()

    st.divider()
    if st.button("🗑️  Clear chat", key="clear"):
        st.session_state.history = []
        st.rerun()

    # Deploy helper panel (keeps content exactly as before)
    st.divider()
    st.markdown(
        "<p class='sidebar-section-label'>🚀 Deploy</p>", unsafe_allow_html=True
    )
    st.markdown(
        f"<div style='font-size:0.72rem;line-height:1.75;color:{TEXT_DIM} !important;"
        f"background:{BTN_BG};border:1px solid {GLASS_BORDER};border-radius:0.7rem;"
        f"padding:0.65rem 0.8rem;'>"
        f"<span style='color:{TAG_COLOR} !important;font-weight:600;'>Streamlit Community Cloud</span><br>"
        f"① Push project to <b style='color:{TEXT} !important;'>GitHub</b><br>"
        f"② Visit <code style='font-size:0.67rem;color:{ACCENT} !important;'>share.streamlit.io</code><br>"
        f"③ New app → select repo &amp; <code style='font-size:0.67rem;'>app.py</code><br>"
        f"④ Add secrets if needed → <b style='color:{TEXT} !important;'>Deploy!</b>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── Main chat area ───────────────────────────────────────────────────
st.markdown("<div style='max-width:780px;margin:0 auto;'>", unsafe_allow_html=True)
st.markdown(
    f"""
<div class='glass'>
    <div class='chat-header'>
        <div class='chat-header-icon'>🚢</div>
        <h1>Titanic AI Chatbot</h1>
        <div style='margin-top:0.5rem;'>
            <span class='chat-header-badge'>LIVE · Dataset Ready</span>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

if not st.session_state.history:
    st.markdown(
        f"""
    <div class='empty-state'>
        <span class='empty-icon'>💬</span>
        <h3>Start a conversation</h3>
        <p>Ask anything about the Titanic dataset — survival rates, demographics, fares, and more. Try the quick prompts on the left.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.markdown(
                f"""
            <div class='msg-row user'>
                <div class='msg-avatar user-av'>U</div>
                <div>
                    <div class='msg-bubble user-msg'>{msg["text"]}</div>
                    <div class='msg-meta'><span class='msg-time'>{msg["time"]}</span></div>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )
        else:
            bot_html = msg["text"].replace("\n", "<br>")
            st.markdown(
                f"""
            <div class='msg-row'>
                <div class='msg-avatar bot-av'>🚢</div>
                <div>
                    <div class='msg-bubble bot-msg'>{bot_html}</div>
                    <div class='msg-meta'><span class='msg-time'>{msg["time"]}</span></div>
                </div>
            </div>""",
                unsafe_allow_html=True,
            )
            if msg.get("plot"):
                try:
                    img_bytes = base64.b64decode(msg["plot"])
                    # use use_column_width=True for robust display
                    st.image(img_bytes, use_column_width=True)
                except Exception:
                    pass

st.markdown("</div></div>", unsafe_allow_html=True)

# ── Chat input ───────────────────────────────────────────────────────
user_text = st.chat_input("Ask about the Titanic dataset…")

if user_text:
    st.session_state.history.append(
        {"role": "user", "text": user_text, "time": datetime.now().strftime("%H:%M")}
    )
    try:
        with st.spinner("Analyzing…"):
            resp = requests.post(BACKEND, json={"question": user_text}, timeout=60)
            data = resp.json()
    except Exception as e:
        data = {"answer": f"⚠ Cannot reach the backend. ({e})", "plot": None}

    st.session_state.history.append(
        {
            "role": "bot",
            "text": data["answer"],
            "plot": data.get("plot"),
            "time": datetime.now().strftime("%H:%M"),
        }
    )
    # correct placement of rerun: on its own line
    st.rerun()
