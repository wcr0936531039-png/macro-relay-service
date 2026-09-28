#!/usr/bin/env python3
"""Sequential official public-feed ingestion; no provider API keys."""
import csv, io, json, math, os, sys, zipfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.request import Request, urlopen
import sync_macro as legacy

# Match the dashboard's original series, units and formulas; never substitute proxies.
SPECS = [('SOFR',7),('RRPONTSYD',8),('RPONTSYD',8),('UNRATE',85),('SAHMREALTIME',85),
 ('T10Y2Y',7),('DFII10',7),('T5YIE',7),('RSAFS',85),('PAYEMS',85)]
# Additional indicators already represented in the dashboard. Every series is
# fetched serially after the initial Taiwan/U.S. acceptance set below.
MORE_SPECS = [
 ('SP500',7),('DJIA',7),('NASDAQCOM',7),
 ('DCOILWTICO',7),('DCOILBRENTEU',7),('DHHNGSP',7),('T10YIE',7),
 ('CPILFESL',95),('PCEPILFE',95),('BAMLH0A0HYM2',7),('BAMLC0A0CM',7),('IORB',7),
 ('STLFSI4',14),('ICSA',14),('CCSA',21),('IC4WSA',14),('INDPRO',95),('RRSFS',95),
 ('DTB3',7),('DGS10',7),('DGS30',7),('T10Y3M',7),('VIXCLS',7),('DEXJPUS',7),
 ('WALCL',14),('WCESTUS1',14),('NOCDFSA066MSFRBPHI',45)
]
OUT=Path('data/keyless_snapshot.json')
NDC_OPEN_DATA_ZIP=('https://ws.ndc.gov.tw/Download.ashx?icon=.zip&n=5pmv5rCj5oyH5qiZ5Y%2BK54eI6JmfLnppcA%3D%3D'
 '&u=LzAwMS9hZG1pbmlzdHJhdG9yLzEwL3JlbGZpbGUvNTc4MS82MzkyL2VhMjM1YmQ5LWQwNTItNGE2OS1hYmZjLWQ1Yzc4NWQzZDBlMi56aXA%3D')

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

def ndc_open_data_metric():
    """Use NDC's no-key government open-data ZIP when its live chart API blocks CI."""
    request=Request(NDC_OPEN_DATA_ZIP,headers={'User-Agent':legacy.USER_AGENT,'Accept':'application/zip,application/octet-stream,*/*'})
    with urlopen(request,timeout=30) as response:
        raw=response.read(15_000_001)
    if len(raw)>15_000_000 or not raw.startswith(b'PK'):
        raise ValueError('data.gov.tw linked NDC resource is not a valid ZIP')
    archive=zipfile.ZipFile(io.BytesIO(raw))
    names=[name for name in archive.namelist() if name.lower().endswith(('.csv','.txt')) and not name.startswith('__MACOSX/')]
    if not names:
        raise ValueError('NDC open-data ZIP contains no CSV/TXT table')
    def parse_period(raw_date):
        raw_date=str(raw_date).strip().replace('年','/').replace('月','').replace('-','/').replace('.','/')
        m=__import__('re').search(r'(?<!\d)(\d{3,4})\s*/?\s*(\d{1,2})(?!\d)',raw_date)
        if not m:return None
        year,month=map(int,m.groups())
        if year<1000:year+=1911
        if not 1<=month<=12:return None
        return f'{year}-{month:02d}-01'
    candidates=[]
    for name in names:
        payload=archive.read(name)
        text=None
        for encoding in ('utf-8-sig','cp950','big5'):
            try:text=payload.decode(encoding);break
            except UnicodeDecodeError:continue
        if text is None:continue
        sample=text[:4096]
        try:dialect=csv.Sniffer().sniff(sample,delimiters=',\t;')
        except csv.Error:dialect=csv.excel
        reader=csv.DictReader(io.StringIO(text),dialect=dialect)
        fields=[str(x or '').strip().lstrip('\ufeff') for x in (reader.fieldnames or [])]
        if not fields:continue
        score_key=next((f for f in fields if '景氣對策信號' in f and '分數' in f),None)
        light_key=next((f for f in fields if '景氣對策信號' in f and '分數' not in f),None)
        date_key=next((f for f in fields if f.lower() in ('date','年月','日期','資料年月','資料日期') or '年月' in f or '日期' in f),None)
        if not score_key or not date_key:continue
        # DictReader keys keep original BOM/spacing; normalize only for lookup.
        for row in reader:
            normalized={str(k or '').strip().lstrip('\ufeff'):v for k,v in row.items()}
            date=parse_period(normalized.get(date_key,''));value=normalized.get(score_key,'')
            if date is None or not legacy.valid_number(value):continue
            score=float(value)
            if not score.is_integer() or not 9<=score<=45:continue
            light=str(normalized.get(light_key,'')).strip() if light_key else ''
            if light:
                for short,standard in (('黃藍','黃藍燈'),('黃紅','黃紅燈'),('藍','藍燈'),('綠','綠燈'),('紅','紅燈')):
                    if light==short or light==standard:
                        light=standard;break
            if not light:
                light='紅燈' if score>=38 else '黃紅燈' if score>=32 else '綠燈' if score>=23 else '黃藍燈' if score>=17 else '藍燈'
            candidates.append((date,int(score),light,name))
    if not candidates:raise ValueError('NDC open-data ZIP lacks recognizable date and composite-signal score columns')
    date,score,light,name=max(candidates)
    return {'history':[{'date':date,'value':score}],'date':date,'value':score,'unit':'分','light':light,
        'provider':'國家發展委員會｜政府資料開放平台「景氣指標及燈號」',
        'source':'https://data.gov.tw/dataset/6099','method':f'國發會原始月資料 ZIP，欄位「景氣對策信號綜合分數」及燈號；檔案 {name}'}

def ecb_reference_rate(currency):
    url=f'https://data-api.ecb.europa.eu/service/data/EXR/D.{currency}.EUR.SP00.A?lastNObservations=25&format=csvdata'
    with urlopen(Request(url,headers={'User-Agent':legacy.USER_AGENT,'Accept':'text/csv'}),timeout=25) as response:
        raw=response.read(500_001)
    if len(raw)>500_000:raise ValueError('ECB response too large')
    reader=csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))
    rows={}
    for row in reader:
        date=row.get('TIME_PERIOD','').strip();value=row.get('OBS_VALUE','').strip()
        if row.get('OBS_STATUS','A') not in ('A',''):continue
        if not date or not legacy.valid_number(value):continue
        datetime.strptime(date,'%Y-%m-%d');rows[date]=float(value)
    if not rows:raise ValueError(f'ECB {currency}/EUR reference-rate table has no valid observations')
    return rows,url

def ecb_usd_jpy_cross():
    """USD/JPY reference cross from ECB JPY/EUR divided by USD/EUR, same date only."""
    jpy,jpy_url=ecb_reference_rate('JPY');usd,usd_url=ecb_reference_rate('USD')
    dates=sorted(set(jpy)&set(usd))
    if not dates:raise ValueError('ECB USD and JPY reference observations do not share a date')
    history=[{'date':date,'value':jpy[date]/usd[date]} for date in dates if usd[date]>0]
    if not history:raise ValueError('ECB USD/EUR denominator is not positive')
    latest=history[-1]
    return {'history':history[-20:],'date':latest['date'],'value':latest['value'],'unit':'JPY per USD',
        'provider':'歐洲中央銀行 ECB｜USD/EUR 與 JPY/EUR 參考匯率同日交叉換算',
        'source':jpy_url+' | '+usd_url,
        'method':'ECB 同日 JPY/EUR ÷ USD/EUR；這是官方參考匯率交叉換算，不是即時外匯成交價。'}

def eia_commercial_crude_stocks():
    """Parse the public EIA history table; keep the dashboard's million-barrel unit."""
    url='https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?f=W&n=PET&s=WCESTUS1'
    parser=legacy.TableParser();parser.feed(legacy.http_text(url))
    months={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
    points=[]
    for cells in parser.rows:
        if not cells:continue
        match=__import__('re').search(r'\b(20\d{2})-([A-Za-z]{3})\b',cells[0])
        if not match or match[2] not in months:continue
        year=int(match[1])
        for i in range(1,len(cells)-1,2):
            day=__import__('re').fullmatch(r'\s*(\d{2})/(\d{2})\s*',cells[i])
            value=cells[i+1].strip().replace(',','')
            if not day or not legacy.valid_number(value):continue
            month,dom=map(int,day.groups())
            try:date=f'{year:04d}-{month:02d}-{dom:02d}';datetime.strptime(date,'%Y-%m-%d')
            except ValueError:continue
            points.append({'date':date,'value':float(value)/1000})
    points=sorted({p['date']:p for p in points}.values(),key=lambda p:p['date'])
    if not points:raise ValueError('EIA WCESTUS1 history table contains no weekly observations')
    return {'history':points[-20:],'date':points[-1]['date'],'value':points[-1]['value'],'unit':'百萬桶',
        'provider':'U.S. Energy Information Administration｜WCESTUS1',
        'source':url,'method':'EIA 官方週資料表；原始千桶除以 1,000 轉為百萬桶，不含 SPR。'}

def twse_open_data_metric(metric):
    """Read one validated field from the exchange's no-key daily market CSV."""
    url='https://www.twse.com.tw/exchangeReport/FMTQIK?response=open_data'
    fields={'TWSE_TAIEX':('發行量加權股價指數','點',1.0),
            'TWSE_TOTAL_TRADE_VALUE':('成交金額','億元',100_000_000.0)}
    if metric not in fields:raise ValueError(f'unsupported TWSE market metric: {metric}')
    token,unit,divisor=fields[metric]
    request=Request(url,headers={'User-Agent':legacy.USER_AGENT,'Accept':'text/csv,application/csv;q=0.9,*/*;q=0.8'})
    with urlopen(request,timeout=25) as response:
        content_type=response.headers.get('Content-Type','').lower()
        body=response.read(1_000_001)
    if len(body)>1_000_000:raise ValueError('TWSE market CSV too large')
    if 'csv' not in content_type:raise ValueError(f'TWSE expected CSV; got {content_type or "unknown content type"}')
    try:text=body.decode('utf-8-sig')
    except UnicodeDecodeError:text=body.decode('cp950')
    if '<html' in text[:1000].lower():raise ValueError('TWSE returned HTML challenge, not CSV')
    rows=list(csv.reader(io.StringIO(text)))
    def clean(value):return str(value or '').strip().lstrip('\ufeff').replace(',','')
    header_index=None;date_col=index_col=None
    for i,cells in enumerate(rows):
        normalized=[clean(cell) for cell in cells]
        date_col=next((j for j,v in enumerate(normalized) if v in ('日期','資料日期','Date')),None)
        value_col=next((j for j,v in enumerate(normalized) if token in v),None)
        if date_col is not None and value_col is not None:
            header_index=i;break
    if header_index is None:raise ValueError(f'TWSE FMTQIK CSV lacks date and {token} columns')
    points=[]
    for cells in rows[header_index+1:]:
        if max(date_col,value_col)>=len(cells):continue
        raw_date=clean(cells[date_col]);raw_value=clean(cells[value_col])
        if not legacy.valid_number(raw_value):continue
        date=legacy.parse_roc_date(raw_date)
        if not date:continue
        datetime.strptime(date,'%Y-%m-%d')
        value=float(raw_value)/divisor
        if value<=0:continue
        points.append({'date':date,'value':value})
    points.sort(key=lambda point:point['date'])
    if points:
        latest=points[-1]
        return {'history':points[-20:],'date':latest['date'],'value':latest['value'],'unit':'點',
            'provider':'臺灣證券交易所｜政府資料開放平台每日市場成交資訊 CSV',
            'source':url,'method':f'TWSE 官方每日市場統計原始 CSV；直接讀取「{token}」欄位，成交金額以新臺幣元換算億元。'}
    sample=repr(rows[:6])[:1000]
    raise ValueError(f'TWSE FMTQIK CSV has no valid TAIEX observation; sample={sample}')

def main():
    old=json.loads(OUT.read_text()) if OUT.exists() else {'series':{}}
    if not isinstance(old,dict) or not isinstance(old.get('series'),dict):raise ValueError('Invalid prior snapshot')
    now=datetime.now(timezone.utc).isoformat(); current={}
    for key,entry in old['series'].items():current[key]={**entry,'status':'stale','error':'本輪尚未驗證'}
    tasks=[(sid,days,lambda sid=sid:fred_csv(sid)) for sid,days in SPECS]
    def get_ndc():
        try:return legacy.fetch_ndc()
        except Exception as live_error:
            try:return ndc_open_data_metric()
            except Exception as dataset_error:
                raise ValueError(f'NDC JSON/chart unavailable ({live_error}); official open-data ZIP unavailable ({dataset_error})') from dataset_error
    tasks += [('TW_EXPORT_ORDERS',85,lambda:legacy.taiwan_export_metric(legacy.http_text(legacy.MOEA_URL))),
              ('TPEX_BREADTH',5,lambda:legacy.tpex_metric(legacy.http_json(legacy.TPEX_URL))),
              ('TW_NDC_SIGNAL',120,get_ndc)]
    def additional_source(sid):
        if sid=='DEXJPUS':return ecb_usd_jpy_cross()
        if sid=='WCESTUS1':return eia_commercial_crude_stocks()
        return fred_csv(sid)
    tasks += [(sid,days,lambda sid=sid:additional_source(sid)) for sid,days in MORE_SPECS]
    tasks += [('TWSE_TAIEX',5,lambda:twse_open_data_metric('TWSE_TAIEX')),
              ('TWSE_TOTAL_TRADE_VALUE',5,lambda:twse_open_data_metric('TWSE_TOTAL_TRADE_VALUE'))]
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
