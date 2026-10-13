"""Optional OpenBB adapter. No changes to existing snapshot writer.

Install OpenBB separately in the scheduled Python environment:
    pip install openbb-fred\n    openbb-build
This adapter does not require OpenBB for imports or for existing ETL jobs.
"""
from datetime import datetime, timezone
from typing import Any


def fetch_fred_series(series_id: str, provider: str = "fred") -> dict[str, Any]:
    """Fetch a FRED series through OpenBB, returning an auditable observation.

    This is a *candidate* source, not an automatic replacement for the official
    FRED pipeline. Never infer a date or synthesize a value on failure.
    """
    try:
        import re
        if not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", series_id):
            raise ValueError("invalid_series_id")
        from openbb import obb
        response = obb.fred.economy.fred_series(symbol=series_id, provider=provider, limit=12)
        records = response.to_dataframe()
        if records.empty:
            raise ValueError("empty_response")
        # OpenBB providers may expose date/value columns or a dated index.
        column = next((c for c in records.columns if str(c).lower() in (series_id.lower(), "value")), None)
        if column is None:
            raise ValueError("series_column_missing")
        if "date" in records.columns:
            candidates = [(str(row["date"])[:10], row[column])
                          for _, row in records.iterrows()]
        else:
            candidates = [(idx.date().isoformat() if hasattr(idx, "date") else str(idx)[:10], row[column])
                          for idx, row in records.iterrows()]
        import math
        valid = []
        for date_text, raw_value in candidates:
            try:
                parsed = datetime.strptime(date_text, "%Y-%m-%d").date()
                number = float(raw_value)
                if math.isfinite(number) and parsed <= datetime.now(timezone.utc).date():
                    valid.append((parsed, number))
            except (TypeError, ValueError, OverflowError):
                continue
        if not valid:
            raise ValueError("no_valid_observations")
        parsed_date, value = max(valid, key=lambda x: x[0])
        observation_date = parsed_date.isoformat()
        parsed_date = datetime.strptime(observation_date, "%Y-%m-%d").date()
        if parsed_date > datetime.now(timezone.utc).date():
            raise ValueError("future_observation_date")
        value = float(row[column])
        import math
        if not math.isfinite(value):
            raise ValueError("non_finite_value")
        return {
            "symbol": series_id,
            "value": value,
            "date": observation_date,
            "source": "openbb:fred",
            "status": "ok",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        return {
            "symbol": series_id,
            "value": None,
            "date": None,
            "source": "openbb:fred",
            "status": "missing",
            "error": f"{type(exc).__name__}: {exc}",
        }
