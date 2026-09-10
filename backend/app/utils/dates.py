"""Small date helpers (ported from the notebook)."""
from datetime import date
from typing import Optional


def _iso_to_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except Exception:
        return None
