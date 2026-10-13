#!/usr/bin/env python3
import datetime as dt
import json
import pathlib
import sys
import urllib.parse
import urllib.request
TICKERS=('SPY','XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE')
def fetch(ticker):
    url='https://query1.finance.yahoo.com/v8/finance/chart/'+urllib.parse.quote(ticker)+'?range=3mo&interval=1d'
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=15) as response:
        chart=json.load(response)['chart']['result'][0]
    offset=chart.get('meta',{}).get('gmtoffset',0)
    closes=chart['indicators']['quote'][0]['close']
    dates=chart['timestamp']
    rows={}
    for ts,price in zip(dates,closes):
        if isinstance(price,(int,float)) and 0<price<float('inf'):
            day=(dt.datetime.fromtimestamp(ts,dt.timezone.utc)+dt.timedelta(seconds=offset)).date().isoformat()
            rows[day]={'date':day,'close':round(price,6)}
    return [rows[k] for k in sorted(rows)]
def build(fetcher=fetch):
    result={'schema_version':1,'generated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'source':'Yahoo Finance chart API (unofficial)','histories':{},'status':{}}
    for ticker in TICKERS:
        try:
            rows=fetcher(ticker)
            if len(rows)<21: raise ValueError('INSUFFICIENT_HISTORY')
            result['histories'][ticker]=rows
            result['status'][ticker]={'status':'ok','observed_at':rows[-1]['date'],'count':len(rows)}
        except Exception as exc:
            result['histories'][ticker]=[]
            result['status'][ticker]={'status':'UNKNOWN','reason':type(exc).__name__}
    return result
if __name__=='__main__':
    target=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else 'data/us_sector_history.json')
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(build(),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
