"""One-shot audit collection. Does not publish or modify hosted code."""
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys
import urllib.error
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
RELAY = ROOT.parent / 'macro-relay-remediation'
sys.path.insert(0, str(RELAY / 'scripts'))
from us_market_calendar import expected_latest_session, is_session, session_settled_utc

TICKERS = ('SPY','XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE')
NY = ZoneInfo('America/New_York')

def collect(ticker):
    records = []
    for host in ['query1.finance.yahoo.com', 'query2.finance.yahoo.com']:
        url = 'https://' + host + '/v8/finance/chart/' + urllib.parse.quote(ticker) + '?range=3mo&interval=1d'
        meta = {'ticker':ticker,'url':url,'started_at':dt.datetime.now(dt.timezone.utc).isoformat()}
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'}),timeout=20) as response:
                raw = response.read()
                meta.update(http_status=response.status,final_url=response.url,headers={k:response.headers[k] for k in ['Date','Content-Type','Age'] if k in response.headers})
            meta.update(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),raw_file=f'{ticker}-{host}.json')
            (ROOT / meta['raw_file']).write_bytes(raw)
            parsed = json.loads(raw)
            chart = parsed['chart']['result'][0]
            if parsed['chart'].get('error') is not None: raise ValueError('YAHOO_CHART_ERROR')
            if chart['meta'].get('symbol') != ticker: raise ValueError('SYMBOL_MISMATCH')
            if chart['meta'].get('exchangeTimezoneName') != 'America/New_York': raise ValueError('TIMEZONE_MISMATCH')
            if chart['meta'].get('currency') != 'USD': raise ValueError('CURRENCY_MISMATCH')
            times, closes = chart['timestamp'], chart['indicators']['quote'][0]['close']
            if not isinstance(times,list) or not isinstance(closes,list) or len(times)!=len(closes): raise ValueError('LENGTH_MISMATCH')
            now = dt.datetime.now(dt.timezone.utc)
            rows, dropped = {}, []
            for stamp, close in zip(times, closes):
                session_day = dt.datetime.fromtimestamp(stamp,dt.timezone.utc).astimezone(NY).date()
                day = session_day.isoformat()
                reason = None
                if isinstance(close,bool) or not isinstance(close,(int,float)) or not math.isfinite(close) or close <= 0: reason='NULL_OR_INVALID_CLOSE'
                elif not is_session(session_day): reason='NON_SESSION'
                elif now < session_settled_utc(session_day): reason='SESSION_NOT_SETTLED'
                if reason:
                    dropped.append({'date':day,'reason':reason});continue
                if day in rows: raise ValueError('DUPLICATE_DATE')
                rows[day] = {'date':day,'close':round(close,6)}
            rows = [rows[key] for key in sorted(rows)]
            if len(rows)<21: raise ValueError('INSUFFICIENT_HISTORY')
            required = expected_latest_session(now,grace_hours=0).isoformat()
            if rows[-1]['date'] != required: raise ValueError('LATEST_SESSION_MISSING: '+rows[-1]['date']+' expected '+required)
            meta.update(completed_at=dt.datetime.now(dt.timezone.utc).isoformat(),observed_at=rows[-1]['date'],count=len(rows),required_session=required,dropped_bars=dropped)
            records.append(meta)
            return ticker,rows,records
        except Exception as exc:
            meta.update(completed_at=dt.datetime.now(dt.timezone.utc).isoformat(),error_type=type(exc).__name__,error=str(exc))
            if isinstance(exc,urllib.error.HTTPError):meta['http_status']=exc.code
            records.append(meta)
            # Save each failure immediately; no stale fallback masquerades as fresh.
            (ROOT/f'{ticker}-failures.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    return ticker,None,records

def main():
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    all_records = {}
    histories = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(collect,ticker) for ticker in TICKERS]
        for future in concurrent.futures.as_completed(futures):
            ticker, rows, records = future.result()
            all_records[ticker] = records
            if rows is not None: histories[ticker]=rows
            manifest = {'started_at':started,'completed_tickers':len(all_records),'success_tickers':len(histories),'requests':all_records}
            (ROOT/'collection-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
            print(json.dumps({'ticker':ticker,'ok':rows is not None,'date':rows[-1]['date'] if rows else None,'count':len(rows) if rows else 0,'attempts':len(records)},ensure_ascii=False),flush=True)
    if len(histories) != len(TICKERS): raise SystemExit('PARTIAL_SOURCE_COLLECTION: candidate not published')
    dates = [row['date'] for row in histories['SPY']]
    if any([r['date'] for r in histories[ticker]] != dates for ticker in TICKERS): raise SystemExit('SESSION_ALIGNMENT_MISMATCH')
    # No return bars are created. Dates and rounded closes all come from saved original responses.
    payload = {'schema_version':1,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source':'Yahoo Finance chart API (unofficial)','histories':{ticker:histories[ticker] for ticker in TICKERS},'status':{ticker:{'status':'ok','observed_at':histories[ticker][-1]['date'],'count':len(histories[ticker])} for ticker in TICKERS}}
    (ROOT/'us_sector_history.candidate.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
    print('CANDIDATE_READY: 12/12 real sources; common latest session '+dates[-1],flush=True)

if __name__ == '__main__':main()
