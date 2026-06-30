"""
Inventory page.
"""

import streamlit as st
from datetime import datetime
from utils.storage import load_json, save_json
from utils.recommendation import generate_inventory_recommendation
from utils.ui_components import page_header, render_badge, render_blue_card, spacer

def _days_until(date_str: str) -> int:
    if not date_str:
        return 9999
    try:
        return (datetime.strptime(date_str, "%Y-%m-%d").date() - datetime.now().date()).days
    except ValueError:
        return 9999

def render():
    page_header("📦", "Inventory", "Track your food and household supplies.")

    inventory = load_json("inventory.json", [])

    # Add item
    with st.expander("➕ Add item", expanded=False):
        with st.form("add_item_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item name")
            with col2:
                quantity = st.text_input("Quantity", placeholder="e.g. 2, 500ml")

            col3, col4 = st.columns(2)
            with col3:
                exp_date = st.date_input("Expiration date (optional)", value=None)
            with col4:
                category = st.selectbox(
                    "Category",
                    ["🥗 Food", "🧴 Supplies", "🧹 Cleaning", "📦 Other"],
                )

            submitted = st.form_submit_button(
                "Add to Inventory", type="primary", use_container_width=True
            )

            if submitted and name:
                new_item = {
                    "name": name.strip(),
                    "quantity": quantity.strip() or "1",
                    "expiration_date": exp_date.strftime("%Y-%m-%d") if exp_date else "",
                    "category": category,
                    "added_date": datetime.now().strftime("%Y-%m-%d"),
                }
                inventory.append(new_item)
                save_json("inventory.json", inventory)

                tl = load_json("timeline.json", [])
                tl.insert(0, {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "event": f"Added {name} to inventory",
                    "icon": "📦",
                    "category": "inventory",
                })
                save_json("timeline.json", tl)
                st.success(f"✅ {name} added!")
                st.rerun()

    spacer("0.8rem")

    # Empty state
    if not inventory:
        with st.container(border=True):
            st.markdown(
                "<div style='text-align:center; padding:2rem;'>"
                "<div style='font-size:2.5rem; margin-bottom:0.8rem;'>📦</div>"
                "<div style='color:#64748B; font-size:0.95rem;'>"
                "No items yet. Add your first item above!</div></div>",
                unsafe_allow_html=True,
            )
        return

    st.markdown(f"### 🗂️ Your Items ({len(inventory)})")
    spacer("0.3rem")

    # Sort: expired/expiring first
    def sort_key(item):
        d = _days_until(item.get("expiration_date", ""))
        return d if d != 9999 else 99999

    sorted_inv = sorted(inventory, key=sort_key)

    cols = st.columns(2)
    for idx, item in enumerate(sorted_inv):
        col = cols[idx % 2]
        with col:
            item_name = item["name"]
            qty = item.get("quantity", "1")
            exp = item.get("expiration_date", "")
            category = item.get("category", "📦 Other")
            cat_icon = category.split(" ")[0] if category else "📦"

            # Badge text
            if exp:
                days = _days_until(exp)
                if days < 0:
                    badge_text = f"Expired {abs(days)}d ago"
                    badge_level = "urgent"
                elif days == 0:
                    badge_text = "Expires today"
                    badge_level = "urgent"
                elif days == 1:
                    badge_text = "D-1"
                    badge_level = "warn"
                elif days <= 3:
                    badge_text = f"D-{days}"
                    badge_level = "warn"
                else:
                    badge_text = f"D-{days}"
                    badge_level = "ok"
            else:
                badge_text = "No expiration"
                badge_level = "muted"

            # Use st.container to avoid broken HTML
            with st.container(border=True):
                badge_html = render_badge(badge_text, badge_level)
                st.markdown(
                    f"<div style='display:flex; justify-content:space-between; "
                    f"align-items:flex-start;'>"
                    f"<div>"
                    f"<span style='font-size:1.2rem; margin-right:0.4rem;'>{cat_icon}</span>"
                    f"<span style='font-weight:600; color:#0F172A; "
                    f"font-size:0.95rem;'>{item_name}</span>"
                    f"</div>"
                    f"{badge_html}"
                    f"</div>"
                    f"<div style='margin-top:0.5rem; color:#64748B; font-size:0.82rem;'>"
                    f"Quantity: {qty}"
                    f"{'&nbsp;&nbsp;&middot;&nbsp;&nbsp;Exp: ' + exp if exp else ''}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if st.button("🗑️ Remove", key=f"del_{idx}_{item_name}"):
                    inventory.remove(item)
                    save_json("inventory.json", inventory)
                    tl = load_json("timeline.json", [])
                    tl.insert(0, {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "event": f"Removed {item_name} from inventory",
                        "icon": "🗑️",
                        "category": "inventory",
                    })
                    save_json("timeline.json", tl)
                    st.rerun()

    spacer("1.5rem")

    # AI Recommendation
    st.markdown("### 🤖 AI Recommendation")
    spacer("0.3rem")

    rec_text = generate_inventory_recommendation(inventory)
    render_blue_card(
        f"<div style='font-size:0.9rem; line-height:1.7; color:#1E40AF; "
        f"white-space:pre-line;'>{rec_text}</div>"
    )
