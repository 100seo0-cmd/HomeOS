"""
Timeline page.
"""

import streamlit as st
from datetime import datetime
from utils.storage import load_json, save_json
from utils.ui_components import page_header, render_badge, spacer

def render():
    page_header("📅", "Timeline", "A log of all activities and events in your home.")

    timeline = load_json("timeline.json", [])
    schedule = load_json("schedule.json", [])

    tab1, tab2 = st.tabs(["📜 Activity Log", "📅 Scheduled Events"])

    # ── Tab 1: Activity Log ────────────────────────────────────────
    with tab1:
        if not timeline:
            with st.container(border=True):
                st.markdown(
                    "<div style='text-align:center; padding:2rem;'>"
                    "<div style='font-size:2.5rem; margin-bottom:0.8rem;'>📜</div>"
                    "<div style='color:#64748B; font-size:0.95rem;'>"
                    "No activity yet. Start managing your home to see events here!"
                    "</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            # Group by date
            grouped = {}
            for entry in timeline:
                date = entry.get("date", "Unknown")
                if date not in grouped:
                    grouped[date] = []
                grouped[date].append(entry)

            sorted_dates = sorted(grouped.keys(), reverse=True)

            for date in sorted_dates:
                try:
                    dt = datetime.strptime(date, "%Y-%m-%d")
                    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                    display_date = f"{dt.strftime('%b %d, %Y')} ({weekdays[dt.weekday()]})"
                except ValueError:
                    display_date = date

                st.markdown(
                    f'<div class="timeline-date">{display_date}</div>',
                    unsafe_allow_html=True,
                )

                for entry in grouped[date]:
                    icon = entry.get("icon", "📌")
                    event = entry.get("event", "")
                    category = entry.get("category", "")

                    cat_colors = {
                        "inventory": "#3B82F6",
                        "maintenance": "#F59E0B",
                        "appliance": "#8B5CF6",
                        "schedule": "#10B981",
                    }
                    dot_color = cat_colors.get(category, "#94A3B8")

                    st.markdown(
                        f"<div style='display:flex; align-items:center; "
                        f"margin:0.3rem 0 0.3rem 1rem; padding:0.5rem 0.8rem; "
                        f"background:#FFFFFF; border-radius:12px; "
                        f"border:1px solid #F1F5F9;'>"
                        f"<div style='width:8px; height:8px; border-radius:50%; "
                        f"background:{dot_color}; margin-right:0.7rem; "
                        f"flex-shrink:0;'></div>"
                        f"<span style='font-size:1rem; margin-right:0.5rem;'>"
                        f"{icon}</span>"
                        f"<span class='timeline-event'>{event}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                spacer("0.5rem")

            # Clear timeline
            spacer("1rem")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🗑️ Clear Activity Log", use_container_width=True):
                    save_json("timeline.json", [])
                    st.rerun()

    # ── Tab 2: Scheduled Events ────────────────────────────────────
    with tab2:
        with st.expander("➕ Add scheduled event", expanded=False):
            with st.form("add_event_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    event_name = st.text_input("Event name")
                with col2:
                    event_date = st.date_input("Date")

                event_type = st.selectbox(
                    "Type",
                    ["general", "travel", "social", "shopping", "maintenance"],
                )

                submitted = st.form_submit_button(
                    "Add Event", type="primary", use_container_width=True
                )

                if submitted and event_name:
                    new_event = {
                        "event": event_name.strip(),
                        "date": event_date.strftime("%Y-%m-%d"),
                        "type": event_type,
                    }
                    schedule.append(new_event)
                    save_json("schedule.json", schedule)

                    tl = load_json("timeline.json", [])
                    tl.insert(0, {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "event": f"Scheduled: {event_name}",
                        "icon": "📅",
                        "category": "schedule",
                    })
                    save_json("timeline.json", tl)
                    st.success(f"✅ Event '{event_name}' added!")
                    st.rerun()

        spacer("0.5rem")

        if not schedule:
            with st.container(border=True):
                st.markdown(
                    "<div style='text-align:center; padding:2rem;'>"
                    "<div style='font-size:2.5rem; margin-bottom:0.8rem;'>📅</div>"
                    "<div style='color:#64748B; font-size:0.95rem;'>"
                    "No events scheduled. Add one above!"
                    "</div></div>",
                    unsafe_allow_html=True,
                )
        else:
            sorted_schedule = sorted(
                schedule, key=lambda x: x.get("date", "9999-12-31")
            )

            type_icons = {
                "travel": "✈️",
                "social": "👥",
                "shopping": "🛒",
                "maintenance": "🔧",
                "general": "📌",
            }

            for idx, event in enumerate(sorted_schedule):
                e_name = event["event"]
                e_date = event["date"]
                e_type = event.get("type", "general")
                e_icon = type_icons.get(e_type, "📌")

                try:
                    target = datetime.strptime(e_date, "%Y-%m-%d").date()
                    days = (target - datetime.now().date()).days
                except ValueError:
                    days = 9999

                if days < 0:
                    day_label = f"{abs(days)}d ago"
                    badge_level = "muted"
                elif days == 0:
                    day_label = "Today"
                    badge_level = "urgent"
                elif days == 1:
                    day_label = "Tomorrow"
                    badge_level = "warn"
                elif days <= 7:
                    day_label = f"In {days}d"
                    badge_level = "blue"
                else:
                    day_label = f"In {days}d"
                    badge_level = "muted"

                badge_html = render_badge(day_label, badge_level)

                with st.container(border=True):
                    st.markdown(
                        f"<div style='display:flex; justify-content:space-between; "
                        f"align-items:center;'>"
                        f"<div>"
                        f"<span style='font-size:1.2rem; margin-right:0.4rem;'>"
                        f"{e_icon}</span>"
                        f"<span style='font-weight:600; color:#0F172A; "
                        f"font-size:0.95rem;'>{e_name}</span>"
                        f"</div>"
                        f"{badge_html}"
                        f"</div>"
                        f"<div style='margin-top:0.4rem; color:#64748B; "
                        f"font-size:0.82rem;'>{e_date}</div>",
                        unsafe_allow_html=True,
                    )

                    if st.button("🗑️ Remove", key=f"del_evt_{idx}_{e_name}"):
                        schedule = [
                            s for s in schedule
                            if not (s["event"] == e_name and s["date"] == e_date)
                        ]
                        save_json("schedule.json", schedule)
                        st.rerun()
