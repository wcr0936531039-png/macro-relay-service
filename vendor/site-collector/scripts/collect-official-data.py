"""Fetch dated official observations and quotes. Credentials are never needed here."""
import argparse, concurrent.futures, csv, datetime as dt, io, json, pathlib, re, urllib.parse, urllib.request, html, time

p = argparse.ArgumentParser()
p.add_argument('--output', required=True)
p.add_argument('--sessions', type=int, default=60)
p.add_argument('--company-evidence')
p.add_argument('--issuer-only', action='store_true')
p.add_argument('--market-only', action='store_true')
p.add_argument('--macro-only', action='store_true')
p.add_argument('--cpi-only', action='store_true')
p.add_argument('--statistics-only', action='store_true')
# 白天（信用統計當晚才公布）跑一般收集時略過信用統計，不留舊檔、不重試等待；狀態檔照實記「略過」。
p.add_argument('--skip-statistics', action='store_true')
args = p.parse_args()
root = pathlib.Path(args.output); root.mkdir(parents=True, exist_ok=True)
rawdir = root / 'raw'; rawdir.mkdir(exist_ok=True)
now = lambda: dt.datetime.now(dt.timezone.utc).isoformat()
# 網站匯入用 UTC 日期檢查「不得晚於今天」；收集程式也用 UTC，否則台北凌晨抓到 FRED 提前公布的下一日觀測（如 IORB）會整筆被拒。
utc_today = lambda: dt.datetime.now(dt.timezone.utc).date()
def fetch(url):
    # FRED 在 GitHub 雲端主機上擋自訂 User-Agent（2026-11-03 GitHub 實測：只有 Python 預設字串回 200，其他逾時或連線中斷）；
    # 對 FRED 第一次用 Python 預設字串、第二次用原本字串；其他網站不變。
    error = None
    fred = urllib.parse.urlparse(url).hostname == 'fred.stlouisfed.org'
    for attempt in range(2):
        headers = {'Accept':'application/json,text/csv'}
        if not (fred and attempt == 0): headers['User-Agent'] = 'TaiwanStockMaster/1.0'
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=25).read().decode('utf-8-sig')
        except Exception as exc: error = exc
    raise error
def save(name, value): (root / name).write_text(json.dumps(value, ensure_ascii=False))
def number(value):
    try: return float(re.sub('<[^>]*>', '', str(value)).replace(',', '').strip())
    except ValueError: return None

def collect_statistics():
    # MI_INDEX is the session anchor; turnover OpenAPI can lag by a day.
    target='https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?type=ALLBUT0999&response=json'
    latest=json.loads(fetch(target))
    if latest.get('stat')!='OK' or not re.fullmatch(r'\d{8}',str(latest.get('date',''))): raise ValueError('Latest MI_INDEX session unavailable')
    date_key=latest['date'];date=dt.datetime.strptime(date_key,'%Y%m%d').date().isoformat()
    (rawdir/'statistics-latest-session.json').write_text(json.dumps(latest,ensure_ascii=False))
    failures=[]
    for attempt in range(3):
        try:
            calendar_url='https://www.twse.com.tw/holidaySchedule/holidaySchedule?response=json'
            dates_url='https://openapi.twse.com.tw/v1/exchangeReport/FMTQIK'
            calendar=json.loads(fetch(calendar_url));dates=json.loads(fetch(dates_url))
            last=max(str(row['Date']) for row in dates)
            normalized=(str(int(last[:3])+1911)+last[3:]) if len(last)==7 else last
            if normalized!=date_key:
                dates_url='https://www.twse.com.tw/exchangeReport/FMTQIK?date='+date_key[:6]+'01&response=json'
                dates=json.loads(fetch(dates_url))
                if dates.get('stat')!='OK' or dates.get('fields',[])[0:3:2]!=['日期','成交金額']: raise ValueError('Official FMTQIK monthly schema mismatch')
                last=max(str(row[0]) for row in dates['data']);parts=last.split('/')
                normalized=str(int(parts[0])+1911)+parts[1].zfill(2)+parts[2].zfill(2)
            if normalized!=date_key: raise ValueError('Official turnover not yet aligned to latest MI_INDEX session')
            base='https://www.twse.com.tw/rwd/zh/marginTrading/'
            sources={'calendar':calendar_url,'tradingDates':dates_url,'margin':base+'MI_MARGN?response=json&date='+date_key+'&selectType=MS','marginTrend':base+'MI_MARGN_TREND?response=json&date='+date_key+'&days=30','creditSummary':base+'BFIJ3U?response=json&date='+date_key}
            stats={'date':date,'sourceUrls':sources,'calendar':calendar,'tradingDates':dates,'latestSessionSource':target,'collectionAttempts':attempt+1,'retryErrors':failures.copy()}
            for key in ['margin','marginTrend','creditSummary']:
                raw=fetch(sources[key]);(rawdir/(key+'-'+date+'.json')).write_text(raw);payload=json.loads(raw)
                if payload.get('stat')!='OK' or payload.get('date')!=date_key: raise ValueError('Official statistics not yet aligned: '+key)
                stats[key]=payload
            stats['capturedAt']=now();save('statistics.json',{'schema_version':1,'marketStatistics':stats});return stats
        except Exception as exc:
            failures.append(str(exc))
            if attempt<2: time.sleep(10)
    raise ValueError('Official statistics incomplete after 3 attempts: '+'; '.join(failures))

def core_cpi_history(points):
    points=sorted(points,key=lambda row:row['date'])
    if len(points)<4 or len({row['date'] for row in points})!=len(points): raise ValueError('Insufficient or duplicate core CPI history')
    last=points[-4:]
    month=lambda row:int(row['date'][:4])*12+int(row['date'][5:7])
    if any(month(b)-month(a)!=1 for a,b in zip(last,last[1:])): raise ValueError('Non-consecutive core CPI history')
    return points[-24:]

def collect_core_cpi():
    sources=[];errors=[]
    bls_url='https://download.bls.gov/pub/time.series/cu/cu.data.0.Current'
    fred_url='https://fred.stlouisfed.org/graph/fredgraph.csv?'+urllib.parse.urlencode({'id':'CPILFESL','cosd':(dt.date.today()-dt.timedelta(days=800)).isoformat()})
    for family,url in [('BLS',bls_url),('FRED',fred_url)]:
        try:
            points=[]
            if family=='BLS':
                # AllItems omits SA0L1E. Stream Current; never retain 49 MB in memory.
                try:
                    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0','Accept':'text/plain,*/*;q=0.8'})
                    with urllib.request.urlopen(request,timeout=30) as response, (rawdir/'BLS-core-CPI-current.txt').open('wb') as raw:
                        columns=None;size=0
                        for line in response:
                            size+=len(line)
                            if size>80_000_000 or len(line)>4096: raise ValueError('BLS CPI file exceeds expected size')
                            raw.write(line);cells=line.decode('utf-8-sig').split()
                            if not cells: continue
                            if columns is None:
                                columns=[cells.index(key) for key in ['series_id','year','period','value']]
                                continue
                            si,yi,pi,vi=columns
                            if len(cells)<=max(columns) or cells[si]!='CUSR0000SA0L1E' or not re.fullmatch(r'M(?:0[1-9]|1[0-2])',cells[pi]): continue
                            date=dt.date(int(cells[yi]),int(cells[pi][1:]),1).isoformat();value=number(cells[vi])
                            if value is not None and value>0 and date<=utc_today().isoformat(): points.append({'date':date,'value':value})
                    core_cpi_history(points)
                except Exception as file_error:
                    # The keyless official API is a second BLS route, never an
                    # independent vote. Preserve the failed file attempt too.
                    url='https://api.bls.gov/publicAPI/v1/timeseries/data/'
                    try:
                        request=urllib.request.Request(url,data=json.dumps({'seriesid':['CUSR0000SA0L1E'],'startyear':str(dt.date.today().year-2),'endyear':str(dt.date.today().year)}).encode(),headers={'User-Agent':'Mozilla/5.0','Content-Type':'application/json','Accept':'application/json'})
                        with urllib.request.urlopen(request,timeout=20) as response: raw=response.read(2_000_001)
                        if len(raw)>2_000_000: raise ValueError('BLS API response exceeds expected size')
                        (rawdir/'BLS-core-CPI-api.json').write_bytes(raw);body=json.loads(raw)
                        result=body.get('Results',{}).get('series',[])
                        if body.get('status')!='REQUEST_SUCCEEDED' or len(result)!=1 or result[0].get('seriesID')!='CUSR0000SA0L1E': raise ValueError('BLS API series/status mismatch: '+str(body.get('message',[])))
                        points=[]
                        for row in result[0].get('data',[]):
                            if not re.fullmatch(r'M(?:0[1-9]|1[0-2])',row.get('period','')): continue
                            date=dt.date(int(row['year']),int(row['period'][1:]),1).isoformat();value=number(row['value'])
                            if value is not None and value>0 and date<=utc_today().isoformat(): points.append({'date':date,'value':value})
                        core_cpi_history(points)
                    except Exception as api_error: raise ValueError('BLS Current: '+str(file_error)+'; BLS API: '+str(api_error)) from api_error
                    errors.append({'source':'BLS-core-CPI','error':('BLS Current: '+str(file_error)+'; official API fallback used')[:500]})
            else:
                raw=fetch(url);(rawdir/'FRED-core-CPI.csv').write_text(raw)
                for row in csv.DictReader(io.StringIO(raw)):
                    value=number(row['CPILFESL']);date=dt.date.fromisoformat(row['observation_date']).isoformat()
                    if value is not None and value>0 and date<=utc_today().isoformat(): points.append({'date':date,'value':value})
            history=core_cpi_history(points)
            sources.append({'series':'CUSR0000SA0L1E' if family=='BLS' else 'CPILFESL','sourceFamily':family,'source':url,'fetchedAt':now(),'history':history})
        except Exception as exc: errors.append({'source':family+'-core-CPI','error':str(exc)[:500]})
    # Write even an empty result, so reusing a folder cannot import an old success.
    save('cpi.json',{'schema_version':1,'coreCpiSources':sources,'coreCpiFailures':errors})
    same_month=len(sources)==2 and sources[0]['history'][-1]['date']==sources[1]['history'][-1]['date']
    passed=same_month and abs(sources[0]['history'][-1]['value']-sources[1]['history'][-1]['value'])<=.02
    status={'sources':[{'family':row['sourceFamily'],'date':row['history'][-1]['date'],'value':row['history'][-1]['value'],'fetchedAt':row['fetchedAt']} for row in sources],'passed':passed,'errors':errors}
    save('cpi-collection-status.json',status)
    return status

def collect_macro():
    series=[]; errors=[]
    source_ids={key:key for key in ['DCOILBRENTEU','DHHNGSP','DEXJPUS','DCOILWTICO','IORB','DTWEXAFEGS']}
    source_ids.update({'US3M':'DTB3','US10Y':'DGS10','US30Y':'DGS30'})
    for key,source_id in source_ids.items():
        try:
            start=(dt.date.today()-dt.timedelta(days=145 if key in ('DEXJPUS','DTWEXAFEGS') else 45)).isoformat()
            url='https://fred.stlouisfed.org/graph/fredgraph.csv?'+urllib.parse.urlencode({'id':source_id,'cosd':start})
            raw=fetch(url); (rawdir/(key+'.csv')).write_text(raw); history=[]
            for row in csv.DictReader(io.StringIO(raw)):
                value=number(row[source_id])
                if value is not None and value>0 and row['observation_date']<=utc_today().isoformat(): history.append({'date':row['observation_date'],'value':value})
            if len(history)<(65 if key=='DEXJPUS' else 26 if key=='DTWEXAFEGS' else 3): raise ValueError('Insufficient official history: '+key)
            record={'id':key,'source':url,'fetchedAt':now(),'history':history}
            try:
                source='https://fred.stlouisfed.org/series/'+source_id
                page=fetch(source); (rawdir/(key+'-release.html')).write_text(page)
                latest=re.search(r'(\d{4}-\d{2}-\d{2}):\s*<span[^>]*class="series-meta-observation-value"[^>]*>([\d.,]+)</span>',page)
                release=re.search(r'Next Release Date:\s*<span[^>]*>([^<]+)</span>',page)
                if latest and release and latest[1]<=utc_today().isoformat():
                    next_date=dt.datetime.strptime(html.unescape(release[1]).strip(),'%b %d, %Y').date().isoformat()
                    if latest[1]!=history[-1]['date'] or abs(number(latest[2])-history[-1]['value'])>1e-8: raise ValueError('FRED page/CSV latest observation mismatch')
                    if not 0<=(dt.date.fromisoformat(next_date)-dt.date.fromisoformat(latest[1])).days<=21: raise ValueError('Unbounded FRED next-release window')
                    record['releaseVerification']={'source':source,'date':latest[1],'value':number(latest[2]),'nextReleaseDate':next_date,'fetchedAt':now()}
            except Exception as exc: errors.append({'source':key+'-release','error':str(exc)})
            series.append(record)
        except Exception as exc: errors.append({'source':key,'error':str(exc)})
    if series: save('series.json', {'schema_version':1,'series':series})
    stats=None
    (root/'statistics.json').unlink(missing_ok=True)
    if args.skip_statistics: errors.append({'source':'TWSE-statistics','error':'skipped: --skip-statistics'})
    else:
        try: stats=collect_statistics()
        except Exception as exc: errors.append({'source':'TWSE-statistics','error':str(exc)});stats=None
    cpi=collect_core_cpi();errors.extend(cpi['errors'])
    status={'checkedAt':now(),'series':[{'id':row['id'],'date':row['history'][-1]['date'],'nextReleaseDate':row.get('releaseVerification',{}).get('nextReleaseDate')} for row in series],'coreCpi':cpi,'marketStatisticsDate':stats and stats['date'],'errors':errors}
    save('macro-collection-status.json',status);print(json.dumps(status,ensure_ascii=False),flush=True)
    return status

if args.statistics_only:
    (root/'statistics.json').unlink(missing_ok=True)
    try:
        stats=collect_statistics();print(json.dumps({'date':stats['date'],'source':stats['sourceUrls']['tradingDates'],'attempts':stats['collectionAttempts']}),flush=True)
    except Exception as exc:
        save('statistics-collection-status.json',{'checkedAt':now(),'error':str(exc)});raise
    raise SystemExit(0)

if args.cpi_only:
    status=collect_core_cpi();print(json.dumps(status,ensure_ascii=False),flush=True)
    raise SystemExit(0 if status['passed'] else 1)

if not args.issuer_only and not args.market_only:
    macro_status=collect_macro()
    if args.macro_only:
        raise SystemExit(0 if len(macro_status['series'])==9 and (args.skip_statistics or macro_status['marketStatisticsDate']) and macro_status['coreCpi']['passed'] else 1)

sources = {'twse':'https://openapi.twse.com.tw/v1/opendata/t187ap03_L','tpex':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O'}
meta = {}; metadata_errors = []
metadata_url = 'https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockInfo'
try:
    for item in sorted(json.loads(fetch(metadata_url))['data'], key=lambda x:x.get('date','')):
        meta[str(item['stock_id'])] = item
except Exception as exc:
    metadata_errors.append({'source':metadata_url,'error':str(exc),'fallback':'Official issuer industry codes; no inferred industry names'})
    print('OPTIONAL_METADATA_FAILED',str(exc),flush=True)
issuers = {}
for market, code, name, industry in [('twse','公司代號','公司簡稱','產業別'),('tpex','SecuritiesCompanyCode','CompanyAbbreviation','SecuritiesIndustryCode')]:
    payload = json.loads(fetch(sources[market])); (rawdir / (market+'-issuers.json')).write_text(json.dumps(payload, ensure_ascii=False))
    for item in payload:
        symbol = str(item[code])
        if re.fullmatch(r'[1-9]\d{3}', symbol):
            industry_code = str(item[industry]).strip()
            label = meta.get(symbol,{}).get('industry_category')
            fallback_label = '官方產業別 '+industry_code if re.fullmatch(r'\d{1,2}',industry_code) else '產業未分類'
            issuers[symbol] = {'id':symbol,'name':item[name],'market':market,'industry_code':industry_code,'industry':label or fallback_label,'industry_source':metadata_url if label else sources[market]}
            listing = str(item.get('上市日期' if market == 'twse' else 'DateOfListing', '')).strip()
            if re.fullmatch(r'\d{8}', listing):
                try:
                    listing_date = dt.datetime.strptime(listing, '%Y%m%d').date()
                    if listing_date <= utc_today():
                        issuers[symbol].update(listingDate=listing_date.isoformat(), listingSource=sources[market])
                except ValueError: pass
# STOCK_DAY_ALL can still contain the prior session after today's close.
# Use the date actually published by the exchange's latest after-trading report.
latest_url = 'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?type=ALLBUT0999&response=json'
latest_raw = fetch(latest_url); (rawdir / 'latest-twse-report.json').write_text(latest_raw)
latest = json.loads(latest_raw)
if str(latest.get('stat', '')).lower() != 'ok' or not any('證券代號' in table.get('fields', []) for table in latest.get('tables', [])):
    raise ValueError('Latest official after-trading report unavailable or schema changed')
asof_date = dt.datetime.strptime(str(latest.get('date', '')), '%Y%m%d').date()
if asof_date > dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date():
    raise ValueError('Latest official after-trading date is in the future')
asof = asof_date.isoformat()
universe = {market:sum(row['market']==market for row in issuers.values()) for market in sources}; universe['total']=sum(universe.values())
save('universe.json', {'schema_version':1,'issuerUniverse':{'asOf':asof,'capturedAt':now(),'sources':sources,'classificationSource':metadata_url if meta else 'TWSE/TPEx official issuer industry codes','metadataErrors':metadata_errors,'rows':list(issuers.values())}})
if args.issuer_only:
    print(json.dumps({'issuers':len(issuers),'listingDates':sum(bool(row.get('listingDate')) for row in issuers.values()),'asOf':asof}))
    raise SystemExit(0)
def quote(day):
    urls={'twse':'https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX?'+urllib.parse.urlencode({'date':day.replace('-',''),'type':'ALLBUT0999','response':'json'}),'tpex':'https://www.tpex.org.tw/www/zh-tw/afterTrading/otc?'+urllib.parse.urlencode({'date':day.replace('-','/'),'type':'AL','response':'json'})}
    rows=[]; no_trade_rows=[]; volume_rows=[]; seen=set()
    for market,url in urls.items():
        cache=rawdir/(day+'-'+market+'.json')
        if cache.exists() and dt.datetime.now().timestamp()-cache.stat().st_mtime<30*3600: text=cache.read_text(); captured=dt.datetime.fromtimestamp(cache.stat().st_mtime,dt.timezone.utc).isoformat()
        else: text=fetch(url); cache.write_text(text); captured=now()
        payload=json.loads(text)
        if payload.get('stat','').lower()!='ok': return None
        if payload.get('date')!=day.replace('-',''): raise ValueError('Official date mismatch '+market+' '+day)
        code='證券代號' if market=='twse' else '代號'
        table=next((t for t in payload.get('tables',[]) if code in [x.strip() for x in t.get('fields',[])] and '成交股數' in [x.strip() for x in t.get('fields',[])]),None)
        if table is None: raise ValueError('Official quote schema changed '+market)
        for values in table['data']:
            item=dict(zip([x.strip() for x in table['fields']],values)); symbol=str(item[code]).strip(); base=issuers.get(symbol)
            if not base or base['market']!=market: continue
            seen.add(symbol)
            base={key:value for key,value in base.items() if key not in ('listingDate','listingSource')}
            close=number(item.get('收盤價',item.get('收盤'))); volume=number(item['成交股數']); amount=number(item.get('成交金額',item.get('成交金額(元)'))); change=number(item.get('漲跌價差',item.get('漲跌')))
            if volume == 0 and amount == 0:
                no_trade_rows.append({**base,'volume':0,'amount':0,'close':None,'state':'official_no_trade'})
                continue
            if any(x is None for x in [close,volume,amount,change]) or close<=0 or volume<=0:
                if volume is not None and volume>0 and amount is not None and amount>=0:
                    volume_rows.append({**base,'volume':volume,'amount':amount,'close':close if close is not None and close>0 else None,'state':'official_volume_only'})
                continue
            if market=='twse' and '-' in str(item.get('漲跌(+/-)','')): change=-abs(change)
            rows.append({**base,'close':close,'volume':volume,'amount':amount,'change':change})
    # 名冊有、當天官方行情表沒有（多為停止買賣／暫停交易）：列出來，不補價（網站 missingBreakdown 依此重算）
    not_quoted_rows=[{**{k:v for k,v in row.items() if k not in ('listingDate','listingSource')},'close':None,'state':'official_not_quoted'} for symbol,row in issuers.items() if symbol not in seen]
    counts={market:sum(row['market']==market for row in rows) for market in urls}
    if any(counts[m]/universe[m]<.9 for m in urls): raise ValueError('Official coverage below 90% '+day)
    return {'date':day,'capturedAt':captured,'sourceUrls':urls,'universe':universe,'universeAsOf':asof,'classificationAsOf':asof,'source_method':'同日官方盤後普通股行情；產業分類採目前名冊，歷史成分未校正存活偏誤。','rows':rows,'noTradeRows':no_trade_rows,'volumeRows':volume_rows,'notQuotedRows':not_quoted_rows}

day=dt.date.fromisoformat(asof); snapshots=[]; errors=[]
while len(snapshots)<args.sessions and (dt.date.fromisoformat(asof)-day).days<145:
    batch=[]
    while len(batch)<min(12, max(1, args.sessions-len(snapshots))):
        if day.weekday()<5: batch.append(day.isoformat())
        day-=dt.timedelta(days=1)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures={executor.submit(quote,date):date for date in batch}
        for future in concurrent.futures.as_completed(futures):
            date=futures[future]
            try:
                result=future.result()
                if result: snapshots.append(result); print(date,len(result['rows']),flush=True)
            except Exception as exc: errors.append({'date':date,'error':str(exc)}); print(date,str(exc),flush=True)
snapshots=sorted(snapshots,key=lambda x:x['date'])[-args.sessions:]
for item in snapshots: save(item['date']+'.json',{'schema_version':1,'marketSnapshots':[item]})
if args.company_evidence:
    evidence=json.loads(pathlib.Path(args.company_evidence).read_text())
    for record in evidence['records']: record.pop('local_pdf',None)
    save('company.json',{'schema_version':1,'companies':[{'symbol':evidence['symbol'],'records':evidence['records']}]})
save('collection-status.json',{'checkedAt':now(),'asOf':asof,'sessions':len(snapshots),'requested':args.sessions,'errors':errors,'metadataErrors':metadata_errors,'universe':universe})
print('COMPLETE',len(snapshots),'sessions',universe,'errors',len(errors),flush=True)
if len(snapshots)<args.sessions: raise SystemExit('Required history incomplete; do not claim completion')
