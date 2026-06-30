"""
ui_components.py
----------------
재사용 가능한 UI 컴포넌트 헬퍼 함수들.
"""

import streamlit as st

def card_start(extra_class: str = "") -> str:
    """카드 HTML 열기 태그를 반환합니다."""
    cls = f"homeos-card {extra_class}".strip()
    return f'<div class="{cls}">'

def card_end() -> str:
    """카드 HTML 닫기 태그를 반환합니다."""
    return "</div>"

def render_card(content_html: str, extra_class: str = ""):
    """완성된 카드를 렌더링합니다."""
    cls = f"homeos-card {extra_class}".strip()
    st.markdown(f'<div class="{cls}">{content_html}</div>', unsafe_allow_html=True)

def render_blue_card(content_html: str):
    """파란 틴트 카드를 렌더링합니다."""
    st.markdown(
        f'<div class="homeos-card-blue">{content_html}</div>',
        unsafe_allow_html=True,
    )

def render_badge(text: str, level: str = "muted") -> str:
    """배지 HTML을 반환합니다. level: urgent, warn, ok, muted, blue"""
    return f'<span class="badge badge-{level}">{text}</span>'

def page_header(icon: str, title: str, subtitle: str = ""):
    """페이지 헤더를 렌더링합니다."""
    sub_html = ""
    if subtitle:
        sub_html = f'<p class="text-muted" style="margin-top:0.2rem;">{subtitle}</p>'
    st.markdown(
        f"""
        <div style="margin-bottom: 1.5rem;">
            <h1>{icon} {title}</h1>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

def spacer(height: str = "1rem"):
    """수직 여백을 추가합니다."""
    st.markdown(f'<div style="height: {height};"></div>', unsafe_allow_html=True)
