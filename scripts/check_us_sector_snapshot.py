import datetime as dt
import json
import pathlib
import sys
TICKERS={'SPY','XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE'}
def validate(data, now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    issues=[]
    if data.get('schema_version')!=1:issues.append('SCHEMA_MISMATCH')
    status=data.get('status') or {}
    histories=data.get('histories') or {}
    if set(status)!=TICKERS or set(histories)!=TICKERS:issues.append('SYMBOL_COVERAGE')
    dates=set()
    for ticker in sorted(TICKERS):
        item=status.get(ticker) or {}
        rows=histories.get(ticker) or []
        if item.get('status')!='ok' or len(rows)<21:
            issues.append(ticker+':MISSING_HISTORY')
            continue
        dates.add(item.get('observed_at'))
        if rows[-1].get('date')!=item.get('observed_at'):issues.append(ticker+':DATE_MISMATCH')
        if any(not isinstance(row.get('close'),(int,float)) or row['close']<=0 for row in rows):issues.append(ticker+':BAD_PRICE')
    if len(dates)!=1:issues.append('DATES_NOT_ALIGNED')
    observed=next(iter(dates)) if len(dates)==1 else None
    if observed:
        try:
            age=(now.date()-dt.date.fromisoformat(observed)).days
            if age<0 or age>5:issues.append('STALE_OR_FUTURE_DATA')
        except ValueError:issues.append('INVALID_DATE')
    return {'status':'OK' if not issues else 'UNKNOWN','coverage':sum((status.get(t) or {}).get('status')=='ok' for t in TICKERS),'observed_at':observed,'issues':issues}
if __name__=='__main__':
    payload=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'))
    result=validate(payload)
    print(json.dumps(result,ensure_ascii=False))
    if result['status']!='OK':sys.exit(1)
