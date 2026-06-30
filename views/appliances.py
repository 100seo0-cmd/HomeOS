"""
Appliances page.
"""

import streamlit as st
from datetime import datetime
from utils.storage import load_json, save_json
from utils.ui_components import page_header, render_badge, spacer

DEFAULT_APPLIANCES = [
    {
        "name": "Air Conditioner",
        "icon": "❄️",
        "maintenance_type": "Filter cleaning",
        "maintenance_interval_days": 90,
        "last_maintenance": "",
    },
    {
        "name": "Washing Machine",
        "icon": "🫧",
        "maintenance_type": "Drum cleaning",
        "maintenance_interval_days": 30,
        "last_maintenance": "",
    },
    {
        "name": "Air Purifier",
        "icon": "🌬️",
        "maintenance_type": "Filter replacement",
        "maintenance_interval_days": 180,
        "last_maintenance": "",
    },
    {
        "name": "Water Purifier",
        "icon": "💧",
        "maintenance_type": "Filter replacement",
        "maintenance_interval_days": 180,
        "last_maintenance": "",
    },
    {
        "name": "Robot Vacuum",
        "icon": "🤖",
        "maintenance_type": "Dustbin & brush cleaning",
        "maintenance_interval_days": 14,
        "last_maintenance": "",
    },
]

def _days_since(date_str: str) -> int:
    if not date_str:
        return -1
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (datetime.now().date() - target).days
    except ValueError:
        return -1

def render():
    page_header("🔧", "Appliances", "Track maintenance schedules for your home appliances.")

    appliances = load_json("appliances.json", [])

    # Initialize with defaults if empty
    if not appliances:
        appliances = DEFAULT_APPLIANCES[:]
        save_json("appliances.json", appliances)

    # Add custom appliance
    with st.expander("➕ Add appliance", expanded=False):
        with st.form("add_appliance_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Appliance name")
            with col2:
                icon = st.text_input("Icon (emoji)", value="🔧")

            col3, col4 = st.columns(2)
            with col3:
                mtype = st.text_input("Maintenance type", placeholder="e.g. Filter cleaning")
            with col4:
                interval = st.number_input("Interval (days)", min_value=1, value=90)

            submitted = st.form_submit_button(
                "Add Appliance", type="primary", use_container_width=True
            )

            if submitted and name:
                new_appliance = {
                    "name": name.strip(),
                    "icon": icon.strip() or "🔧",
                    "maintenance_type": mtype.strip() or "Maintenance",
                    "maintenance_interval_days": interval,
                    "last_maintenance": "",
                }
                appliances.append(new_appliance)
                save_json("appliances.json", appliances)

                tl = load_json("timeline.json", [])
                tl.insert(0, {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "event": f"Added {name} to appliances",
                    "icon": icon.strip() or "🔧",
                    "category": "appliance",
                })
                save_json("timeline.json", tl)
                st.success(f"✅ {name} added!")
                st.rerun()

    spacer("0.8rem")

    # Appliance cards
    st.markdown(f"### 🏠 Your Appliances ({len(appliances)})")
    spacer("0.3rem")

    cols = st.columns(2)
    for idx, appliance in enumerate(appliances):
        col = cols[idx % 2]
        with col:
            a_name = appliance["name"]
            a_icon = appliance.get("icon", "🔧")
            a_mtype = appliance.get("maintenance_type", "Maintenance")
            a_interval = appliance.get("maintenance_interval_days", 90)
            a_last = appliance.get("last_maintenance", "")

            # Status
            if not a_last:
                badge_text = "No record"
                badge_level = "muted"
                status_text = "No maintenance recorded yet."
            else:
                elapsed = _days_since(a_last)
                remaining = a_interval - elapsed

                if remaining < 0:
                    overdue = abs(remaining)
                    badge_text = f"{overdue}d overdue"
                    badge_level = "urgent"
                    status_text = (
                        f"Last: {a_last} ({elapsed}d ago). "
                        f"Overdue by {overdue} day(s)."
                    )
                elif remaining <= 7:
                    badge_text = f"{remaining}d left"
                    badge_level = "warn"
                    status_text = (
                        f"Last: {a_last} ({elapsed}d ago). "
                        f"Due in {remaining} day(s)."
                    )
                else:
                    badge_text = f"{remaining}d left"
                    badge_level = "ok"
                    status_text = (
                        f"Last: {a_last} ({elapsed}d ago). "
                        f"Next in {remaining} day(s)."
                    )

            with st.container(border=True):
                badge_html = render_badge(badge_text, badge_level)
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; "
                    f"align-items:flex-start;'>"
                    f"<div>"
                    f"<span style='font-size:1.4rem; margin-right:0.4rem;'>{a_icon}</span>"
                    f"<span style='font-weight:600; color:#0F172A; "
                    f"font-size:0.95rem;'>{a_name}</span>"
                    f"</div>"
                    f"{badge_html}"
                    f"</div>"
                    f"<div style='margin-top:0.5rem; color:#64748B; font-size:0.82rem;'>"
                    f"{a_mtype} &middot; Every {a_interval} days"
                    f"</div>"
                    f"<div style='margin-top:0.3rem; color:#94A3B8; font-size:0.78rem;'>"
                    f"{status_text}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("✅ Done", key=f"maint_{idx}_{a_name}", use_container_width=True):
                        today_str = datetime.now().strftime("%Y-%m-%d")
                        appliances[idx]["last_maintenance"] = today_str
                        save_json("appliances.json", appliances)

                        tl = load_json("timeline.json", [])
                        tl.insert(0, {
                            "date": today_str,
                            "event": f"{a_name}: {a_mtype} completed",
                            "icon": a_icon,
                            "category": "maintenance",
                        })
                        save_json("timeline.json", tl)
                        st.rerun()
                with bcol2:
                    if st.button("🗑️ Remove", key=f"del_app_{idx}_{a_name}", use_container_width=True):
                        appliances.pop(idx)
                        save_json("appliances.json", appliances)
                        st.rerun()
