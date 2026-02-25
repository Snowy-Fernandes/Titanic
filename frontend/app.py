import streamlit as st
import requests
import base64
from datetime import datetime

BACKEND = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Titanic AI Chatbot", layout="centered", page_icon="🚢")

# ── Theme state ──────────────────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "history" not in st.session_state:
    st.session_state.history = []

dark = st.session_state.dark_mode

# ── Color tokens ─────────────────────────────────────────────────────
if dark:
    PAGE_BG = "#09090f"
    GRID_COLOR = "rgba(255,255,255,0.03)"
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
    SIDEBAR_BG = "rgba(9,9,15,0.96)"
    BTN_BG = "rgba(255,255,255,0.04)"
    BTN_HOVER_BG = "rgba(59,108,255,0.12)"
    BTN_HOVER_BD = "rgba(59,108,255,0.35)"
    INPUT_BG = "rgba(255,255,255,0.05)"
    GLOW = "rgba(59,108,255,0.15)"
    TOGGLE_LABEL = "🌙 Dark"
    DIVIDER = "rgba(255,255,255,0.07)"
    TAG_BG = "rgba(59,108,255,0.12)"
    TAG_COLOR = "#7aa2ff"
else:
    PAGE_BG = "#f4f6fb"
    GRID_COLOR = "rgba(0,0,0,0.03)"
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
    SIDEBAR_BG = "rgba(244,246,251,0.96)"
    BTN_BG = "rgba(0,0,0,0.03)"
    BTN_HOVER_BG = "rgba(59,108,255,0.08)"
    BTN_HOVER_BD = "rgba(59,108,255,0.30)"
    INPUT_BG = "rgba(255,255,255,0.90)"
    GLOW = "rgba(59,108,255,0.10)"
    TOGGLE_LABEL = "☀️ Light"
    DIVIDER = "rgba(0,0,0,0.06)"
    TAG_BG = "rgba(59,108,255,0.08)"
    TAG_COLOR = "#3b6cff"

# ── Global CSS ───────────────────────────────────────────────────────
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & base ── */
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

/* ── Noise texture overlay ── */
.stApp::before {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}}

/* ── Main container ── */
.block-container {{
    max-width: 780px !important;
    padding: 1.5rem 1.25rem 2rem !important;
}}

/* ── Glass card ── */
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
.glass::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}}

/* ── Header ── */
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
.chat-header-badge::before {{
    content: '';
    width: 5px; height: 5px;
    border-radius: 50%;
    background: currentColor;
    opacity: 0.8;
    animation: pulse-dot 2s ease infinite;
}}
@keyframes pulse-dot {{
    0%, 100% {{ opacity: 0.8; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(0.85); }}
}}

/* ── Messages ── */
.msg-row {{
    display: flex;
    margin-bottom: 1.1rem;
    align-items: flex-start;
    gap: 0.6rem;
    animation: slide-up 0.25s ease both;
}}
@keyframes slide-up {{
    from {{ opacity: 0; transform: translateY(6px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.msg-row.user {{ flex-direction: row-reverse; }}

.msg-avatar {{
    width: 32px; height: 32px;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.7rem; flex-shrink: 0; margin-top: 2px;
    font-weight: 700;
}}
.msg-avatar.user-av {{
    background: linear-gradient(135deg, {ACCENT}, {ACCENT2});
    color: #fff;
    box-shadow: 0 4px 12px {GLOW};
}}
.msg-avatar.bot-av {{
    background: {BOT_BG};
    border: 1px solid {BOT_BORDER};
    font-size: 0.9rem;
}}

.msg-bubble {{
    padding: 0.7rem 1rem;
    border-radius: 1rem;
    font-size: 0.83rem;
    line-height: 1.65;
    max-width: 78%;
    position: relative;
}}
.msg-bubble.user-msg {{
    background: {USER_BG};
    color: {USER_TEXT};
    border-bottom-right-radius: 0.3rem;
    box-shadow: 0 4px 20px {GLOW};
    font-weight: 400;
}}
.msg-bubble.bot-msg {{
    background: {BOT_BG};
    color: {BOT_TEXT};
    border: 1px solid {BOT_BORDER};
    border-bottom-left-radius: 0.3rem;
    backdrop-filter: blur(10px);
}}

.msg-meta {{
    display: flex;
    align-items: center;
    gap: 0.3rem;
    margin-top: 0.3rem;
}}
.msg-time {{
    font-size: 0.6rem;
    color: {TEXT_DIM};
    font-family: 'JetBrains Mono', monospace;
}}
.msg-row.user .msg-meta {{ flex-direction: row-reverse; }}

/* ── Empty state ── */
.empty-state {{
    text-align: center;
    padding: 3rem 1rem 2.5rem;
    color: {TEXT_DIM};
}}
.empty-icon {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
    opacity: 0.4;
}}
.empty-state h3 {{
    font-size: 1rem;
    font-weight: 600;
    color: {TEXT};
    margin: 0 0 0.5rem;
    letter-spacing: -0.02em;
}}
.empty-state p {{
    font-size: 0.78rem;
    max-width: 320px;
    margin: 0 auto;
    line-height: 1.6;
    opacity: 0.7;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {SIDEBAR_BG} !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid {GLASS_BORDER} !important;
}}
section[data-testid="stSidebar"] * {{
    color: {TEXT} !important;
    font-family: 'Sora', sans-serif !important;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background: {BTN_BG} !important;
    color: {TEXT} !important;
    border: 1px solid {GLASS_BORDER} !important;
    border-radius: 0.7rem !important;
    font-size: 0.74rem !important;
    padding: 0.5rem 0.8rem !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.18s ease !important;
    font-weight: 400 !important;
    font-family: 'Sora', sans-serif !important;
    line-height: 1.4 !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: {BTN_HOVER_BG} !important;
    border-color: {BTN_HOVER_BD} !important;
    transform: translateX(2px) !important;
}}

/* ── Sidebar label ── */
.sidebar-section-label {{
    font-size: 0.6rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {TEXT_DIM} !important;
    margin-bottom: 0.4rem;
    margin-top: 0.1rem;
}}

/* ── Toggle ── */
section[data-testid="stSidebar"] .stToggle {{
    margin-bottom: 0 !important;
}}

/* ── Input ── */
.stChatInput {{
    margin-top: 0.5rem;
}}
.stChatInput > div {{
    background: {INPUT_BG} !important;
    border: 1px solid {GLASS_BORDER} !important;
    border-radius: 1rem !important;
    backdrop-filter: blur(10px) !important;
}}
.stChatInput > div:focus-within {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 3px {GLOW} !important;
}}
.stChatInput textarea {{
    font-family: 'Sora', sans-serif !important;
    font-size: 0.83rem !important;
    color: {TEXT} !important;
}}
.stChatInput textarea::placeholder {{
    color: {TEXT_DIM} !important;
}}

/* ── Divider ── */
hr {{
    border-color: {DIVIDER} !important;
    margin: 0.75rem 0 !important;
}}

/* ── Spinner ── */
.stSpinner > div {{
    border-top-color: {ACCENT} !important;
}}

/* ── Images from bot ── */
.stImage > img {{
    border-radius: 0.85rem !important;
    border: 1px solid {GLASS_BORDER} !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2) !important;
    margin-top: 0.5rem !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {GLASS_BORDER}; border-radius: 4px; }}
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
        f"<p style='font-size:0.69rem;color:{TEXT_DIM} !important;margin:0 0 1rem 0;padding-left:2px;'>"
        f"LangChain · HuggingFace</p>",
        unsafe_allow_html=True,
    )

    # ── Theme toggle ──
    st.markdown(f"<p class='sidebar-section-label'>Theme</p>", unsafe_allow_html=True)
    if st.toggle(TOGGLE_LABEL, value=dark, key="theme_toggle"):
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
                    st.image(img_bytes, width="stretch")
                except Exception:
                    pass

st.markdown("</div></div>", unsafe_allow_html=True)

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
    st.rerun()
