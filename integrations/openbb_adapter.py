"""Optional OpenBB adapter. No changes to existing snapshot writer.

Install OpenBB separately in the scheduled Python environment:
    pip install openbb-fred
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
        from openbb import obb
        response = obb.fred.economy.fred_series(symbol=series_id, provider=provider)
        records = response.to_dataframe()
        if records.empty:
            raise ValueError("empty_response")
        column = next((c for c in records.columns if c.lower() in (series_id.lower(), "value")), None)
        if column is None:
            raise ValueError("series_column_missing")
        observations = records[[column]].dropna()
        if observations.empty:
            raise ValueError("no_valid_observations")
        index, row = observations.sort_index().iloc[-1:].iterrows().__next__()
        observation_date = index.date().isoformat() if hasattr(index, "date") else str(index)[:10]
        datetime.strptime(observation_date, "%Y-%m-%d")
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
