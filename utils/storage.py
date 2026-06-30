"""
storage.py
----------
JSON 기반 데이터 저장/로드 유틸리티.
"""

import json
import os

DATA_DIR = "data"

def _ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(filename: str, default=None):
    """JSON 파일을 로드합니다."""
    if default is None:
        default = []
    _ensure_dir()
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return default
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default

def save_json(filename: str, data):
    """데이터를 JSON 파일로 저장합니다."""
    _ensure_dir()
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
