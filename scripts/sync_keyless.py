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
 ('WALCL',14),('WCESTUS1',14),('NOCDFSA066MSFRBPHI',45),('DRTSCILM',120),('DTWEXBGS',10)
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

def yahoo_chart_metric(sid):
    """Fetch a keyless Yahoo chart series without changing its market definition."""
    symbols={'ICE_DXY':([('^NYICDX','query1.finance.yahoo.com'),('DX-Y.NYB','query2.finance.yahoo.com'),('^NYICDX','query2.finance.yahoo.com')],'指數點'),
             'XAU':([('XAUUSD=X','query1.finance.yahoo.com'),('XAUUSD=X','query2.finance.yahoo.com')],'美元/金衡盎司')}
    if sid not in symbols:raise ValueError(f'unsupported Yahoo chart metric: {sid}')
    candidates,unit=symbols[sid];failures=[];response_data=None;symbol=None;url=None
    for symbol_candidate,host in candidates:
        candidate_url=f'https://{host}/v8/finance/chart/{symbol_candidate}?interval=1d&range=1mo'
        request=Request(candidate_url,headers={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/128 Safari/537.36','Accept':'application/json'})
        try:
            with urlopen(request,timeout=25) as response:
                content_type=response.headers.get('Content-Type','').lower();body=response.read(500_001)
            if len(body)>500_000:raise ValueError('Yahoo chart response too large')
            if 'json' not in content_type:raise ValueError(f'Yahoo chart expected JSON; got {content_type or "unknown content type"}')
            response_data=json.loads(body.decode('utf-8-sig'))
            result=(response_data.get('chart') or {}).get('result')
            if not isinstance(result,list) or not result:raise ValueError(f'Yahoo chart has no {symbol_candidate} observations')
            symbol=symbol_candidate;url=candidate_url;break
        except Exception as error:
            failures.append(f'{host}/{symbol_candidate}: {error}')
    if response_data is None:raise ValueError('All Yahoo no-key endpoints failed: '+'; '.join(failures))
    result=(response_data.get('chart') or {}).get('result')
    item=result[0];timestamps=item.get('timestamp') or [];quotes=((item.get('indicators') or {}).get('quote') or [{}])[0];closes=quotes.get('close') or []
    points=[]
    for timestamp,value in zip(timestamps,closes):
        if not isinstance(timestamp,(int,float)) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:continue
        date=datetime.fromtimestamp(timestamp,timezone.utc).date().isoformat();points.append({'date':date,'value':float(value)})
    points=sorted({p['date']:p for p in points}.values(),key=lambda p:p['date'])
    if not points:raise ValueError(f'Yahoo chart returned no numeric close for {symbol}')
    latest=points[-1]
    return {'history':points[-20:],'date':latest['date'],'value':latest['value'],'unit':unit,
        'provider':f'Yahoo Finance｜{symbol} ICE 日資料（延遲行情）' if sid=='ICE_DXY' else f'Yahoo Finance｜{symbol} 日資料（延遲行情）','source':url,
        'method':'Yahoo Finance chart 最後一筆有效日收盤；觀測日為原始 Unix timestamp 的 UTC 日期，並依序列時效門檻驗證。'}

def gold_api_metric():
    """Fetch the public USD/XAU spot quote; keep provider and timestamp explicit."""
    url='https://api.gold-api.com/price/XAU'
    request=Request(url,headers={'User-Agent':legacy.USER_AGENT,'Accept':'application/json'})
    with urlopen(request,timeout=25) as response:
        content_type=response.headers.get('Content-Type','').lower();body=response.read(200_001)
    if len(body)>200_000:raise ValueError('Gold API response too large')
    if 'json' not in content_type:raise ValueError(f'Gold API expected JSON; got {content_type or "unknown content type"}')
    data=json.loads(body.decode('utf-8-sig'))
    if data.get('symbol')!='XAU' or (data.get('currency') and data.get('currency')!='USD'):
        raise ValueError('Gold API symbol/currency mismatch; expected XAU quoted in USD')
    value=data.get('price')
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:
        raise ValueError('Gold API price is not a positive numeric value')
    updated=data.get('updatedAt') or data.get('updated_at') or data.get('timestamp')
    if not isinstance(updated,str):raise ValueError('Gold API has no ISO timestamp')
    try:stamp=datetime.fromisoformat(updated.replace('Z','+00:00'))
    except ValueError as error:raise ValueError('Gold API timestamp is not ISO format') from error
    if stamp.tzinfo is None:raise ValueError('Gold API timestamp has no timezone')
    date=stamp.astimezone(timezone.utc).date().isoformat()
    return {'history':[{'date':date,'value':float(value)}],'date':date,'value':float(value),'unit':'美元/金衡盎司',
        'provider':'Gold API｜XAU/USD 現貨參考價（第三方；非官方定盤價）','source':url,
        'method':f'來源回傳 XAU/USD 報價 {value}，更新時間 {stamp.isoformat()}；不是 LBMA 定盤價或即時交易所成交價。'}

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
        return {'history':points[-20:],'date':latest['date'],'value':latest['value'],'unit':unit,
            'provider':'臺灣證券交易所｜政府資料開放平台每日市場成交資訊 CSV',
            'source':url,'method':f'TWSE 官方每日市場統計原始 CSV；直接讀取「{token}」欄位，成交金額以新臺幣元換算億元。'}
    sample=repr(rows[:6])[:1000]
    raise ValueError(f'TWSE FMTQIK CSV has no valid TAIEX observation; sample={sample}')

def twse_credit_metric(metric,date):
    """Read one official aggregate field from the TWSE daily summary HTML."""
    compact=date.replace('-','')
    url=f'https://www.twse.com.tw/exchangeReport/MI_MARGN?date={compact}&response=html'
    html=legacy.http_text(url)
    date_match=__import__('re').search(r'(\d{3})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',html)
    observed=f'{int(date_match[1])+1911:04d}-{int(date_match[2]):02d}-{int(date_match[3]):02d}' if date_match else None
    if observed!=date:raise ValueError(f'TWSE credit observation date mismatch: requested {date}, returned {observed or "missing"}')
    parser=legacy.TableParser();parser.feed(html)
    data={}
    for cells in parser.rows:
        if not cells:continue
        label=''.join(str(cells[0]).split())
        numbers=[]
        for cell in cells[1:]:
            raw=str(cell).replace(',','').strip()
            if legacy.valid_number(raw):numbers.append(float(raw))
        if label and len(numbers)>=5:data[label]=numbers
    mapping={
      'TWSE_MARGIN_BALANCE_NTD':('融資金額(仟元)', '億元', lambda p:p[-1]/100000),
      'TWSE_MARGIN_CHANGE_NTD':('融資金額(仟元)', '億元', lambda p:(p[-1]-p[-2])/100000),
      'TWSE_MARGIN_BALANCE_UNITS':('融資(交易單位)', '張', lambda p:p[-1]),
      'TWSE_SHORT_BALANCE':('融券(交易單位)', '張', lambda p:p[-1]),
      'TWSE_SHORT_CHANGE':('融券(交易單位)', '張', lambda p:p[-1]-p[-2]),
    }
    if metric not in mapping:raise ValueError(f'unsupported TWSE credit metric: {metric}')
    label,unit,calculate=mapping[metric]
    selected=next((values for key,values in data.items() if key==label),None)
    if not selected:raise ValueError(f'TWSE credit HTML lacks aggregate row {label}; sample={repr(parser.rows[:12])[:1200]}')
    value=calculate(selected)
    if not math.isfinite(value):raise ValueError(f'TWSE credit HTML produced nonfinite {metric}')
    return {'history':[{'date':date,'value':value}],'date':date,'value':value,'unit':unit,
        'provider':'臺灣證券交易所｜信用交易統計（MI_MARGN）官方頁面',
        'source':url,'method':f'{label} 欄位；{unit}；日增減以今日餘額減前日餘額計算。'}

def twse_market_breadth(reference_date):
    """Calculate TWSE-listed advance share from the official no-key daily stock CSV."""
    url='https://www.twse.com.tw/exchangeReport/STOCK_DAY_ALL?response=open_data'
    request=Request(url,headers={'User-Agent':legacy.USER_AGENT,'Accept':'text/csv,application/csv;q=0.9,*/*;q=0.8'})
    with urlopen(request,timeout=25) as response:
        content_type=response.headers.get('Content-Type','').lower();body=response.read(8_000_001)
    if len(body)>8_000_000:raise ValueError('TWSE daily stock CSV too large')
    if 'csv' not in content_type:raise ValueError(f'TWSE expected daily-stock CSV; got {content_type or "unknown content type"}')
    try:text=body.decode('utf-8-sig')
    except UnicodeDecodeError:text=body.decode('cp950')
    if '<html' in text[:1000].lower():raise ValueError('TWSE returned HTML challenge, not CSV')
    rows=list(csv.reader(io.StringIO(text)))
    clean=lambda x:str(x or '').strip().lstrip('\ufeff')
    header=None;date_col=change_col=None
    for i,cells in enumerate(rows):
        fields=[clean(x) for x in cells]
        date_col=next((j for j,x in enumerate(fields) if x in ('Date','日期','資料日期')),None)
        change_col=next((j for j,x in enumerate(fields) if x in ('Change','漲跌價差','漲跌')),None)
        code_col=next((j for j,x in enumerate(fields) if x in ('Code','證券代號','股票代號')),None)
        if date_col is not None and change_col is not None and code_col is not None:header=i;break
    if header is None:raise ValueError(f'TWSE stock CSV lacks date/code/change columns; sample={repr(rows[:5])[:1000]}')
    observations=[]
    for cells in rows[header+1:]:
        if max(date_col,change_col,code_col)>=len(cells):continue
        code=clean(cells[code_col]);date=legacy.parse_roc_date(clean(cells[date_col]))
        raw=clean(cells[change_col]).replace(',','').replace('＋','+').replace('－','-').replace('−','-')
        if not code or not date:continue
        if date!=reference_date:continue
        try:value=float(raw.replace('+',''))
        except ValueError:continue
        if math.isfinite(value):observations.append(value)
    if not observations:raise ValueError('TWSE stock CSV has no parseable rows for the official market date')
    advances=sum(value>0 for value in observations);declines=sum(value<0 for value in observations);unchanged=sum(value==0 for value in observations);moving=advances+declines
    if moving<100:raise ValueError(f'TWSE market breadth sample too small: {len(observations)} securities')
    value=advances/moving*100
    return {'history':[{'date':reference_date,'value':value}],'date':reference_date,'value':value,'unit':'%',
        'advancers':advances,'decliners':declines,'unchanged':unchanged,'included':len(observations),
        'provider':'臺灣證券交易所｜政府資料開放平台 STOCK_DAY_ALL CSV',
        'source':url,'method':f'上市證券上漲占比 = 上漲 {advances} ÷（上漲 {advances} + 下跌 {declines}）× 100%；平盤 {unchanged} 家不放入分母。交易日與同日官方 FMTQIK 核對。'}

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
        if sid in ('ICE_DXY','XAU'):return yahoo_chart_metric(sid)
        return fred_csv(sid)
    tasks += [(sid,days,lambda sid=sid:additional_source(sid)) for sid,days in MORE_SPECS]
    tasks += [('TWSE_TAIEX',5,lambda:twse_open_data_metric('TWSE_TAIEX')),
              ('TWSE_TOTAL_TRADE_VALUE',5,lambda:twse_open_data_metric('TWSE_TOTAL_TRADE_VALUE')),
              ('TWSE_BREADTH',5,lambda:twse_market_breadth(current['TWSE_TAIEX']['history'][-1]['date'])),
              ('TWSE_MARGIN_BALANCE_NTD',5,lambda:twse_credit_metric('TWSE_MARGIN_BALANCE_NTD',current['TWSE_TAIEX']['history'][-1]['date'])),
              ('TWSE_MARGIN_CHANGE_NTD',5,lambda:twse_credit_metric('TWSE_MARGIN_CHANGE_NTD',current['TWSE_TAIEX']['history'][-1]['date'])),
              ('TWSE_MARGIN_BALANCE_UNITS',5,lambda:twse_credit_metric('TWSE_MARGIN_BALANCE_UNITS',current['TWSE_TAIEX']['history'][-1]['date'])),
              ('TWSE_SHORT_BALANCE',5,lambda:twse_credit_metric('TWSE_SHORT_BALANCE',current['TWSE_TAIEX']['history'][-1]['date'])),
              ('TWSE_SHORT_CHANGE',5,lambda:twse_credit_metric('TWSE_SHORT_CHANGE',current['TWSE_TAIEX']['history'][-1]['date'])),
              ('XAU',3,lambda:gold_api_metric()),
              ('ICE_DXY',3,lambda:yahoo_chart_metric('ICE_DXY'))]
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
