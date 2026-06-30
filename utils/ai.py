"""
ai.py
-----
HomeOS AI 에이전트 모듈 (로컬 규칙 기반).
외부 API 없이 동작하며, 인벤토리/가전/일정/타임라인/날씨를 분석하여
자연어 응답을 생성합니다.

한국어와 영어 질문을 모두 지원합니다.
"""

import os
import re
from datetime import datetime, timedelta

from utils.recommendation import (
    generate_recommendations,
    generate_summary,
    generate_inventory_recommendation,
    get_weather,
)

# ═══════════════════════════════════════════════════════════════════
#  헬퍼 함수
# ═══════════════════════════════════════════════════════════════════

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

def _is_korean(text: str) -> bool:
    """텍스트에 한글이 포함되어 있으면 True를 반환합니다."""
    return bool(re.search(r"[가-힣]", text))

def _weekday_name(date_str: str, korean: bool = False) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if korean:
            names = ["월", "화", "수", "목", "금", "토", "일"]
            return names[dt.weekday()]
        return dt.strftime("%A")
    except ValueError:
        return ""

def _format_date_display(date_str: str, korean: bool = False) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if korean:
            return f"{dt.month}월 {dt.day}일 ({_weekday_name(date_str, True)})"
        return f"{dt.strftime('%b %d')} ({_weekday_name(date_str, False)})"
    except ValueError:
        return date_str

# ═══════════════════════════════════════════════════════════════════
#  의도 감지 (한국어 + 영어)
# ═══════════════════════════════════════════════════════════════════

def _detect_intent(msg: str) -> str:
    """사용자 메시지에서 의도를 파악합니다."""
    m = msg.lower().strip()

    # ── 이번 주 일정 ────────────────────────────────────────────────
    if any(kw in m for kw in [
        "이번 주", "이번주", "금주", "주간 일정", "주간일정",
        "이번 주 뭐", "이번주 뭐", "무슨 일정", "뭐 있어",
        "뭐있어", "일정 알려", "일정알려", "스케줄",
        "this week", "coming up", "upcoming", "week ahead",
        "what's on", "what is on", "what's happening",
        "any plans", "any events", "schedule this week",
        "weekly schedule", "week plan",
    ]):
        return "weekly_schedule"

    # ── 여행/출장 ───────────────────────────────────────────────────
    if any(kw in m for kw in [
        "여행", "출장", "떠나", "놀러", "trip", "travel",
        "traveling", "travelling", "vacation", "weekend trip",
        "going away", "leaving home", "be away", "out of town",
    ]):
        return "travel"

    # ── 음식/뭐 먹지 ───────────────────────────────────────────────
    if any(kw in m for kw in [
        "뭐 먹", "뭐먹", "먼저 먹", "먼저먹", "먹어야",
        "소비", "유통기한", "식재료", "요리",
        "레시피", "반찬", "메뉴", "식사",
        "eat first", "what to eat", "what should i eat",
        "cook", "recipe", "meal", "consume", "use first",
        "expiring food", "ingredients",
    ]):
        return "eat_first"

    # ── 가전 / 유지보수 ────────────────────────────────────────────
    if any(kw in m for kw in [
        "가전", "에어컨", "세탁기", "공기청정기", "정수기",
        "필터", "청소", "유지보수", "관리", "점검",
        "appliance", "air conditioner", "aircon", "ac",
        "washing machine", "air purifier", "water purifier",
        "filter", "maintenance", "clean",
    ]):
        return "appliances"

    # ── 장보기 / 구매 ──────────────────────────────────────────────
    if any(kw in m for kw in [
        "뭐 사", "뭐사", "장보", "장봐", "사야 할",
        "사야할", "구매", "쇼핑", "마트", "필요한 것",
        "필요한것", "부족", "떨어",
        "buy", "shop", "grocery", "groceries", "need to buy",
        "shopping list", "run out", "running low", "supplies",
        "restock", "pick up",
    ]):
        return "shopping"

    # ── 날씨 ────────────────────────────────────────────────────────
    if any(kw in m for kw in [
        "날씨", "비", "우산", "기온", "습도", "덥", "춥",
        "weather", "rain", "sunny", "forecast", "temperature",
        "humid", "hot", "cold",
    ]):
        return "weather"

    # ── 빨래 ────────────────────────────────────────────────────────
    if any(kw in m for kw in [
        "빨래", "세탁", "건조", "laundry", "wash clothes",
        "dry clothes", "hang clothes",
    ]):
        return "laundry"

    # ── 인사 ────────────────────────────────────────────────────────
    greeting_exact = [
        "안녕", "안녕하세요", "하이", "헬로",
        "hello", "hi", "hey",
        "good morning", "good evening", "good afternoon",
    ]

    if m in greeting_exact:
        return "greeting"

    if any(kw in m for kw in ["반가", "좋은 아침", "좋은 저녁"]):
        return "greeting"

    # ── 도움말 ──────────────────────────────────────────────────────
    if any(kw in m for kw in [
        "도움", "뭐 할 수", "뭐할수", "기능", "사용법",
        "help", "what can you do", "what do you do", "how to use",
    ]):
        return "help"

    return "general"

# ═══════════════════════════════════════════════════════════════════
#  응답 생성기 (의도별)
# ═══════════════════════════════════════════════════════════════════

def _respond_weekly_schedule(
    korean: bool,
    inventory: list,
    appliances: list,
    timeline: list,
    schedule: list,
) -> str:
    """이번 주 일정 + 가정 관리 제안을 반환합니다."""
    today = datetime.now().date()
    # 이번 주: 오늘부터 일요일까지 (최소 7일)
    days_to_sunday = 6 - today.weekday()
    if days_to_sunday < 0:
        days_to_sunday += 7
    end_of_week = today + timedelta(days=max(days_to_sunday, 6))

    upcoming = [
        s for s in schedule
        if 0 <= _days_until(s["date"]) <= (end_of_week - today).days
    ]
    upcoming.sort(key=lambda x: x["date"])

    weather = get_weather()

    if korean:
        lines = ["## 📅 이번 주 일정\n"]

        if not upcoming:
            lines.append("이번 주에는 등록된 일정이 없습니다.\n")
            lines.append("여유로운 한 주가 될 것 같아요! 😊\n")
        else:
            for evt in upcoming:
                days = _days_until(evt["date"])
                date_disp = _format_date_display(evt["date"], True)
                if days == 0:
                    tag = "**오늘**"
                elif days == 1:
                    tag = "**내일**"
                else:
                    tag = f"**{days}일 후**"
                type_icon = {
                    "travel": "✈️",
                    "social": "👥",
                    "shopping": "🛒",
                }.get(evt.get("type", ""), "📌")
                lines.append(f"- {type_icon} **{date_disp}** ({tag}): {evt['event']}")
            lines.append("")

        # 가정 관리 제안
        lines.append("---\n")
        lines.append("### 💡 이번 주 가정 관리 팁\n")

        suggestions = []

        # 유통기한 임박 아이템
        expiring = [
            item for item in inventory
            if item.get("expiration_date")
            and 0 <= _days_until(item["expiration_date"]) <= (end_of_week - today).days
        ]
        if expiring:
            names = ", ".join(f"**{item['name']}**" for item in expiring)
            suggestions.append(f"🥗 이번 주 안에 소비하면 좋은 식재료: {names}")

        # 가전 유지보수
        for a in appliances:
            interval = a.get("maintenance_interval_days", 90)
            last = a.get("last_maintenance", "")
            if last and _days_since(last) > interval:
                suggestions.append(
                    f"{a.get('icon', '🔧')} **{a['name']}** {a.get('maintenance_type', '관리')}가 "
                    f"예정일을 {_days_since(last) - interval}일 지났어요."
                )

        # 날씨 기반
        if weather["tomorrow"]["condition"].lower() in ["rainy", "rain"]:
            suggestions.append("🧺 내일 비 예보가 있으니, 빨래는 오늘 하시는 게 좋아요.")

        # 여행 관련
        has_travel = any(
            s.get("type") == "travel" and 0 <= _days_until(s["date"]) <= 7
            for s in schedule
        )
        if has_travel:
            suggestions.append("✈️ 여행 전에 음식물 쓰레기를 처리하고, 냉장고 정리를 해두세요.")

        if suggestions:
            for s in suggestions:
                lines.append(f"- {s}")
        else:
            lines.append("- ✨ 특별히 긴급한 사항은 없어요. 편안한 한 주 보내세요!")

        return "\n\n".join(lines)

    else:
        # ── 영어 ────────────────────────────────────────────────────
        lines = ["## 📅 This Week's Schedule\n"]

        if not upcoming:
            lines.append("No events scheduled for this week.\n")
            lines.append("Looks like a relaxed week ahead! 😊\n")
        else:
            for evt in upcoming:
                days = _days_until(evt["date"])
                date_disp = _format_date_display(evt["date"], False)
                if days == 0:
                    tag = "**today**"
                elif days == 1:
                    tag = "**tomorrow**"
                else:
                    tag = f"**in {days} days**"
                type_icon = {
                    "travel": "✈️",
                    "social": "👥",
                    "shopping": "🛒",
                }.get(evt.get("type", ""), "📌")
                lines.append(f"- {type_icon} **{date_disp}** ({tag}): {evt['event']}")
            lines.append("")

        lines.append("---\n")
        lines.append("### 💡 Household Tips for This Week\n")

        suggestions = []

        expiring = [
            item for item in inventory
            if item.get("expiration_date")
            and 0 <= _days_until(item["expiration_date"]) <= (end_of_week - today).days
        ]
        if expiring:
            names = ", ".join(f"**{item['name']}**" for item in expiring)
            suggestions.append(f"🥗 Use these before they expire this week: {names}")

        for a in appliances:
            interval = a.get("maintenance_interval_days", 90)
            last = a.get("last_maintenance", "")
            if last and _days_since(last) > interval:
                overdue = _days_since(last) - interval
                suggestions.append(
                    f"{a.get('icon', '🔧')} **{a['name']}** {a.get('maintenance_type', 'maintenance')} "
                    f"is {overdue} day(s) overdue."
                )

        if weather["tomorrow"]["condition"].lower() in ["rainy", "rain"]:
            suggestions.append("🧺 Rain is expected tomorrow. Today is a good day for laundry.")

        has_travel = any(
            s.get("type") == "travel" and 0 <= _days_until(s["date"]) <= 7
            for s in schedule
        )
        if has_travel:
            suggestions.append("✈️ Clear out perishables and take out the trash before your trip.")

        if suggestions:
            for s in suggestions:
                lines.append(f"- {s}")
        else:
            lines.append("- ✨ Nothing urgent this week. Enjoy your time!")

        return "\n\n".join(lines)

def _respond_travel(
    korean: bool,
    inventory: list,
    appliances: list,
    schedule: list,
) -> str:
    """여행/출장 관련 체크리스트를 반환합니다."""
    expiring = [
        item for item in inventory
        if item.get("expiration_date") and _days_until(item["expiration_date"]) <= 5
    ]

    if korean:
        lines = ["## ✈️ 여행 준비 체크리스트\n"]
        lines.append("떠나기 전에 아래 사항들을 확인해보세요!\n")

        # 냉장고 정리
        lines.append("### 🥗 냉장고 정리\n")
        if expiring:
            for item in expiring:
                days = _days_until(item["expiration_date"])
                if days <= 0:
                    lines.append(f"- ⚠️ **{item['name']}**: 이미 유통기한이 지났어요. 확인 후 처리해주세요.")
                else:
                    lines.append(f"- **{item['name']}**: {days}일 남았어요. 출발 전에 소비하세요.")
        else:
            lines.append("- ✅ 유통기한이 임박한 식재료는 없어요.")
        lines.append("")

        # 장보기
        lines.append("### 🛒 장보기\n")
        lines.append("- 여행 전에는 식재료 구매를 미루는 것이 좋아요.")
        lines.append("- 돌아온 후에 필요한 것만 구매하면 낭비를 줄일 수 있어요.\n")

        # 쓰레기
        lines.append("### 🗑️ 쓰레기 처리\n")
        lines.append("- 음식물 쓰레기를 반드시 비워주세요.")
        lines.append("- 일반 쓰레기도 출발 전에 버려두면 냄새 걱정이 없어요.\n")

        # 가전
        lines.append("### 🔌 가전 점검\n")
        lines.append("- 에어컨: 외출 모드로 설정하거나 꺼주세요.")
        lines.append("- 세탁기: 드럼 안에 빨래가 없는지 확인하세요.")
        lines.append("- 정수기/공기청정기: 전원을 끄거나 절전 모드로 전환하세요.\n")

        lines.append("---\n")
        lines.append("좋은 여행 되세요! 🌟 집 걱정은 돌아와서 해도 늦지 않아요.")

        return "\n\n".join(lines)

    else:
        lines = ["## ✈️ Pre-Trip Home Checklist\n"]
        lines.append("Here's what to take care of before you leave!\n")

        lines.append("### 🥗 Refrigerator\n")
        if expiring:
            for item in expiring:
                days = _days_until(item["expiration_date"])
                if days <= 0:
                    lines.append(f"- ⚠️ **{item['name']}**: Already expired. Please check and discard if needed.")
                else:
                    lines.append(f"- **{item['name']}**: Expires in {days} day(s). Try to use it before you go.")
        else:
            lines.append("- ✅ No items expiring soon. You're all set.")
        lines.append("")

        lines.append("### 🛒 Grocery Shopping\n")
        lines.append("- Hold off on buying groceries until you return.")
        lines.append("- This way, nothing goes to waste while you're away.\n")

        lines.append("### 🗑️ Trash\n")
        lines.append("- Empty the food waste bin before leaving.")
        lines.append("- Take out the general trash too, so nothing sits.\n")

        lines.append("### 🔌 Appliances\n")
        lines.append("- Air conditioner: Switch to away mode or turn off.")
        lines.append("- Washing machine: Make sure the drum is empty.")
        lines.append("- Water/air purifier: Turn off or set to power-saving mode.\n")

        lines.append("---\n")
        lines.append("Have a wonderful trip! 🌟 Your home will be just fine.")

        return "\n\n".join(lines)

def _respond_eat_first(korean: bool, inventory: list) -> str:
    """유통기한이 가까운 아이템 우선 추천 + 간단 요리 제안."""
    perishables = [
        item for item in inventory if item.get("expiration_date")
    ]
    perishables.sort(key=lambda x: _days_until(x["expiration_date"]))

    # 간단 레시피 매핑
    recipe_map_kr = {
        ("egg", "bread"): "🍳 달걀과 빵으로 **프렌치 토스트**나 **달걀 샌드위치**를 만들어보세요.",
        ("egg", "carrot"): "🥕 달걀과 당근으로 **달걀말이** 또는 **볶음밥**을 추천해요.",
        ("milk", "egg"): "🥛 우유와 달걀로 **스크램블 에그**나 **푸딩**을 만들 수 있어요.",
        ("milk", "bread"): "🍞 우유와 빵으로 간단한 **밀크 토스트**는 어떨까요?",
        ("milk",): "🥛 우유로 **스무디**나 **시리얼**을 곁들여보세요.",
        ("egg",): "🍳 달걀 하나로 **달걀 프라이**나 **삶은 달걀**이면 충분해요.",
        ("bread",): "🍞 빵은 **토스트**에 잼이나 버터를 발라 간단하게 드세요.",
        ("carrot",): "🥕 당근은 **당근 스틱**으로 간식 삼아 드셔도 좋아요.",
    }
    recipe_map_en = {
        ("egg", "bread"): "🍳 Try making **French toast** or an **egg sandwich** with your eggs and bread.",
        ("egg", "carrot"): "🥕 How about a **vegetable omelette** or **fried rice** with eggs and carrots?",
        ("milk", "egg"): "🥛 Make **scrambled eggs** with a splash of milk, or try a simple **pudding**.",
        ("milk", "bread"): "🍞 **Milk toast** is a quick and comforting option.",
        ("milk",): "🥛 Use the milk for a **smoothie** or with cereal.",
        ("egg",): "🍳 A simple **fried egg** or **boiled egg** is always a good choice.",
        ("bread",): "🍞 Toast the bread with jam or butter for a quick snack.",
        ("carrot",): "🥕 Enjoy the carrots as **carrot sticks** with a dip.",
    }

    inv_names = {item["name"].lower() for item in inventory}

    def _find_recipe(korean_mode: bool) -> str:
        rmap = recipe_map_kr if korean_mode else recipe_map_en
        for combo, suggestion in rmap.items():
            if all(name in inv_names for name in combo):
                return suggestion
        return ""

    if korean:
        lines = ["## 🍽️ 먼저 드시면 좋은 식재료\n"]

        if not perishables:
            lines.append("유통기한이 있는 식재료가 없어요.")
            lines.append("재고를 추가하면 더 구체적인 추천을 드릴 수 있어요! 😊")
            return "\n\n".join(lines)

        lines.append("유통기한이 가까운 순서대로 정리해드릴게요.\n")

        for item in perishables:
            days = _days_until(item["expiration_date"])
            name = item["name"]
            qty = item["quantity"]

            if days < 0:
                lines.append(f"- ⚠️ **{name}** ({qty}): 유통기한이 {abs(days)}일 전에 지났어요. 상태를 확인해주세요.")
            elif days == 0:
                lines.append(f"- 🔴 **{name}** ({qty}): **오늘**이 유통기한이에요!")
            elif days == 1:
                lines.append(f"- 🟠 **{name}** ({qty}): **내일**까지에요. 오늘 드시는 걸 추천해요.")
            elif days <= 3:
                lines.append(f"- 🟡 **{name}** ({qty}): {days}일 남았어요. 이번 주 안에 드세요.")
            else:
                lines.append(f"- 🟢 **{name}** ({qty}): {days}일 남아서 여유 있어요.")

        recipe = _find_recipe(True)
        if recipe:
            lines.append("")
            lines.append("---\n")
            lines.append("### 🧑‍🍳 오늘의 간단 요리 제안\n")
            lines.append(recipe)

        return "\n\n".join(lines)

    else:
        lines = ["## 🍽️ What to Eat First\n"]

        if not perishables:
            lines.append("You don't have any perishable items tracked.")
            lines.append("Add items with expiration dates for better recommendations! 😊")
            return "\n\n".join(lines)

        lines.append("Here are your items sorted by expiration date.\n")

        for item in perishables:
            days = _days_until(item["expiration_date"])
            name = item["name"]
            qty = item["quantity"]

            if days < 0:
                lines.append(f"- ⚠️ **{name}** ({qty}): Expired {abs(days)} day(s) ago. Please check it.")
            elif days == 0:
                lines.append(f"- 🔴 **{name}** ({qty}): Expires **today**!")
            elif days == 1:
                lines.append(f"- 🟠 **{name}** ({qty}): Expires **tomorrow**. Best to use today.")
            elif days <= 3:
                lines.append(f"- 🟡 **{name}** ({qty}): {days} days left. Use this week.")
            else:
                lines.append(f"- 🟢 **{name}** ({qty}): {days} days left. No rush.")

        recipe = _find_recipe(False)
        if recipe:
            lines.append("")
            lines.append("---\n")
            lines.append("### 🧑‍🍳 Quick Meal Idea\n")
            lines.append(recipe)

        return "\n\n".join(lines)

def _respond_appliances(korean: bool, appliances: list) -> str:
    """가전 유지보수 현황을 반환합니다."""
    if korean:
        lines = ["## 🛠 가전 유지보수 현황\n"]

        if not appliances:
            lines.append("등록된 가전이 없어요. 가전 페이지에서 추가해보세요!")
            return "\n\n".join(lines)

        overdue_list = []
        ok_list = []

        for a in appliances:
            icon = a.get("icon", "🔧")
            name = a["name"]
            mtype = a.get("maintenance_type", "관리")
            last = a.get("last_maintenance", "")
            interval = a.get("maintenance_interval_days", 90)

            if not last:
                overdue_list.append(f"- {icon} **{name}**: 유지보수 기록이 없어요. 점검이 필요합니다.")
                continue

            elapsed = _days_since(last)
            overdue = elapsed - interval
            last_disp = _format_date_display(last, True)

            if overdue > 0:
                overdue_list.append(
                    f"- {icon} **{name}** ({mtype})\n"
                    f"  - 마지막 관리: {last_disp} ({elapsed}일 전)\n"
                    f"  - 권장 주기: {interval}일마다\n"
                    f"  - ⚠️ **{overdue}일 초과**되었어요."
                )
            elif overdue > -7:
                overdue_list.append(
                    f"- {icon} **{name}** ({mtype})\n"
                    f"  - 마지막 관리: {last_disp} ({elapsed}일 전)\n"
                    f"  - 🟡 {abs(overdue)}일 후 관리가 필요해요."
                )
            else:
                ok_list.append(
                    f"- {icon} **{name}**: ✅ 다음 {mtype}까지 {abs(overdue)}일 남았어요."
                )

        if overdue_list:
            lines.append("### ⚠️ 관리가 필요한 가전\n")
            lines.extend(overdue_list)
            lines.append("")

        if ok_list:
            lines.append("### ✅ 정상 상태\n")
            lines.extend(ok_list)

        if overdue_list:
            lines.append("\n---\n")
            lines.append("가전 페이지에서 유지보수 완료 버튼을 누르면 기록이 업데이트됩니다. 😊")

        return "\n\n".join(lines)

    else:
        lines = ["## 🛠 Appliance Maintenance Status\n"]

        if not appliances:
            lines.append("No appliances registered. Add them on the Appliances page!")
            return "\n\n".join(lines)

        overdue_list = []
        ok_list = []

        for a in appliances:
            icon = a.get("icon", "🔧")
            name = a["name"]
            mtype = a.get("maintenance_type", "maintenance")
            last = a.get("last_maintenance", "")
            interval = a.get("maintenance_interval_days", 90)

            if not last:
                overdue_list.append(f"- {icon} **{name}**: No maintenance record found. Please check soon.")
                continue

            elapsed = _days_since(last)
            overdue = elapsed - interval
            last_disp = _format_date_display(last, False)

            if overdue > 0:
                overdue_list.append(
                    f"- {icon} **{name}** ({mtype})\n"
                    f"  - Last done: {last_disp} ({elapsed} days ago)\n"
                    f"  - Recommended: every {interval} days\n"
                    f"  - ⚠️ **{overdue} days overdue**"
                )
            elif overdue > -7:
                overdue_list.append(
                    f"- {icon} **{name}** ({mtype})\n"
                    f"  - Last done: {last_disp} ({elapsed} days ago)\n"
                    f"  - 🟡 Due in {abs(overdue)} day(s)"
                )
            else:
                ok_list.append(
                    f"- {icon} **{name}**: ✅ Next {mtype} in {abs(overdue)} days."
                )

        if overdue_list:
            lines.append("### ⚠️ Needs Attention\n")
            lines.extend(overdue_list)
            lines.append("")

        if ok_list:
            lines.append("### ✅ All Good\n")
            lines.extend(ok_list)

        if overdue_list:
            lines.append("\n---\n")
            lines.append("You can mark maintenance as completed on the Appliances page. 😊")

        return "\n\n".join(lines)

def _respond_shopping(korean: bool, inventory: list) -> str:
    """장보기 추천 목록을 반환합니다."""
    buy_list = []

    for item in inventory:
        name = item["name"]
        qty = item.get("quantity", "")
        exp = item.get("expiration_date")

        # 유통기한 임박 아이템 (곧 교체 필요)
        if exp and _days_until(exp) <= 2:
            if korean:
                buy_list.append(("🔴", name, "유통기한이 임박해서 곧 새로 구매해야 해요."))
            else:
                buy_list.append(("🔴", name, "Expiring soon; you'll need a replacement."))

        # 소모품 부족
        if name.lower() in ["toilet paper", "laundry detergent", "tissue", "paper towel"]:
            try:
                qty_num = int("".join(filter(str.isdigit, str(qty))) or "0")
            except ValueError:
                qty_num = 0
            if 0 < qty_num <= 3:
                if korean:
                    buy_list.append(("🟡", name, f"현재 {qty} 남았어요. 곧 떨어질 수 있어요."))
                else:
                    buy_list.append(("🟡", name, f"Only {qty} remaining. May run out soon."))

    if korean:
        lines = ["## 🛒 장보기 추천 목록\n"]

        if not buy_list:
            lines.append("지금은 급하게 살 것이 없어 보여요! ✅\n")
            lines.append("재고가 넉넉한 편이니, 다음 정기 장보기 때 확인해보세요. 😊")
            return "\n\n".join(lines)

        lines.append("현재 재고를 분석한 결과, 다음 아이템들을 추천드려요.\n")
        for priority, name, reason in buy_list:
            lines.append(f"- {priority} **{name}**")
            lines.append(f"  - {reason}")
        lines.append("")
        lines.append("---\n")
        lines.append("장을 볼 때 참고해주세요! 🛍️")
        return "\n\n".join(lines)

    else:
        lines = ["## 🛒 Shopping Recommendations\n"]

        if not buy_list:
            lines.append("Your supplies look good for now! ✅\n")
            lines.append("Nothing urgent to buy. Check again during your next regular shopping trip. 😊")
            return "\n\n".join(lines)

        lines.append("Based on your current inventory, here's what you might need.\n")
        for priority, name, reason in buy_list:
            lines.append(f"- {priority} **{name}**")
            lines.append(f"  - {reason}")
        lines.append("")
        lines.append("---\n")
        lines.append("Keep this list handy for your next shopping trip! 🛍️")
        return "\n\n".join(lines)

def _respond_weather(korean: bool) -> str:
    """날씨 정보와 관련 가정 팁을 반환합니다."""
    weather = get_weather()
    today_w = weather["today"]
    tomorrow_w = weather["tomorrow"]

    if korean:
        lines = ["## 🌤️ 날씨 정보\n"]
        lines.append(f"### 오늘\n")
        lines.append(f"- 날씨: **{today_w['condition']}**")
        lines.append(f"- 기온: **{today_w['temp']}°C**")
        lines.append(f"- 습도: **{today_w['humidity']}%**\n")
        lines.append(f"### 내일\n")
        lines.append(f"- 날씨: **{tomorrow_w['condition']}**")
        lines.append(f"- 기온: **{tomorrow_w['temp']}°C**")
        lines.append(f"- 습도: **{tomorrow_w['humidity']}%**\n")
        lines.append(f"### 주간 전망\n")
        lines.append(f"- {weather['week_outlook']}\n")

        lines.append("---\n")
        lines.append("### 💡 날씨 기반 팁\n")
        if tomorrow_w["condition"].lower() in ["rainy", "rain"]:
            lines.append("- 🧺 내일 비가 올 예정이에요. 빨래는 오늘 하시는 게 좋아요.")
            lines.append("- ☂️ 외출 시 우산을 챙기세요.")
        if today_w["temp"] >= 30:
            lines.append("- ❄️ 기온이 높아요. 에어컨 필터 상태를 확인해보세요.")
            lines.append("- 💧 수분 섭취를 충분히 하세요.")
        elif today_w["temp"] <= 5:
            lines.append("- 🔥 기온이 낮아요. 난방 설정을 확인하세요.")
        if today_w["condition"].lower() in ["sunny", "clear"]:
            lines.append("- ☀️ 맑은 날이에요. 환기하기 좋은 날입니다.")

        return "\n\n".join(lines)

    else:
        lines = ["## 🌤️ Weather Overview\n"]
        lines.append("### Today\n")
        lines.append(f"- Condition: **{today_w['condition']}**")
        lines.append(f"- Temperature: **{today_w['temp']}°C**")
        lines.append(f"- Humidity: **{today_w['humidity']}%**\n")
        lines.append("### Tomorrow\n")
        lines.append(f"- Condition: **{tomorrow_w['condition']}**")
        lines.append(f"- Temperature: **{tomorrow_w['temp']}°C**")
        lines.append(f"- Humidity: **{tomorrow_w['humidity']}%**\n")
        lines.append("### Week Outlook\n")
        lines.append(f"- {weather['week_outlook']}\n")

        lines.append("---\n")
        lines.append("### 💡 Weather Tips\n")
        if tomorrow_w["condition"].lower() in ["rainy", "rain"]:
            lines.append("- 🧺 Rain expected tomorrow. Today is the best day for laundry.")
            lines.append("- ☂️ Don't forget an umbrella if going out.")
        if today_w["temp"] >= 30:
            lines.append("- ❄️ It's hot today. Make sure your AC filter is clean.")
            lines.append("- 💧 Stay hydrated.")
        elif today_w["temp"] <= 5:
            lines.append("- 🔥 It's cold today. Check your heating settings.")
        if today_w["condition"].lower() in ["sunny", "clear"]:
            lines.append("- ☀️ Beautiful day! Great time to air out the house.")

        return "\n\n".join(lines)

def _respond_laundry(korean: bool) -> str:
    """빨래 관련 응답을 반환합니다."""
    weather = get_weather()
    tomorrow_cond = weather["tomorrow"]["condition"].lower()

    if korean:
        lines = ["## 🧺 빨래 추천\n"]

        if "rain" in tomorrow_cond:
            lines.append("내일 비 예보가 있어요.\n")
            lines.append("- ☀️ **오늘 빨래하시는 걸 추천해요.** 바깥에 널어 말릴 수 있어요.")
            lines.append("- 내일까지 기다리면 건조가 며칠 늦어질 수 있어요.")
            lines.append("- 실내 건조대가 있다면 내일도 가능하지만, 오늘이 가장 좋아요.")
        else:
            lines.append("내일도 날씨가 괜찮을 것 같아요.\n")
            lines.append("- 오늘이든 내일이든 빨래하기 좋은 날이에요! 👕")
            lines.append("- 여유로운 시간에 하시면 됩니다.")

        return "\n\n".join(lines)

    else:
        lines = ["## 🧺 Laundry Recommendation\n"]

        if "rain" in tomorrow_cond:
            lines.append("Rain is expected tomorrow.\n")
            lines.append("- ☀️ **Today is your best bet for laundry.** You can dry clothes outside.")
            lines.append("- Waiting until tomorrow may delay drying by a few days.")
            lines.append("- If you have an indoor drying rack, tomorrow works too, but today is ideal.")
        else:
            lines.append("The weather looks clear for the next couple of days.\n")
            lines.append("- Any time works for laundry! 👕")
            lines.append("- Pick whichever day is most convenient for you.")

        return "\n\n".join(lines)

def _respond_greeting(korean: bool) -> str:
    """인사 응답을 반환합니다."""
    hour = datetime.now().hour

    if korean:
        if hour < 12:
            greeting = "좋은 아침이에요! ☀️"
        elif hour < 18:
            greeting = "좋은 오후예요! 😊"
        else:
            greeting = "좋은 저녁이에요! 🌙"

        return (
            f"{greeting}\n\n"
            "저는 HomeOS 가정 관리 도우미예요.\n"
            "아래와 같은 것들을 도와드릴 수 있어요.\n\n"
            '- 🥗 "뭐 먼저 먹어야 해?"\n'
            '- 📅 "이번 주 뭐 있어?"\n'
            '- ✈️ "여행 가기 전에 뭐 해야 해?"\n'
            '- 🛒 "뭐 사야 해?"\n'
            '- 🛠 "가전 점검 필요해?"\n'
            '- 🌤️ "날씨 어때?"\n\n'
            "편하게 질문해주세요! 😊"
        )

    else:
        if hour < 12:
            greeting = "Good morning! ☀️"
        elif hour < 18:
            greeting = "Good afternoon! 😊"
        else:
            greeting = "Good evening! 🌙"

        return (
            f"{greeting}\n\n"
            "I'm your HomeOS household assistant.\n"
            "Here are some things I can help with:\n\n"
            '- 🥗 "What should I eat first?"\n'
            '- 📅 "What\'s coming up this week?"\n'
            '- ✈️ "I\'m traveling this weekend."\n'
            '- 🛒 "What should I buy?"\n'
            '- 🛠 "How are my appliances?"\n'
            '- 🌤️ "What\'s the weather like?"\n\n'
            "Feel free to ask anything! 😊"
        )

def _respond_help(korean: bool) -> str:
    """도움말 응답을 반환합니다."""
    if korean:
        return (
            "## 💡 HomeOS 도우미 안내\n\n"
            "저는 여러분의 가정을 효율적으로 관리하도록 도와드려요.\n"
            "아래 주제에 대해 질문해보세요!\n\n"
            "### 할 수 있는 것들\n\n"
            "| 주제 | 예시 질문 |\n"
            "|------|----------|\n"
            '| 🥗 식재료 관리 | "뭐 먼저 먹어야 해?" |\n'
            '| 📅 일정 확인 | "이번 주 뭐 있어?" |\n'
            '| ✈️ 여행 준비 | "여행 전에 뭐 해야 해?" |\n'
            '| 🛒 장보기 | "뭐 사야 해?" |\n'
            '| 🛠 가전 관리 | "에어컨 필터 청소해야 해?" |\n'
            '| 🧺 빨래 | "오늘 빨래해도 돼?" |\n'
            '| 🌤️ 날씨 | "날씨 어때?" |\n\n'
            "한국어와 영어 모두 지원해요! 🌏"
        )

    else:
        return (
            "## 💡 HomeOS Assistant Guide\n\n"
            "I help you manage your household efficiently.\n"
            "Here's what you can ask about!\n\n"
            "### What I Can Do\n\n"
            "| Topic | Example |\n"
            "|-------|---------|\n"
            '| 🥗 Food Management | "What should I eat first?" |\n'
            '| 📅 Schedule | "What\'s coming up this week?" |\n'
            '| ✈️ Travel Prep | "I\'m going on a trip." |\n'
            '| 🛒 Shopping | "What should I buy?" |\n'
            '| 🛠 Appliances | "How are my appliances?" |\n'
            '| 🧺 Laundry | "Is it a good day for laundry?" |\n'
            '| 🌤️ Weather | "What\'s the weather like?" |\n\n'
            "I support both Korean and English! 🌏"
        )

def _respond_general(
    korean: bool,
    inventory: list,
    appliances: list,
    schedule: list,
) -> str:
    """일반적인 질문에 대한 종합 요약 응답을 반환합니다."""
    weather = get_weather()

    if korean:
        lines = ["## 🏠 홈 현황 요약\n"]

        # 날씨
        lines.append(f"### 🌤️ 오늘의 날씨\n")
        lines.append(
            f"- {weather['today']['condition']}, "
            f"{weather['today']['temp']}°C\n"
        )

        # 유통기한 임박
        expiring = [
            item for item in inventory
            if item.get("expiration_date") and _days_until(item["expiration_date"]) <= 3
        ]
        if expiring:
            lines.append("### 🥗 유통기한 주의\n")
            for item in expiring:
                days = _days_until(item["expiration_date"])
                lines.append(f"- **{item['name']}**: {days}일 남음")
            lines.append("")

        # 가전 이슈
        overdue_appliances = [
            a for a in appliances
            if a.get("last_maintenance")
            and _days_since(a["last_maintenance"]) > a.get("maintenance_interval_days", 90)
        ]
        if overdue_appliances:
            lines.append("### 🛠 가전 점검 필요\n")
            for a in overdue_appliances:
                lines.append(f"- {a.get('icon', '🔧')} **{a['name']}**: {a.get('maintenance_type', '관리')} 필요")
            lines.append("")

        # 다가오는 일정
        upcoming = [s for s in schedule if 0 <= _days_until(s["date"]) <= 7]
        if upcoming:
            lines.append("### 📅 이번 주 일정\n")
            for s in upcoming:
                days = _days_until(s["date"])
                lines.append(f"- {s['event']} ({days}일 후)")
            lines.append("")

        if not expiring and not overdue_appliances and not upcoming:
            lines.append("✨ 특별히 주의할 사항이 없어요. 편안한 하루 보내세요!\n")

        lines.append("---\n")
        lines.append("더 궁금한 게 있으시면 언제든 물어보세요! 😊")

        return "\n\n".join(lines)

    else:
        lines = ["## 🏠 Home Overview\n"]

        lines.append("### 🌤️ Today's Weather\n")
        lines.append(
            f"- {weather['today']['condition']}, "
            f"{weather['today']['temp']}°C\n"
        )

        expiring = [
            item for item in inventory
            if item.get("expiration_date") and _days_until(item["expiration_date"]) <= 3
        ]
        if expiring:
            lines.append("### 🥗 Expiring Soon\n")
            for item in expiring:
                days = _days_until(item["expiration_date"])
                lines.append(f"- **{item['name']}**: {days} day(s) left")
            lines.append("")

        overdue_appliances = [
            a for a in appliances
            if a.get("last_maintenance")
            and _days_since(a["last_maintenance"]) > a.get("maintenance_interval_days", 90)
        ]
        if overdue_appliances:
            lines.append("### 🛠 Maintenance Needed\n")
            for a in overdue_appliances:
                lines.append(f"- {a.get('icon', '🔧')} **{a['name']}**: {a.get('maintenance_type', 'maintenance')} due")
            lines.append("")

        upcoming = [s for s in schedule if 0 <= _days_until(s["date"]) <= 7]
        if upcoming:
            lines.append("### 📅 This Week\n")
            for s in upcoming:
                days = _days_until(s["date"])
                lines.append(f"- {s['event']} (in {days} days)")
            lines.append("")

        if not expiring and not overdue_appliances and not upcoming:
            lines.append("✨ Everything looks great! Enjoy your day.\n")

        lines.append("---\n")
        lines.append("Feel free to ask me anything specific! 😊")

        return "\n\n".join(lines)

# ═══════════════════════════════════════════════════════════════════
#  공개 API (다른 모듈에서 호출하는 함수)
# ═══════════════════════════════════════════════════════════════════

def get_chat_response(
    user_message: str,
    inventory: list,
    appliances: list,
    timeline: list,
    schedule: list,
) -> str:
    """
    사용자 메시지를 분석하여 컨텍스트 기반 응답을 생성합니다.

    Parameters:
        user_message: 사용자가 입력한 채팅 메시지
        inventory: 현재 인벤토리 목록
        appliances: 등록된 가전제품 목록
        timeline: 과거 이벤트 히스토리
        schedule: 향후 일정 목록

    Returns:
        마크다운 형식의 응답 문자열
    """
    korean = _is_korean(user_message)
    intent = _detect_intent(user_message)

    if intent == "weekly_schedule":
        return _respond_weekly_schedule(korean, inventory, appliances, timeline, schedule)

    if intent == "travel":
        return _respond_travel(korean, inventory, appliances, schedule)

    if intent == "eat_first":
        return _respond_eat_first(korean, inventory)

    if intent == "appliances":
        return _respond_appliances(korean, appliances)

    if intent == "shopping":
        return _respond_shopping(korean, inventory)

    if intent == "weather":
        return _respond_weather(korean)

    if intent == "laundry":
        return _respond_laundry(korean)

    if intent == "greeting":
        return _respond_greeting(korean)

    if intent == "help":
        return _respond_help(korean)

    # 기본 응답: 종합 현황 요약
    return _respond_general(korean, inventory, appliances, schedule)
