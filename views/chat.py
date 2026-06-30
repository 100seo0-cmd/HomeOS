"""
AI Chat page.
"""

import streamlit as st
from utils.storage import load_json
from utils.ai import get_chat_response
from utils.ui_components import page_header, spacer

def render():
    page_header("🤖", "AI Chat", "Ask me anything about managing your home.")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Quick action chips
    st.markdown('<p class="text-muted">Try asking:</p>', unsafe_allow_html=True)

    chip_cols = st.columns(4)
    chips = [
        ("🥗 What to eat first?", "뭐 먼저 먹어야 해?"),
        ("📅 This week?", "이번 주 뭐 있어?"),
        ("✈️ Travel prep", "여행 준비 도와줘"),
        ("🛒 Shopping list", "뭐 사야 해?"),
    ]

    for i, (label, prompt) in enumerate(chips):
        with chip_cols[i]:
            if st.button(label, key=f"chip_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt})

                inventory = load_json("inventory.json", [])
                appliance_data = load_json("appliances.json", [])
                timeline_data = load_json("timeline.json", [])
                schedule = load_json("schedule.json", [])

                response = get_chat_response(
                    prompt, inventory, appliance_data, timeline_data, schedule
                )
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
                st.rerun()

    spacer("0.5rem")

    # Chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Welcome message if empty
    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.markdown(
                "안녕하세요! 👋 HomeOS 가정 관리 도우미예요.\n\n"
                "궁금한 것이 있으면 편하게 물어보세요. "
                "한국어와 영어 모두 지원해요!\n\n"
                "예시:\n"
                '- "뭐 먼저 먹어야 해?"\n'
                '- "이번 주 일정 알려줘"\n'
                '- "What should I buy?"\n'
                '- "I\'m going on a trip this weekend"'
            )

    # Chat input
    user_input = st.chat_input("Type your message...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        inventory = load_json("inventory.json", [])
        appliance_data = load_json("appliances.json", [])
        timeline_data = load_json("timeline.json", [])
        schedule = load_json("schedule.json", [])

        response = get_chat_response(
            user_input, inventory, appliance_data, timeline_data, schedule
        )
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()

    # Clear chat
    spacer("1rem")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
