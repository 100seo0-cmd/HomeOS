# 🏠 HomeOS

**Your AI Operating System for Home**

HomeOS는 사용자의 일정, 냉장고 재고, 가전 관리 이력, 집안일 기록을 종합하여 지금 필요한 집안일을 추천하는 AI Agent입니다.

단순한 To-do 앱이나 스마트홈 제어 앱이 아니라, 사용자가 놓치기 쉬운 사소한 집안일을 대신 기억하고 생활 상황에 맞춰 필요한 행동을 제안하는 것을 목표로 합니다.

---

## 1. Project Overview

현대의 집안일은 단순히 청소만을 의미하지 않습니다.

냉장고 속 식재료 관리, 유통기한 확인, 생필품 재고 파악, 세탁기·건조기·에어컨과 같은 가전제품의 주기적 관리, 여행이나 외출 전 준비까지 모두 집안일의 일부입니다.

HomeOS는 이러한 정보를 하나의 흐름으로 연결하여 사용자가 집을 더 편하게 관리할 수 있도록 돕는 AI Agent입니다.

---

## 2. Key Features

### 🏠 Dashboard

HomeOS가 오늘 필요한 집안일을 추천합니다.

예시:

* 우유 유통기한이 임박했습니다.
* 두부와 상추를 여행 전에 먼저 소비하는 것이 좋습니다.
* 세탁조 청소 시기가 다가왔습니다.
* 생필품 재고가 부족할 수 있습니다.

각 추천 항목에는 **Why?** 기능이 있어, 왜 해당 집안일을 추천했는지 확인할 수 있습니다.

---

### 🥬 Inventory

냉장고 속 식재료와 생필품을 관리합니다.

관리 항목:

* 식재료 이름
* 수량
* 유통기한
* 생필품 재고

HomeOS는 유통기한이 가까운 식재료를 우선적으로 알려주고, 어떤 재료를 먼저 소비하면 좋을지 제안합니다.

---

### 🛠 Appliances

가전제품의 주기적인 관리 일정을 기억합니다.

관리 대상 예시:

* 에어컨 필터 청소
* 세탁조 청소
* 건조기 필터 청소
* 공기청정기 필터 교체
* 정수기 필터 교체

사용자가 관리 완료 버튼을 누르면 HomeOS가 해당 기록을 저장하고, 이후 관리 주기에 맞춰 다시 알려줍니다.

---

### 🤖 AI Chat

사용자는 HomeOS에게 자연어로 질문할 수 있습니다.

예시 질문:

* 이번 주말 여행 가.
* 냉장고 뭐부터 먹어야 해?
* 가전 관리할 거 있어?
* 이번 주 뭐 있어?
* 뭐 사야 해?

HomeOS는 일정, 재고, 가전 상태, 집안일 기록을 바탕으로 상황에 맞는 답변을 제공합니다.

---

### 📅 Timeline

집안일 기록을 시간순으로 저장합니다.

예시:

* 세탁조 청소 완료
* 에어컨 필터 청소
* 휴지 구매
* 침구 세탁
* 정수기 필터 교체

Timeline은 집안일을 단순히 처리하는 것을 넘어, 집의 관리 이력을 기억하는 역할을 합니다.

---

## 3. Demo Scenario

사용자가 이번 주말 여행을 간다고 입력하면 HomeOS는 다음과 같은 내용을 제안합니다.

* 여행 전 유통기한이 임박한 식재료를 먼저 소비하기
* 여행 전 장보기는 미루기
* 쓰레기를 미리 버리고 가기
* 세탁기와 에어컨 등 가전 상태 확인하기
* 귀가 후 필요한 집안일을 정리하기

이를 통해 HomeOS는 단순한 챗봇이 아니라, 집안일을 맥락에 맞게 이해하고 추천하는 AI Agent로 동작합니다.

---

## 4. Tech Stack

* Python
* Streamlit
* JSON-based local data storage
* Rule-based AI logic for prototype demonstration

본 프로젝트는 과제용 무료 프로토타입으로 제작되었으며, OpenAI API는 연결하지 않았습니다.

---

## 5. Project Structure

```text
HomeOS/
├── app.py
├── views/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── inventory.py
│   ├── appliances.py
│   ├── chat.py
│   └── timeline.py
├── data/
│   ├── inventory.json
│   ├── appliances.json
│   ├── timeline.json
│   └── schedule.json
├── utils/
│   ├── __init__.py
│   ├── ai.py
│   ├── storage.py
│   ├── recommendation.py
│   └── ui_components.py
└── requirements.txt
```

---

## 6. How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 7. Future Vision

HomeOS는 향후 다음 방향으로 확장될 수 있습니다.

* 다양한 브랜드의 스마트 가전 통합 관리
* Wi-Fi 기반 IoT 기기 제어
* 쇼핑몰 API 연동을 통한 생필품 가격 비교 및 구매 지원
* 청소·수리 업체 검색 및 예약 지원
* Physical AI와 연동하여 실제 집안일 수행 로봇의 판단 시스템으로 확장

현재는 사용자가 직접 행동하는 단계이지만, 향후 Physical AI가 발전하면 HomeOS에 축적된 집안일 데이터와 생활 패턴이 로봇의 판단 기준으로 활용될 수 있습니다.

---

## 8. Concept

HomeOS는 사용자를 평가하지 않습니다.

집에 점수를 매기거나 사용자의 생활을 판단하는 대신, 사용자가 기억하기 어려운 일을 조용히 대신 기억하고 필요한 순간에 알려주는 것을 목표로 합니다.

**HomeOS is not a scoring system.
It is a calm AI assistant that remembers, recommends, and helps.**
