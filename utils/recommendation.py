"""
recommendation.py
-----------------
가정 관리 추천 로직 (날씨, 인벤토리, 가전, 일정 기반).
"""

from datetime import datetime, timedelta
import random

def get_weather() -> dict:
    """시뮬레이션 날씨 데이터를 반환합니다."""
    conditions = ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"]
    random.seed(datetime.now().strftime("%Y-%m-%d"))
    today_cond = random.choice(conditions)

    random.seed(datetime.now().strftime("%Y-%m-%d") + "tmr")
    tmr_cond = random.choice(conditions)

    return {
        "today": {"condition": today_cond, "temp": random.randint(18, 32), "humidity": random.randint(40, 80)},
        "tomorrow": {"condition": tmr_cond, "temp": random.randint(18, 32), "humidity": random.randint(40, 80)},
        "week_outlook": "Mixed conditions expected throughout the week.",
    }

def _days_until(date_str: str) -> int:
    if not date_str:
        return 9999
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (target - datetime.now().date()).days
    except ValueError:
        return 9999

def _days_since(date_str: str) -> int:
    if not date_str:
        return 9999
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (datetime.now().date() - target).days
    except ValueError:
        return 9999

def generate_recommendations(inventory: list, appliances: list, schedule: list) -> list:
    """추천 목록을 생성합니다. 각 항목은 dict(icon, title, detail, reasons)."""
    recs = []
    weather = get_weather()

    # ── 유통기한 임박 식재료 ────────────────────────────────────────
    for item in inventory:
        exp = item.get("expiration_date")
        if not exp:
            continue
        days = _days_until(exp)
        if days < 0:
            recs.append({
                "icon": "⚠️",
                "title": f"{item['name']} has expired.",
                "detail": f"Expired {abs(days)} day(s) ago. Please check and discard if needed.",
                "reasons": [
                    f"Expiration date was {exp}.",
                    f"It has been {abs(days)} day(s) since expiration.",
                    "Consuming expired food may be unsafe.",
                ],
            })
        elif days == 0:
            recs.append({
                "icon": "🔴",
                "title": f"{item['name']} expires today.",
                "detail": "Use it today to avoid waste.",
                "reasons": [
                    f"Expiration date is today ({exp}).",
                    "This is a perishable item.",
                    "Using it now prevents food waste.",
                ],
            })
        elif days <= 3:
            recs.append({
                "icon": "🟡",
                "title": f"{item['name']} expires in {days} day(s).",
                "detail": "Plan to use it soon.",
                "reasons": [
                    f"Expiration date is {exp} ({days} days away).",
                    "Planning meals around this item reduces waste.",
                ],
            })

    # ── 가전 유지보수 ──────────────────────────────────────────────
    for a in appliances:
        last = a.get("last_maintenance", "")
        interval = a.get("maintenance_interval_days", 90)
        if last and _days_since(last) > interval:
            overdue = _days_since(last) - interval
            recs.append({
                "icon": a.get("icon", "🔧"),
                "title": f"{a['name']} maintenance is overdue.",
                "detail": f"{a.get('maintenance_type', 'Maintenance')} is {overdue} day(s) overdue.",
                "reasons": [
                    f"Last maintenance was on {last} ({_days_since(last)} days ago).",
                    f"Recommended interval is every {interval} days.",
                    "Regular maintenance extends appliance lifespan.",
                ],
            })

    # ── 일정 기반 ──────────────────────────────────────────────────
    for s in schedule:
        days = _days_until(s["date"])
        if days == 0:
            recs.append({
                "icon": "📅",
                "title": f"Today: {s['event']}",
                "detail": "You have an event scheduled for today.",
                "reasons": [f"Scheduled event: {s['event']} on {s['date']}."],
            })
        elif days == 1:
            recs.append({
                "icon": "📅",
                "title": f"Tomorrow: {s['event']}",
                "detail": "Prepare for tomorrow's event.",
                "reasons": [f"Scheduled event: {s['event']} on {s['date']}."],
            })

    # ── 날씨 기반 ──────────────────────────────────────────────────
    if weather["tomorrow"]["condition"].lower() in ("rainy", "rain"):
        recs.append({
            "icon": "🧺",
            "title": "Do laundry today.",
            "detail": "Rain is expected tomorrow, so today is better for drying clothes.",
            "reasons": [
                f"Tomorrow's forecast: {weather['tomorrow']['condition']}.",
                "Clothes dry best on clear days.",
            ],
        })

    if not recs:
        recs.append({
            "icon": "✨",
            "title": "Everything looks great!",
            "detail": "No urgent tasks right now. Enjoy your day.",
            "reasons": ["No items expiring soon.", "All appliances are up to date.", "No imminent events."],
        })

    return recs

def generate_summary(inventory: list, appliances: list, schedule: list) -> str:
    """가정 현황 요약 문자열을 생성합니다."""
    lines = []
    weather = get_weather()

    lines.append(f"🌤️ Today's weather: {weather['today']['condition']}, {weather['today']['temp']}°C")

    expiring = [i for i in inventory if i.get("expiration_date") and _days_until(i["expiration_date"]) <= 3]
    if expiring:
        names = ", ".join(i["name"] for i in expiring)
        lines.append(f"🥗 Items to use soon: {names}")

    overdue = [
        a for a in appliances
        if a.get("last_maintenance") and _days_since(a["last_maintenance"]) > a.get("maintenance_interval_days", 90)
    ]
    if overdue:
        names = ", ".join(a["name"] for a in overdue)
        lines.append(f"🔧 Maintenance needed: {names}")

    upcoming = [s for s in schedule if 0 <= _days_until(s["date"]) <= 3]
    if upcoming:
        events = ", ".join(s["event"] for s in upcoming)
        lines.append(f"📅 Coming up: {events}")

    if not expiring and not overdue and not upcoming:
        lines.append("✅ Your home is running smoothly. Nothing urgent!")

    return "\n\n".join(lines)

def generate_inventory_recommendation(inventory: list) -> str:
    """인벤토리 기반 간단 추천을 반환합니다."""
    perishables = [i for i in inventory if i.get("expiration_date")]
    perishables.sort(key=lambda x: _days_until(x["expiration_date"]))

    if not perishables:
        return "No perishable items tracked. Add items with expiration dates for better recommendations!"

    lines = ["Here's what to use first:\n"]
    for item in perishables[:5]:
        days = _days_until(item["expiration_date"])
        if days < 0:
            lines.append(f"⚠️ {item['name']}: Expired {abs(days)} day(s) ago")
        elif days == 0:
            lines.append(f"🔴 {item['name']}: Expires today")
        elif days <= 3:
            lines.append(f"🟡 {item['name']}: {days} day(s) left")
        else:
            lines.append(f"🟢 {item['name']}: {days} day(s) left")

    return "\n".join(lines)
