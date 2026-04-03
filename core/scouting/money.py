"""Helpers for parsing and formatting Football Manager money values."""

import re

import pandas as pd


def parse_money_text(value):
    if pd.isna(value):
        return None

    text = str(value).strip().lower().replace(",", "")
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*([kmb])?", text)
    if not match:
        return None

    amount = float(match.group(1))
    multiplier = {"k": 10**3, "m": 10**6, "b": 10**9}.get(match.group(2), 1)
    return int(amount * multiplier)


def format_currency(value):
    if pd.isna(value):
        return "-"
    if value >= 10**6:
        return f"£{round(value / 10**6, 1)}m"
    if value >= 10**3:
        return f"£{int(value / 10**3)}k"
    if value >= 0:
        return f"£{int(value)}"
    return "-"
