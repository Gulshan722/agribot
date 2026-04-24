# app.py — AgriExpert Final Clean
import streamlit as st
import json
import re
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '.')

st.set_page_config(
    page_title="AgriExpert",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: #0A1207 !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    transform: none !important;
    visibility: visible !important;
    display: block !important;
    min-width: 240px !important;
    width: 240px !important;
    background: #0D1A08 !important;
    border-right: 1px solid #1A2E0E !important;
    transition: none !important;
}
section[data-testid="stSidebar"][aria-expanded="false"] {
    margin-left: 0 !important;
    transform: none !important;
}
[data-testid="stSidebarContent"] { padding: 1.2rem 0.9rem !important; }
[data-testid="stSidebarCollapseButton"] { display: none !important; }
[data-testid="stMainMenuButton"] { display: none !important; }
[data-testid="stSidebar"] * {
    color: #8AAA60 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #6A8A45 !important;
    border: 1px solid #1A2E0E !important;
    border-radius: 8px !important;
    font-size: 0.78rem !important;
    padding: 0.4rem 0.7rem !important;
    margin-bottom: 3px !important;
    width: 100% !important;
    text-align: left !important;
    white-space: normal !important;
    height: auto !important;
    line-height: 1.35 !important;
    transition: background 0.15s, border-color 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #111D0A !important;
    border-color: #2A4A18 !important;
    color: #A8C870 !important;
}
[data-testid="stSidebar"] hr {
    border: none !important;
    border-top: 1px solid #1A2E0E !important;
    margin: 0.8rem 0 !important;
}

/* ── Main ── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Header ── */
.agri-header {
    background: #0D1A08;
    border-bottom: 1px solid #1A2E0E;
    padding: 1rem 2rem;
    text-align: center;
}
.agri-logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #C8E890;
    line-height: 1;
}
.agri-logo span { color: #6AB820; }
.agri-sub {
    color: #2A4A18;
    font-size: 0.62rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

/* ── Messages ── */
.user-bubble {
    display: flex;
    justify-content: flex-end;
    padding: 0.3rem 1.5rem;
}
.user-bubble-inner {
    background: #1A3010;
    border: 1px solid #243E14;
    color: #C8E890;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 62%;
    font-size: 0.9rem;
    line-height: 1.55;
}
.bot-row {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 0.3rem 1.5rem;
}
.bot-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #1A3010;
    border: 1px solid #243E14;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    flex-shrink: 0;
    margin-top: 3px;
}
.bot-bubble-inner {
    background: #0F1D0A;
    border: 1px solid #162810;
    color: #A8C870;
    padding: 0.85rem 1.1rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 76%;
    font-size: 0.9rem;
    line-height: 1.7;
}
.bot-bubble-inner p { margin: 0 0 0.5rem; }
.bot-bubble-inner p:last-child { margin: 0; }
.bot-bubble-inner ol, .bot-bubble-inner ul {
    padding-left: 1.2rem;
    margin: 0.3rem 0;
}
.bot-bubble-inner li { margin-bottom: 0.3rem; }
.bot-bubble-inner strong { color: #C8E890; }

/* ── Citations ── */
.cite-row {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    padding: 0.2rem 1.5rem 0.6rem 4.2rem;
}
.cite-pill {
    background: transparent;
    border: 1px solid #1A2E0E;
    color: #2A4A18;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 20px;
}

/* ── Welcome ── */
.welcome-wrap {
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    padding: 1rem 1.5rem;
}
.welcome-inner {
    background: #0F1D0A;
    border: 1px solid #162810;
    color: #4A6A28;
    padding: 0.85rem 1.1rem;
    border-radius: 4px 18px 18px 18px;
    max-width: 76%;
    font-size: 0.88rem;
    line-height: 1.65;
}

/* ── Input ── */
.stForm {
    background: #0D1A08 !important;
    border: 1px solid #1A2E0E !important;
    border-radius: 14px !important;
    padding: 0.7rem 0.9rem !important;
    margin: 0 1.5rem 1rem !important;
}
.stTextInput > div > div > input {
    background: #0A1207 !important;
    border: 1px solid #1A2E0E !important;
    border-radius: 10px !important;
    color: #A8C870 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #2A4A18 !important;
    box-shadow: 0 0 0 2px rgba(42,74,24,0.25) !important;
}
.stTextInput > div > div > input::placeholder { color: #1A2E0E !important; }
.stForm .stButton > button {
    background: #1A3010 !important;
    color: #C8E890 !important;
    border: 1px solid #243E14 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    padding: 0.65rem 1rem !important;
    width: 100% !important;
    transition: all 0.2s !important;
    letter-spacing: 0.3px !important;
}
.stForm .stButton > button:hover {
    background: #243E14 !important;
    box-shadow: 0 3px 12px rgba(26,48,16,0.6) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 2px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #1A2E0E; border-radius: 2px; }

/* ── Hide chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton, [data-testid="stToolbar"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── Translations ───────────────────────────────────────────
T = {
    "English": {
        "subtitle": "AI-POWERED AGRICULTURAL ADVISORY",
        "placeholder": "Ask any farming question...",
        "ask_btn": "Send →",
        "clear_btn": "🗑  New Chat",
        "thinking": "Thinking...",
        "welcome": "Hello! I'm AgriExpert, your AI farming advisor. Ask me anything about crops, soil, pests, fertilizers, or climate-smart agriculture — every answer comes with verified source citations.",
        "quick_q": "SUGGESTIONS",
        "lang": "LANGUAGE",
        "no_info": "I don't have enough information on this topic in my knowledge base. Please consult your local agricultural extension officer.",
    },
    "नेपाली": {
        "subtitle": "AI-आधारित कृषि सल्लाह प्रणाली",
        "placeholder": "कुनै पनि कृषि प्रश्न सोध्नुहोस्...",
        "ask_btn": "पठाउनुस् →",
        "clear_btn": "🗑  नयाँ च्याट",
        "thinking": "खोज्दै...",
        "welcome": "नमस्ते! म AgriExpert हुँ — तपाईंको AI कृषि सल्लाहकार। बाली, माटो, कीरा, मल वा जलवायु-स्मार्ट कृषिबारे कुनै पनि प्रश्न सोध्नुहोस्।",
        "quick_q": "सुझावहरू",
        "lang": "भाषा",
        "no_info": "मेरो ज्ञान आधारमा पर्याप्त जानकारी छैन। कृपया स्थानीय कृषि अधिकारीसँग सम्पर्क गर्नुहोस्।",
    }
}

QUICK_Q = {
    "English": [
        "How to manage drought in wheat?",
        "Best fertilizer for rice paddy?",
        "Organic aphid control?",
        "Signs of nitrogen deficiency?",
        "How to improve soil health?",
        "What is conservation agriculture?",
        "Crop rotation benefits?",
        "Integrated pest management?",
    ],
    "नेपाली": [
        "गहुँमा खडेरी व्यवस्थापन?",
        "धानको लागि उत्तम मल?",
        "जैविक कीरा नियन्त्रण?",
        "नाइट्रोजन कमीका संकेत?",
        "माटोको स्वास्थ्य सुधार?",
        "संरक्षण कृषि के हो?",
    ]
}

# ── Session State ──────────────────────────────────────────
for key, val in {
    "messages": [],
    "query_count": 0,
    "language": "English",
    "quick_q_input": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ── Helpers ────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_agribot():
    from src.agribot import ask
    return ask

def clean_answer(text: str) -> str:
    text = re.sub(r'\(Source:[^)]*\)', '', text)
    text = re.sub(r'Sources?:\s*\[[\d,\s]+\]\.?', '', text)
    text = re.sub(r'\nSources?:\s*\n?', '', text)
    text = re.sub(r'\[(\d+)\]\s*\(Source:[^)]*\)', r'[\1]', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

# ── Sidebar ────────────────────────────────────────────────
lang = st.session_state.language
TL = T[lang]

with st.sidebar:
    st.markdown("""
    <div style='margin-bottom:1.2rem;'>
        <div style='font-family:"Playfair Display",serif;font-size:1.4rem;
                    color:#6AB820;font-weight:700;line-height:1;'>
            🌾 AgriExpert
        </div>
        <div style='font-size:0.6rem;color:#1E3010;letter-spacing:2.5px;
                    text-transform:uppercase;margin-top:4px;'>
            Advisory System
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f"<div style='font-size:0.6rem;color:#1E3010;letter-spacing:2px;"
        f"text-transform:uppercase;margin-bottom:0.35rem;'>{TL['lang']}</div>",
        unsafe_allow_html=True
    )
    new_lang = st.radio(
        "lang", ["English", "नेपाली"],
        index=0 if lang == "English" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    if new_lang != lang:
        st.session_state.language = new_lang
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.6rem;color:#1E3010;letter-spacing:2px;"
        f"text-transform:uppercase;margin-bottom:0.4rem;'>{TL['quick_q']}</div>",
        unsafe_allow_html=True
    )
    for q in QUICK_Q[lang]:
        if st.button(q, key=f"qq_{q}"):
            st.session_state.quick_q_input = q
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button(TL["clear_btn"], use_container_width=True):
        st.session_state.messages = []
        st.session_state.quick_q_input = ""
        st.rerun()

# ── Header ────────────────────────────────────────────────
TL = T[st.session_state.language]

st.markdown(f"""
<div class="agri-header">
    <div class="agri-logo">🌾 <span>Agri</span>Expert</div>
    <div class="agri-sub">{TL['subtitle']}</div>
</div>
""", unsafe_allow_html=True)

# ── Chat area ─────────────────────────────────────────────
with st.container(height=560, border=False):
    if not st.session_state.messages:
        st.markdown(f"""
        <div class="welcome-wrap">
            <div class="bot-avatar">🌾</div>
            <div class="welcome-inner">{TL['welcome']}</div>
        </div>
        """, unsafe_allow_html=True)

    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="user-bubble">
                <div class="user-bubble-inner">{msg['content']}</div>
            </div>""", unsafe_allow_html=True)
        else:
            answer_clean = clean_answer(msg["content"])
            st.markdown(f"""
            <div class="bot-row">
                <div class="bot-avatar">🌾</div>
                <div class="bot-bubble-inner">{answer_clean}</div>
            </div>""", unsafe_allow_html=True)

            if msg.get("citations"):
                pills = "".join([
                    f'<span class="cite-pill">'
                    f'📄 [{c["number"]}] {c["source"]} p.{c["page"]}'
                    f'</span>'
                    for c in msg["citations"]
                ])
                st.markdown(
                    f'<div class="cite-row">{pills}</div>',
                    unsafe_allow_html=True
                )

# ── Input ─────────────────────────────────────────────────
default_val = st.session_state.quick_q_input
st.session_state.quick_q_input = ""

with st.form("chat_form", clear_on_submit=True):
    c1, c2 = st.columns([6, 1])
    with c1:
        user_input = st.text_input(
            "q", value=default_val,
            placeholder=TL["placeholder"],
            label_visibility="collapsed"
        )
    with c2:
        submitted = st.form_submit_button(
            TL["ask_btn"], use_container_width=True
        )

if submitted and user_input.strip():
    st.session_state.messages.append(
        {"role": "user", "content": user_input.strip()}
    )
    st.session_state.query_count += 1

    with st.spinner(TL["thinking"]):
        try:
            result = load_agribot()(
                user_input.strip(),
                run_faithfulness_check=False
            )
            answer = result.get("answer", TL["no_info"])
            citations = result.get("citations", [])
        except Exception as e:
            answer = TL["no_info"]
            citations = []

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "citations": citations
    })
    st.rerun()