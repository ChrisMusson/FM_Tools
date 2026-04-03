"""Helpers for working with Football Manager UID values."""


def normalise_uid(uid):
    text = str(uid).strip()
    return int(text[2:] if text[:2].lower() == "r-" else text)
