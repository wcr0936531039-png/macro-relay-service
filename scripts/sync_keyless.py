#!/usr/bin/env python3
"""Sequential official public-feed ingestion; no provider API keys."""
import csv, io, json, math, os, sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
import sync_macro as legacy

# Match the dashboard's original series, units and formulas; never substitute proxies.
SPECS = [('SOFR',7),('RRPONTSYD',8),('RPONTSYD',8),('UNRATE',85),('SAHMREALTIME',85),
 ('T10Y2Y',7),('DFII10',7),('T5YIE',7),('RSAFS',85),('PAYEMS',85)]
OUT=Path('data/keyless_snapshot.json')

def fred_csv(sid):
    since=(datetime.now(timezone.utc)-timedelta(days=650)).date().isoformat()
    url=f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={since}'
    with urlopen(Request(url,headers={'User-Agent':legacy.USER_AGENT,'Accept':'text/csv'}),timeout=25) as response:
        body=response.read(2000001)
    if len(body)>2000000:raise ValueError('CSV too large')
    reader=csv.DictReader(io.StringIO(body.decode('utf-8-sig')))
    if reader.fieldnames not in (['observation_date',sid],['DATE',sid]):raise ValueError('CSV series/header mismatch')
    rows={}
    for row in reader:
        raw=row[sid].strip()
        if raw in ('','.'):continue
        date=row[reader.fieldnames[0]];datetime.strptime(date,'%Y-%m-%d')
        value=float(raw)
        if not math.isfinite(value):raise ValueError('Nonfinite value')
        rows[date]={'date':date,'value':value}
    history=sorted(rows.values(),key=lambda p:p['date'])
    if not history:raise ValueError('No numeric observations')
    if sid in ('RSAFS','PAYEMS'):
        if len(history)<2:raise ValueError('Monthly history insufficient')
        a,b=history[-2:]
        if legacy.month_number(b['date'])-legacy.month_number(a['date'])!=1:raise ValueError('Nonadjacent monthly observations')
        if sid=='RSAFS' and a['value']<=0:raise ValueError('Invalid retail denominator')
    return {'history':history[-20:],'source':url,'provider':f'FRED 官方公開 CSV｜{sid}'}

def validate(entry,days):
    history=entry['history'];date=history[-1]['date']
    lag=(datetime.now(timezone.utc).date()-datetime.strptime(date,'%Y-%m-%d').date()).days
    if lag<0 or lag>days:raise ValueError(f'Observation outside freshness window: {date}')
    if any(type(p['value']) not in (int,float) or not math.isfinite(p['value']) for p in history):raise ValueError('Invalid numeric history')
    return entry

def main():
    old=json.loads(OUT.read_text()) if OUT.exists() else {'series':{}}
    if not isinstance(old,dict) or not isinstance(old.get('series'),dict):raise ValueError('Invalid prior snapshot')
    now=datetime.now(timezone.utc).isoformat(); current={}
    for key,entry in old['series'].items():current[key]={**entry,'status':'stale','error':'本輪尚未驗證'}
    tasks=[(sid,days,lambda sid=sid:fred_csv(sid)) for sid,days in SPECS]
    tasks += [('TW_EXPORT_ORDERS',85,lambda:legacy.taiwan_export_metric(legacy.http_text(legacy.MOEA_URL))),
              ('TPEX_BREADTH',5,lambda:legacy.tpex_metric(legacy.http_json(legacy.TPEX_URL))),
              ('TW_NDC_SIGNAL',120,legacy.fetch_ndc)]
    failed=None
    for sid,days,fetcher in tasks:
        try:
            item=fetcher()
            if 'history' not in item:item['history']=[{'date':item['date'],'value':item['value']}]
            validate(item,days)
            prior=current.get(sid)
            if prior and prior.get('history') and prior['history'][-1]['date']>item['history'][-1]['date']:raise ValueError('Refuse backward observation')
            current[sid]={**item,'status':'ok','fetched_at':now,'max_age_days':days}
            point=item['history'][-1];print(f"PASS {sid} {point['date']} {point['value']}",flush=True)
        except Exception as exc:
            failed={'id':sid,'reason':str(exc)}
            if sid in current:current[sid].update(status='stale',error=str(exc))
            print(f"STOP {sid}: {exc}",flush=True)
            break  # User requires each series to pass before proceeding.
    snapshot={'schema_version':1,'generated_at':now,'series':current,'blocked_at':failed,
        'coverage':{'usable':sum(x['status']=='ok' for x in current.values()),'expected':len(tasks)}}
    OUT.parent.mkdir(exist_ok=True)
    if any(x.get('history') for x in current.values()):OUT.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2))
    else:raise RuntimeError('No valid new or prior data; refusing empty publication')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as h:
            h.write(f"## No-key sequential verification\nUsable: {snapshot['coverage']['usable']}/{len(tasks)}\n\n")
            for sid,e in current.items():h.write(f"- {sid}: {e['history'][-1]['date']} = {e['history'][-1]['value']} ({e['status']})\n")
            if failed:h.write(f"\nStopped at {failed['id']}: {failed['reason']}\n")
    if failed:print('::warning::Sequential gate stopped; later indicators were not fetched.')

if __name__=='__main__':main()
