"""Pure, side-effect-free arbitration for an optional OpenBB observation.

Official FRED is authoritative. An OpenBB candidate never overwrites it.
The candidate can fill only a genuinely missing official observation, and only
after a separate live-validation gate explicitly enables fallback.
"""
from datetime import date
from math import isfinite


def _valid(row):
    if not isinstance(row, dict) or row.get("status") != "ok":
        return False
    value = row.get("value")
    if isinstance(value, bool):
        return False
    try:
        if not isfinite(float(value)):
            return False
        observed = date.fromisoformat(row["date"])
        if observed > date.today():
            return False
    except (TypeError, ValueError, KeyError, OverflowError):
        return False
    return True


def choose_observation(official, candidate, *, allow_candidate=False):
    """Return (chosen, reason), without modifying either source.

    When official data is valid it always wins, even if candidate is newer.
    Candidate fallback requires an explicit feature gate and validated data.
    """
    if _valid(official):
        return official.copy(), "official_primary"
    if allow_candidate and _valid(candidate):
        return candidate.copy(), "candidate_fallback"
    return None, "unknown_no_valid_official"


# Public read-only validation predicate shared with parity checks.
valid_observation = _valid
