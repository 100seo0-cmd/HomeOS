"""
HomeOS - AI Home Operating System
Main application entry point.
"""

import streamlit as st

# Page config (must be the first Streamlit command)
st.set_page_config(
    page_title="HomeOS",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    background-color: #F8FAFC;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
    border-right: 1px solid #E5E7EB;
}

section[data-testid="stSidebar"] .stMarkdown h1 {
    font-size: 1.3rem !important;
    color: #0F172A;
    font-weight: 700;
    letter-spacing: -0.02em;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #64748B;
    font-size: 0.85rem;
}

/* Main container */
.block-container {
    max-width: 960px;
    padding: 2.5rem 2rem 4rem 2rem;
}

/* Headings */
h1, h2, h3 {
    color: #0F172A !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em;
}
h1 { font-size: 1.85rem !important; }
h2 { font-size: 1.35rem !important; }
h3 { font-size: 1.1rem !important; }

p, li, span, div {
    color: #334155;
}

/* Card (blue tint) */
.homeos-card-blue {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.06);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.01em;
}
.badge-urgent { background: #FEE2E2; color: #DC2626; }
.badge-warn   { background: #FEF3C7; color: #D97706; }
.badge-ok     { background: #DCFCE7; color: #16A34A; }
.badge-muted  { background: #F1F5F9; color: #64748B; }
.badge-blue   { background: #DBEAFE; color: #2563EB; }

/* Buttons */
.stButton > button {
    border-radius: 12px;
    border: 1px solid #E5E7EB;
    background: #FFFFFF;
    color: #334155;
    font-weight: 500;
    padding: 0.45rem 1.2rem;
    font-size: 0.85rem;
    transition: all 0.15s ease;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
}
.stButton > button:hover {
    background: #F1F5F9;
    border-color: #CBD5E1;
    color: #0F172A;
}

/* Text inputs */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    border-radius: 12px !important;
    border: 1px solid #E5E7EB !important;
    padding: 0.55rem 0.85rem !important;
    font-size: 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
}

/* Chat input */
[data-testid="stChatInput"] textarea {
    border-radius: 16px !important;
    border: 1px solid #E5E7EB !important;
    font-size: 0.9rem !important;
    padding: 0.7rem 1rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
}

/* Chat message */
[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: 12px !important;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #E5E7EB;
    margin: 1.5rem 0;
}

/* Links */
a { color: #3B82F6; }
a:hover { color: #2563EB; }

/* Hero header */
.homeos-hero {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
}
.homeos-hero h1 {
    font-size: 2.2rem !important;
    margin-bottom: 0.2rem;
}
.homeos-hero p {
    color: #64748B;
    font-size: 1rem;
    margin-top: 0;
}

/* Muted text */
.text-muted {
    color: #64748B;
    font-size: 0.82rem;
}

/* Timeline */
.timeline-date {
    font-size: 0.78rem;
    color: #64748B;
    font-weight: 600;
    margin-bottom: 0.2rem;
}
.timeline-event {
    font-size: 0.95rem;
    color: #334155;
    margin-bottom: 0.2rem;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 0.4rem 1rem;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("# 🏠 HomeOS")
    st.markdown(
        '<p class="text-muted">Your AI-powered<br>home operating system</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "Navigate",
        ["🏠 Dashboard", "📦 Inventory", "🔧 Appliances", "🤖 AI Chat", "📅 Timeline"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<p class="text-muted">HomeOS v1.0<br>Calm home management</p>',
        unsafe_allow_html=True,
    )

# Page router (imports from views/, not pages/)
if page == "🏠 Dashboard":
    from views import dashboard
    dashboard.render()
elif page == "📦 Inventory":
    from views import inventory
    inventory.render()
elif page == "🔧 Appliances":
    from views import appliances
    appliances.render()
elif page == "🤖 AI Chat":
    from views import chat
    chat.render()
elif page == "📅 Timeline":
    from views import timeline
    timeline.render()
