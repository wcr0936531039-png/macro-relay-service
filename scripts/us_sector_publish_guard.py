#!/usr/bin/env python3
"""Return 0 if candidate snapshot may replace remote; 2 if it is older.

This guard is separate from the strict snapshot validator, which runs before publication.
"""
import datetime as dt
import json
import pathlib
import sys

def observed_date(snapshot):
    if not isinstance(snapshot,dict):
        return None
    entry=(snapshot.get('status') or {}).get('SPY')
    if not isinstance(entry,dict) or entry.get('status')!='ok':
        return None
    value=entry.get('observed_at')
    if not isinstance(value,str):
        return None
    try:
        date=dt.date.fromisoformat(value)
        return date if date.isoformat()==value else None
    except ValueError:
        return None

def should_publish(candidate,remote):
    candidate_date=observed_date(candidate)
    if candidate_date is None:
        raise ValueError('INVALID_CANDIDATE_DATE')
    remote_date=observed_date(remote)
    return remote_date is None or candidate_date>=remote_date

if __name__=='__main__':
    candidate=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    remote_path=pathlib.Path(sys.argv[2])
    remote=json.loads(remote_path.read_text(encoding='utf-8')) if remote_path.exists() else {}
    if not should_publish(candidate,remote):
        print('SKIP_OLDER_SNAPSHOT: already-published SPY observation is newer')
        sys.exit(2)
    print('PUBLICATION_DATE_GATE_OK')
