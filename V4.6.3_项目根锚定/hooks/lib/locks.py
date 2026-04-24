"""Deprecated in V4.6.0 final: freeze locks removed. Keep hash helper for callers.

See gate_freeze_locks.py header for the design rationale.
"""
from __future__ import annotations

import hashlib


def compute_content_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# No-op shims kept so any lingering import does not crash
def feature_checklist_frozen() -> bool:
    return False


def plan_frozen() -> bool:
    return False


def plan_must_changed(current_text: str) -> list[str]:
    return []


def verdict_tampered(slug: str, current_text: str) -> bool:
    return False


def sign_verdict(slug: str, verification_text: str) -> None:
    pass


def feature_hash_matches_lock(current_text: str) -> bool:
    return True


def freeze_feature_checklist(slug: str) -> None:
    pass


def freeze_plan(slug: str) -> None:
    pass


def feature_freeze_lock() -> dict:
    return {}


def plan_freeze_lock() -> dict:
    return {}


def latest_verdict_signature(slug: str) -> dict:
    return {}
