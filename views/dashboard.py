"""
Dashboard page.
"""

import streamlit as st
from utils.storage import load_json
from utils.recommendation import generate_recommendations, generate_summary
from utils.ui_components import page_header, render_blue_card, spacer

def render():
    # Hero header
    st.markdown(
        """
        <div class="homeos-hero">
            <h1>🏠 HomeOS</h1>
            <p>Your AI Operating System for Home</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    spacer("0.5rem")

    # Load data
    inventory = load_json("inventory.json", [])
    appliances = load_json("appliances.json", [])
    schedule = load_json("schedule.json", [])

    # Today's Recommendations
    st.markdown("## 💡 Today's Recommendations")
    spacer("0.3rem")

    recs = generate_recommendations(inventory, appliances, schedule)

    # 2-column layout with expander INSIDE each container
    cols = st.columns(2)
    for idx, rec in enumerate(recs):
        col = cols[idx % 2]
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<div style='font-size:1.5rem; margin-bottom:0.3rem;'>{rec['icon']}</div>"
                    f"<div style='font-weight:600; color:#0F172A; font-size:0.95rem; "
                    f"margin-bottom:0.3rem;'>{rec['title']}</div>"
                    f"<div style='color:#64748B; font-size:0.84rem; line-height:1.5;'>"
                    f"{rec['detail']}</div>",
                    unsafe_allow_html=True,
                )
                with st.expander("Why?", expanded=False):
                    for reason in rec.get("reasons", []):
                        st.markdown(f"- {reason}")

    spacer("1rem")

    # AI Summary
    st.markdown("## 🤖 AI Summary")
    spacer("0.3rem")

    summary = generate_summary(inventory, appliances, schedule)
    render_blue_card(
        f"""
        <div style="font-size:0.92rem; line-height:1.7; color:#1E40AF; white-space:pre-line;">
            {summary}
        </div>
        """
    )

    spacer("1rem")

    # Quick action
    st.markdown(
        '<div style="text-align:center;"><p class="text-muted">'
        'Have a question about your home?</p></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🤖 Open AI Chat", use_container_width=True, type="primary"):
            st.session_state["nav_to_chat"] = True
            st.rerun()
