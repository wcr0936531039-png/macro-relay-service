"""Standalone preflight report for optional OpenBB candidate integration.

No network access, secrets or production writes. Run:
    python -m integrations.openbb_preflight
"""
import importlib.util
import json
from pathlib import Path

REQUIRED = (
    "integrations/openbb_adapter.py",
    "integrations/openbb_arbitration.py",
    "integrations/openbb_parity.py",
    "tests/test_openbb_adapter.py",
    "tests/test_openbb_date_column.py",
    "tests/test_openbb_parity_validation.py",
)


def preflight(root=None):
    base = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    missing = [path for path in REQUIRED if not (base / path).is_file()]
    provider_available = importlib.util.find_spec("openbb") is not None
    return {
        "status": "blocked" if missing else "ready_for_live_validation",
        "missing_files": missing,
        "openbb_installed": provider_available,
        "official_source_priority": True,
        "candidate_publishing_enabled": False,
        "live_parity_verified": False,
        "next_gate": "isolated_live_parity_with_fred_key",
    }


if __name__ == "__main__":
    print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True))
