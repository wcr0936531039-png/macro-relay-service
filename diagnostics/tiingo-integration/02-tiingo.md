# v229 本機整合：第 1 步 Tiingo

狀態：本機實作與指定範圍測試完成；未部署。原站基線 543793fa6be1a9d4dfde79d0be4313eeb436f8e8，Claude 交接 3d62320914a5ab663725d704b7d6f6e7f8d64b3c。

## 完成
- 已從擁有者保存 ZIP 取得原型，修正應有交易日之後的資料列先過濾再判定；同時對持久快取重做防禦檢查。
- exactly 22 tickers；十國每國一票，SPY 必須具備200筆有效觀測。其餘缺項顯示有效分母及涵蓋數，不算成均線下。
- 類股 5/10/20 相對強弱取完整 Tiingo adjClose；Yahoo 整組獨立，標備援來源；無歷史拼接。台灣收盤基準也套用到寬度計算。
- D1 私人持久快取＋跨執行個體單一更新租約＋單條原子SQL保留請求額度。rolling 60min 50、rolling24h1000、calendar month500symbols；429/401 全批停止扣額度並存退避。
- 2028 NYSE 官方休市日與7/3、11/24提前收盤；2027/12/31不誤補假。
- 來源同日比較33個相對報酬，保護界線暫定0.25百分點（來源品質保護，不是買賣門檻；待擁有者審閱）；超過停用Tiingo報告並走獨立Yahoo備援。兩來源不足同日資料時標 not_compared，不宣稱核對完成。

## 限制／下一位接手須知
- 未讀取真實金鑰，未請求真實 Tiingo 價格；雲端實際 API 權限與延遲尚未驗證。真實 Tiingo 行情不進本檔／公開中繼／日誌。
- 投資分數、Gate、VETO、既有權重與風險預算不變。
- 第2步面板與第3步綜合判斷仍在進行；尚未跑最終全套測試。
- 首次SQL測試因測試程式的Python字串引號出錯失敗；已修測試並重跑，下列是最終結果。

## 測試
```text
npm warn Unknown env config "http-proxy". This will stop working in the next major version of npm.

> build
> node build.mjs

✔ exact 22 tickers; ten markets, one vote each (2.826305ms)
✔ exclude later-than-expected bars before observedAt; auth header only, adjClose only (21.555833ms)
✔ defensive stored-result filtering and missing completed session retain original last-good (2.539207ms)
✔ 401/403/429/empty/invalid JSON/exception are sanitized (3.181421ms)
✔ conflicting duplicates are rejected, not overwritten (0.898445ms)
✔ 200 samples required; partial global breadth uses observed denominator only, SPY mandatory (74.892502ms)
✔ RSP/SPY is exactly 20 aligned sessions, not intersection extended across a hole (57.778836ms)
✔ persistent same-session cache survives a fresh refresh invocation without quota/fetch (39.341826ms)
✔ 429 stops the fan-out, persists cooldown; next invocation makes zero requests (1.797529ms)
✔ without persistent cache and atomic reservation no network call is allowed (1.450703ms)
✔ actual SQLite: concurrent reservations cap at 50, rolling-hour boundary, day/month guards and single refresh lease (212.87522ms)
✔ Site uses full private adjClose history independently, including prior calendar year (143.760997ms)
✔ Taiwan-close cutoff applies to breadth as well as relative returns (78.84648ms)
✔ same-date providers compare 33 relative returns; large differences block primary (55.1255ms)
✔ one failed global market is partial; failed SPY makes primary unavailable (114.288361ms)
✔ missing private DB fails closed before any Tiingo request (0.419252ms)
✔ 實檔：2026-10-17 01:28Z 產生、最後一天 10-15；10-19 10:26Z 應有 10-16 → LATEST_SESSION_MISSING（不是格式錯誤） (19.56238ms)
✔ 資料補上 10-16、擷取時間不變：週一早上仍可用（舊規則 57 小時會判 UNKNOWN） (1.382201ms)
✔ 只刷新 generated_at、資料沒變：仍是 LATEST_SESSION_MISSING (0.542371ms)
✔ 收盤後 8 小時內上游還沒發布：前一個交易日仍可用；超過才算缺 (0.915456ms)
✔ 擷取時間早於最後一列的收盤：CAPTURE_BEFORE_CLOSE (3.183955ms)
✔ 格式、來源、擷取時間各自的錯誤碼 (0.264089ms)
✔ NYSE 休市日、提前收盤、夏令時間結束 (2.717647ms)
✔ 超出休市日表的年份：失敗而不是放行 (1.075061ms)
✔ 2028 official NYSE calendar, Saturday New Year has no Friday substitute, two early closes (0.562945ms)
ℹ tests 25
ℹ suites 0
ℹ pass 25
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 670.111761
US sector Site: 12 live ETFs, 66 independent RS comparisons, Taiwan-close timing, gaps/UNKNOWN, source/D1 retention, real report wiring and unchanged scoring/VETO passed

```

## 本階段完整 git diff（含新增檔及建置產物）
```diff
diff --git a/build.mjs b/build.mjs
index 09b4ce3..bbc6705 100644
--- a/build.mjs
+++ b/build.mjs
@@ -16,7 +16,10 @@ const stockRelay = readFileSync(new URL('./worker/stock-relay.js', import.meta.u
 const usSectorCore = readFileSync(new URL('./worker/us-sector-core.js', import.meta.url), 'utf8');
 const usSectors = readFileSync(new URL('./worker/us-sectors.js', import.meta.url), 'utf8');
 const usSectorSessionSource = readFileSync(new URL('./worker/us-sector-session.mjs', import.meta.url), 'utf8').replace(/^export /gm,'');
-const usSectorSession = `const US_SECTOR_SESSION=(()=>{${usSectorSessionSource}\nreturn {usSectorFreshness,isSession,calendarCovers,NYSE_EARLY_CLOSE,sessionSettledAt};})();`;
+const usSectorSession = `const US_SECTOR_SESSION=(()=>{${usSectorSessionSource}\nreturn {usSectorFreshness,isSession,calendarCovers,NYSE_EARLY_CLOSE,sessionSettledAt,expectedLatestSession};})();`;
+const tiingoMarket=`const TIINGO_MARKET=(()=>{${readFileSync(new URL('./worker/tiingo-market.mjs',import.meta.url),'utf8').replace(/^export /gm,'')}\nreturn {SECTORS,GLOBAL,SYMBOLS,PRICE_FIELD,PROVIDER,selectSession,breadth,refreshPrivateMarket};})();`;
+const tiingoStore=`const TIINGO_STORE=(()=>{${readFileSync(new URL('./worker/tiingo-store.mjs',import.meta.url),'utf8').replace(/^export /gm,'')}\nreturn {createPrivateStore};})();`;
+const tiingoSite=readFileSync(new URL('./worker/tiingo-site.js',import.meta.url),'utf8');
 const marketTimeline = readFileSync(new URL('./worker/market-timeline.js', import.meta.url), 'utf8');
 const masterEvidence = readFileSync(new URL('./worker/master-evidence.js', import.meta.url), 'utf8');
 const masterInputs = readFileSync(new URL('./worker/master-inputs.js', import.meta.url), 'utf8');
@@ -35,4 +38,4 @@ const officialNewsModule=readFileSync(new URL('./worker/official-news.js',import
 updateTools.sourceCollectorNode=updateTools.sourceCollectorNode.replace("let newsModule = '__OFFICIAL_NEWS_MODULE__';",`let newsModule = ${JSON.stringify(officialNewsModule)};`);
 const macro = readFileSync(new URL('./worker/macro.js', import.meta.url), 'utf8');
 mkdirSync(new URL('./dist/server/', import.meta.url), { recursive: true });
-writeFileSync(new URL('./dist/server/index.js', import.meta.url), `const HTML = ${JSON.stringify(html)};\nconst CPI_SEED = ${JSON.stringify(cpiSeed)};\nconst OFFICIAL_UPDATE_TOOLS = ${JSON.stringify(updateTools)};\n${observations}\n${observationFreshness}\nconst RELAY_SEED = ${JSON.stringify(relaySeed)};\n${relay}\n${research}\n${macroScoring}\n${dataImport}\n${sourceResearch}\n${reportContext}\n${stockRelay}\n${fallbackRating}\n${gate5bBoundaries}\n${masterEvidence}\n${masterInputs}\n${issuerContext}\n${crossMarketCore}\n${crossMarket}\n${usSectorCore}\n${usSectorSession}\n${usSectors}\n${marketTimeline}\n${officialNewsModule}\n${macro}`);
+writeFileSync(new URL('./dist/server/index.js', import.meta.url), `const HTML = ${JSON.stringify(html)};\nconst CPI_SEED = ${JSON.stringify(cpiSeed)};\nconst OFFICIAL_UPDATE_TOOLS = ${JSON.stringify(updateTools)};\n${observations}\n${observationFreshness}\nconst RELAY_SEED = ${JSON.stringify(relaySeed)};\n${relay}\n${research}\n${macroScoring}\n${dataImport}\n${sourceResearch}\n${reportContext}\n${stockRelay}\n${fallbackRating}\n${gate5bBoundaries}\n${masterEvidence}\n${masterInputs}\n${issuerContext}\n${crossMarketCore}\n${crossMarket}\n${usSectorCore}\n${usSectorSession}\n${tiingoMarket}\n${tiingoStore}\n${usSectors}\n${tiingoSite}\n${marketTimeline}\n${officialNewsModule}\n${macro}`);
diff --git a/dist/server/index.js b/dist/server/index.js
index 87cd5fb..debda96 100644
--- a/dist/server/index.js
+++ b/dist/server/index.js
@@ -4364,10 +4364,12 @@ const NYSE_HOLIDAYS = new Set([
   '2026-09-07', '2026-11-26', '2026-12-25',
   '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
   '2027-09-06', '2027-11-25', '2027-12-24',
+  '2028-01-17', '2028-02-21', '2028-04-14', '2028-05-29', '2028-06-19', '2028-07-04',
+  '2028-09-04', '2028-11-23', '2028-12-25',
 ]);
-const NYSE_EARLY_CLOSE = new Set(['2026-11-27', '2026-12-24', '2027-11-26']);   // 13:00 收盤
+const NYSE_EARLY_CLOSE = new Set(['2026-11-27', '2026-12-24', '2027-11-26', '2028-07-03', '2028-11-24']);   // 13:00 收盤
 const CALENDAR_FIRST_DAY = '2026-01-01';
-const CALENDAR_LAST_DAY = '2027-12-31';
+const CALENDAR_LAST_DAY = '2028-12-31';
 // 上游排程 23:35 UTC（週一至週五），GitHub 實際延遲約 1.9–2.5 小時（2026-10-14～10-17 的提交時間）；
 // 收盤後 8 小時內還沒發布，才算缺少該交易日。
 const PUBLISH_GRACE_HOURS = 8;
@@ -4440,7 +4442,118 @@ function usSectorFreshness(data, now = Date.now(), opts = {}) {
   return { ok: true, observed, expected, captured_at: data.generated_at };
 }
 
-return {usSectorFreshness,isSession,calendarCovers,NYSE_EARLY_CLOSE,sessionSettledAt};})();
+return {usSectorFreshness,isSession,calendarCovers,NYSE_EARLY_CLOSE,sessionSettledAt,expectedLatestSession};})();
+const TIINGO_MARKET=(()=>{/** Private-owner EOD adapter. Never send raw histories to a public relay or logs. */
+const SECTORS=Object.freeze(['XLB','XLC','XLE','XLF','XLI','XLK','XLP','XLRE','XLU','XLV','XLY']);
+const GLOBAL=Object.freeze(['SPY','EWJ','MCHI','EWU','EWC','INDA','EWT','EWG','EWQ','EWY']);
+const SYMBOLS=Object.freeze([...new Set([...SECTORS,'SPY','RSP',...GLOBAL])]);
+const PRICE_FIELD='adjClose';
+const PROVIDER='tiingo-eod-private-v1';
+const DAY=86400000;
+const safeDate=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&Number.isFinite(Date.parse(s))&&new Date(s).toISOString().slice(0,10)===s;
+const goodHistory=h=>Array.isArray(h)&&h.length>0&&h.every((r,i)=>safeDate(r?.date)&&Number.isFinite(r.price)&&r.price>0&&(!i||r.date>h[i-1].date));
+async function fetchTiingoDaily(symbol,{token,expectedSession,fetchImpl=fetch,now=new Date()}={}) {
+  if(!token)return {status:'source_failed',code:'not_configured'};
+  if(!SYMBOLS.includes(symbol))return {status:'source_failed',code:'invalid_symbol'};
+  if(!safeDate(expectedSession))return {status:'source_failed',code:'invalid_expected_session'};
+  const start=new Date(new Date(now).getTime()-430*DAY).toISOString().slice(0,10);
+  const url=`https://api.tiingo.com/tiingo/daily/${symbol}/prices?startDate=${start}&endDate=${expectedSession}&format=json`;
+  let response;
+  try{response=await fetchImpl(url,{headers:{Authorization:`Token ${token}`,Accept:'application/json'},signal:AbortSignal.timeout(12000)});}catch{return {status:'source_failed',code:'network_error'};}
+  if([401,403,429].includes(response.status))return {status:'source_failed',code:response.status===429?'rate_limited':'unauthorized'};
+  if(!response.ok)return {status:'source_failed',code:'upstream_http_error'};
+  let json;try{json=await response.json();}catch{return {status:'source_failed',code:'invalid_json'};}
+  if(!Array.isArray(json)||!json.length)return {status:'source_failed',code:'empty_data'};
+  const unique=new Map();let excludedFutureRows=0;
+  for(const row of json){
+    const date=typeof row?.date==='string'?row.date.slice(0,10):'';
+    // Filter BEFORE determining observedAt: an intraday/next-session bar cannot invalidate an available completed session.
+    if(safeDate(date)&&date>expectedSession){excludedFutureRows++;continue;}
+    if(!safeDate(date)||date<start||!Number.isFinite(row?.adjClose)||row.adjClose<=0)continue;
+    if(unique.has(date)&&unique.get(date).price!==row.adjClose)return {status:'source_failed',code:'conflicting_duplicate'};
+    unique.set(date,{date,price:row.adjClose});
+  }
+  const history=[...unique.values()].sort((a,b)=>a.date.localeCompare(b.date));
+  return history.length?{status:'ok',symbol,history,observedAt:history.at(-1).date,priceField:PRICE_FIELD,excludedFutureRows}:{status:'source_failed',code:'invalid_prices'};
+}
+function selectSession(result,expectedSession,previous=null){
+  const old=previous?.status==='ok'?previous:previous?.previous||null;
+  const failed=code=>({status:'source_failed',reasonCode:code,source:'tiingo',previous:old});
+  if(!safeDate(expectedSession))return failed('invalid_expected_session');
+  if(result?.status!=='ok')return failed(result?.code||'invalid_response');
+  // Defensive second check for stored/imported adapter results as well as HTTP results.
+  const history=result.history?.filter(r=>r.date<=expectedSession);
+  if(!goodHistory(history))return failed('invalid_prices');
+  const observedAt=history.at(-1).date;
+  if(observedAt!==expectedSession)return {...failed('expected_session_missing'),receivedSession:observedAt};
+  return {...result,history,observedAt,status:'ok',source:'tiingo',priceField:PRICE_FIELD};
+}
+function sma200(history){return goodHistory(history)&&history.length>=200?history.slice(-200).reduce((s,r)=>s+r.price,0)/200:null;}
+function breadth(snapshots){
+  const get=s=>snapshots[s]?.status==='ok'&&goodHistory(snapshots[s].history)?snapshots[s].history:null;
+  const count=symbols=>{let above=0;const missing=[];for(const s of symbols){const h=get(s),ma=sma200(h);if(ma===null)missing.push(s);else if(h.at(-1).price>ma)above++;}return {above,coverage:symbols.length-missing.length,total:symbols.length,missing};};
+  const sectors=count(SECTORS),global=count(GLOBAL),spy=get('SPY'),rsp=get('RSP');
+  let equalWeightRatio20d=null,ratioObservedAt=null;
+  if(spy&&rsp){
+    // Require identical last 21 sessions; an intersected gap would silently change the time window.
+    const a=rsp.slice(-21),b=spy.slice(-21);
+    if(a.length===21&&b.length===21&&a.every((r,i)=>r.date===b[i].date)){
+      equalWeightRatio20d=((a.at(-1).price/b.at(-1).price)/(a[0].price/b[0].price)-1)*100;ratioObservedAt=b.at(-1).date;
+    }
+  }
+  const spyAvailable=sma200(spy)!==null;
+  return {priceField:PRICE_FIELD,sectorBreadth:{...sectors,complete:sectors.coverage===11},globalBreadth:{...global,spyAvailable,ratio:spyAvailable&&global.coverage?global.above/global.coverage:null,denominator:spyAvailable?global.coverage:null,complete:global.coverage===10},equalWeightRatio20d,ratioObservedAt,ratioDirection:equalWeightRatio20d===null?'missing':equalWeightRatio20d>0?'rising':equalWeightRatio20d<0?'falling':'flat'};
+}
+async function refreshPrivateMarket({token,expectedSession,cache,quota,now=new Date(),fetchImpl=fetch}){
+  if(!cache?.get||!cache?.set||!quota?.reserve)throw Error('PRIVATE_PERSISTENT_CACHE_AND_ATOMIC_QUOTA_REQUIRED');
+  const snapshots={};let requests=0,stopCode=null;
+  for(const symbol of SYMBOLS){
+    const old=await cache.get(`tiingo:${symbol}`);
+    if(old?.status==='ok'&&old.observedAt===expectedSession&&old.priceField===PRICE_FIELD){snapshots[symbol]=selectSession(old,expectedSession);continue;}
+    if(old?.expectedSession===expectedSession&&Date.parse(old.retryAt)>now.getTime()){snapshots[symbol]=old;continue;}
+    let result;
+    if(!token)result={status:'source_failed',code:'not_configured'};
+    else if(stopCode)result={status:'source_failed',code:stopCode};
+    else if(!await quota.reserve(symbol,now.getTime()))result={status:'source_failed',code:'quota_guard'};
+    else{requests++;result=await fetchTiingoDaily(symbol,{token,expectedSession,now,fetchImpl});if(['unauthorized','rate_limited'].includes(result.code))stopCode=result.code;}
+    const selected=selectSession(result,expectedSession,old);
+    const resolved={...selected,expectedSession,capturedAt:now.toISOString(),...(selected.status!=='ok'?{retryAt:new Date(now.getTime()+(stopCode==='unauthorized'?12:1)*3600000).toISOString()}: {})};
+    // Store failure/backoff separately from the original last-good observation. Never move the old date.
+    if(!await cache.set(`tiingo:${symbol}`,resolved))throw Error('PRIVATE_CACHE_WRITE_FAILED');
+    snapshots[symbol]=resolved;
+  }
+  return {provider:PROVIDER,expectedSession,checkedAt:now.toISOString(),snapshots,summary:breadth(snapshots),requestCount:requests};
+}
+
+return {SECTORS,GLOBAL,SYMBOLS,PRICE_FIELD,PROVIDER,selectSession,breadth,refreshPrivateMarket};})();
+const TIINGO_STORE=(()=>{/** Shared D1 storage; rolling request limits are reserved by ONE atomic SQL UPDATE. */
+const GUARD_SCHEMA="CREATE TABLE IF NOT EXISTS tiingo_private_guard (id INTEGER PRIMARY KEY CHECK(id=1), requests TEXT NOT NULL DEFAULT '[]', symbols TEXT NOT NULL DEFAULT '{}', month TEXT NOT NULL DEFAULT '', lease_owner TEXT, lease_until INTEGER NOT NULL DEFAULT 0)";
+const RESERVE_SQL=`UPDATE tiingo_private_guard SET
+ requests=json_insert(COALESCE((SELECT json_group_array(json(value)) FROM json_each(requests) WHERE json_extract(value,'$.at')>?), '[]'),'$[#]',json(?)),
+ symbols=CASE WHEN month=? THEN json_set(symbols,?,1) ELSE json_object(?,1) END, month=?
+ WHERE id=1 AND (SELECT count(*) FROM json_each(requests) WHERE json_extract(value,'$.at')>?)<50
+ AND (SELECT count(*) FROM json_each(requests) WHERE json_extract(value,'$.at')>?)<1000
+ AND (month<>? OR json_type(symbols,?) IS NOT NULL OR (SELECT count(*) FROM json_each(symbols))<500)
+ RETURNING id`;
+const LEASE_SQL='UPDATE tiingo_private_guard SET lease_owner=?,lease_until=? WHERE id=1 AND lease_until<=? RETURNING id';
+async function createPrivateStore({db,read,write}){
+  if(!db?.prepare||!read||!write)throw Error('PRIVATE_STORAGE_UNAVAILABLE');
+  await db.prepare(GUARD_SCHEMA).run();
+  await db.prepare('INSERT OR IGNORE INTO tiingo_private_guard (id) VALUES (1)').run();
+  const change=async(sql,args)=>(await db.prepare(sql).bind(...args).all())?.results?.length>0;
+  return {
+    cache:{get:async key=>(await read(key))?.payload||null,set:async(key,value)=>write(key,value,370*86400000)},
+    quota:{reserve:async(symbol,now)=>{
+      if(!/^[A-Z]{1,8}$/.test(symbol)||!Number.isFinite(now))return false;
+      const month=new Date(now).toISOString().slice(0,7),path=`$.${symbol}`;
+      return change(RESERVE_SQL,[now-86400000,JSON.stringify({at:now,symbol}),month,path,symbol,month,now-3600000,now-86400000,month,path]);
+    }},
+    acquire:(owner,now)=>change(LEASE_SQL,[owner,now+15*60000,now]),
+    release:async owner=>db.prepare('UPDATE tiingo_private_guard SET lease_until=0,lease_owner=NULL WHERE id=1 AND lease_owner=?').bind(owner).run()
+  };
+}
+
+return {createPrivateStore};})();
 // Advisory ETF context on the existing Site; never a new score or VETO.
 const US_SECTOR_URL='https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/us_sector_history.json';
 const US_SECTOR_CACHE_KEY='us-sector-history:v1';
@@ -4471,7 +4584,7 @@ function normalizeUSSectorSnapshot(data,now=Date.now()) {
 }
 function evaluateUSSectorContext(snapshot,{referenceDate=null,now=Date.now()}={}) {
   const limits={scoreContribution:0,macroGateOverride:null,vetoOverride:null},unknown=reason=>({...US_SECTOR_CORE.buildSectorReport(),...limits,errorCode:reason,sourceUrl:US_SECTOR_URL,pending:!!snapshot?.pending,refreshing:!!snapshot?.refreshing,referenceDate,summary:`美股板塊 UNKNOWN：${reason}；其他報告繼續輸出，新增評分0。`});
-  let data;try{data=normalizeUSSectorSnapshot(snapshot,now);}catch(error){return {...unknown(snapshot?.error||error.message),sessionFreshness:error.freshness||null};}
+  let data;try{data=snapshot?.provider===TIINGO_MARKET.PROVIDER?normalizeTiingoSnapshot(snapshot.snapshots?snapshot:{...snapshot,snapshots:Object.fromEntries(Object.entries(snapshot.histories||{}).map(([id,rows])=>[id,{symbol:id,status:snapshot.status[id]?.status==='ok'?'ok':'source_failed',priceField:'adjClose',history:rows.map(r=>({date:r.date,price:r.close}))}])),expectedSession:snapshot.sourceObservedAt,checkedAt:snapshot.generated_at},now):normalizeUSSectorSnapshot(snapshot,now);}catch(error){return {...unknown(snapshot?.error||error.message),sessionFreshness:error.freshness||null};}
   if(referenceDate!=null&&(!cmDate(referenceDate)||referenceDate>new Date(now+8*3600000).toISOString().slice(0,10)))return unknown('REFERENCE_DATE_INVALID');
   const sourceCoverage=['SPY',...US_SECTOR_CORE.SECTORS].filter(id=>data.status[id].status==='ok').length;
   const analysis={...data,histories:{},status:{}};
@@ -4482,12 +4595,16 @@ function evaluateUSSectorContext(snapshot,{referenceDate=null,now=Date.now()}={}
   }
   const report=US_SECTOR_CORE.buildSectorReport(analysis),observed=report.observedAt;
   if(!cmDate(observed)||(Date.UTC(new Date(now).getUTCFullYear(),new Date(now).getUTCMonth(),new Date(now).getUTCDate())-Date.parse(observed))/86400000>5)return {...unknown('STALE_OR_NO_COMPLETED_SESSION'),latestSourceObservedAt:data.sourceObservedAt};
-  const benchmarkReturns=US_SECTOR_CORE.returnsFromCloses(analysis.histories.SPY),sectors=Object.fromEntries(Object.entries(report.sectors).map(([id,row])=>[id,{...row,name:US_SECTOR_NAMES[id],returns:row.status==='OK'?US_SECTOR_CORE.returnsFromCloses(analysis.histories[id]):null,sourceUrl:`https://finance.yahoo.com/quote/${id}/`}]));
+  const isTiingo=data.provider===TIINGO_MARKET.PROVIDER,sourceUrl=isTiingo?'https://www.tiingo.com/documentation/end-of-day':US_SECTOR_URL;
+  const benchmarkReturns=US_SECTOR_CORE.returnsFromCloses(analysis.histories.SPY),sectors=Object.fromEntries(Object.entries(report.sectors).map(([id,row])=>[id,{...row,name:US_SECTOR_NAMES[id],returns:row.status==='OK'?US_SECTOR_CORE.returnsFromCloses(analysis.histories[id]):null,sourceUrl:isTiingo?sourceUrl:`https://finance.yahoo.com/quote/${id}/`}]));
+  const breadth=isTiingo?tiingoBreadthForAnalysis(data,referenceDate):null;
   const leads=Object.entries(sectors).filter(([,row])=>row.classification==='LEADING').map(([id])=>id),lags=Object.entries(sectors).filter(([,row])=>row.classification==='LAGGING').map(([id])=>id);
   const labels={BROAD_PARTICIPATION:'多板塊相對領先',NARROW_OR_WEAK:'相對領先集中／偏弱',MIXED_ROTATION:'板塊強弱分化',DATA_INCOMPLETE:'資料不足'};
   const returns=benchmarkReturns.status==='OK'?`SPY 5D／10D／20D ${[5,10,20].map(n=>`${benchmarkReturns['return'+n+'d'].toFixed(2)}%`).join('／')}`:'SPY 報酬 UNKNOWN';
   const summary=`美股板塊 ${report.status}／${labels[report.classification]}：${observed}（資料池最新 ${data.sourceObservedAt}${referenceDate?`，台股基準 ${referenceDate}`:''}）；來源 ${sourceCoverage}/12，板塊有效 ${report.coverage.valid}/11；${returns}。相對 SPY 三個期間皆領先：${leads.join('、')||'無'}；皆落後：${lags.join('、')||'無'}。ETF 價格輪動參考，採 USD 收盤價格報酬，含 Yahoo 非官方來源與ETF追蹤誤差；成分股廣度、資金流與 EPS 修正尚無資料，新增評分0。`;
-  return {...report,...limits,sectors,benchmarkReturns,sourceCoverage:{valid:sourceCoverage,total:12},latestSourceObservedAt:data.sourceObservedAt,referenceDate,sourceUrl:US_SECTOR_URL,errorCode:report.status==='OK'?null:'DATA_INCOMPLETE',pending:false,refreshing:!!snapshot?.refreshing,fetchError:snapshot?.fetchError||null,summary};
+  const breadthText=breadth?`美股寬度 ${breadth.sectorBreadth.above}/${breadth.sectorBreadth.coverage} 有效類股在200日線上（涵蓋${breadth.sectorBreadth.coverage}/11）；RSP/SPY 20日變化 ${breadth.equalWeightRatio20d===null?'缺值':breadth.equalWeightRatio20d.toFixed(2)+'%'}；全球 ${breadth.globalBreadth.spyAvailable?`${breadth.globalBreadth.above}/${breadth.globalBreadth.coverage} 個有效市場在200日線上`:'SPY缺值，全球比例不輸出'}（涵蓋${breadth.globalBreadth.coverage}/10；缺${breadth.globalBreadth.missing.join('、')||'無'}）。`:'';
+  const sourceText=isTiingo?'Tiingo 主要來源，完整 adjClose 歷史獨立重算':`Yahoo 備援來源，獨立 close 序列${snapshot?.primaryError?'；Tiingo '+snapshot.primaryError:''}`;
+  return {...report,...limits,sectors,benchmarkReturns,breadth,sourceRole:isTiingo?'主要來源':'備援來源',priceField:isTiingo?'adjClose':'close',sourceComparison:snapshot?.sourceComparison||null,sourceCoverage:{valid:sourceCoverage,total:12},latestSourceObservedAt:data.sourceObservedAt,referenceDate,sourceUrl,errorCode:report.status==='OK'?null:'DATA_INCOMPLETE',pending:false,refreshing:!!snapshot?.refreshing||!!snapshot?.tiingoRefreshing,fetchError:snapshot?.fetchError||null,summary:`${isTiingo?summary.replace('採 USD 收盤價格報酬，含 Yahoo 非官方來源','採 USD 調整收盤價格報酬，來源為 Tiingo'):summary} ${sourceText}。${breadthText}`};
 }
 async function refreshUSSectorSnapshot(env={}) {
   const previous=await readRuntimeCache(env,US_SECTOR_CACHE_KEY);
@@ -4506,7 +4623,7 @@ async function refreshUSSectorSnapshot(env={}) {
     usSectorMemory={snapshot,expiresAt:Date.now()+15*60000};return snapshot;
   }catch(error){const snapshot={...previous?.payload,pending:false,fetchError:String(error.message||error),...(!previous?.payload?{error:'DATA_UNAVAILABLE'}:{})};usSectorMemory={snapshot,expiresAt:Date.now()+60000};return snapshot;}
 }
-async function readUSSectorSnapshot(env={},ctx={},force=false) {
+async function readYahooSectorSnapshot(env={},ctx={},force=false) {
   if(!force&&usSectorMemory?.expiresAt>Date.now())return usSectorMemory.snapshot;
   const saved=await readRuntimeCache(env,US_SECTOR_CACHE_KEY);
   if(!force&&saved?.fresh){usSectorMemory={snapshot:saved.payload,expiresAt:Date.parse(saved.expiresAt)};return saved.payload;}
@@ -4522,6 +4639,78 @@ async function usSectorReportResponse(request,env={},ctx={}) {
   return Response.json(evaluateUSSectorContext(snapshot,{referenceDate:url.searchParams.get('reference_date')}),{headers:jsonHeaders});
 }
 
+// Private Site adapter. This is deliberately absent from official-data-tools and public relay collectors.
+const TIINGO_PRIVATE_KEY='tiingo:private-market:v1';
+const TIINGO_SOURCE='Tiingo EOD (private owner; adjClose)';
+// Source validation guard only, NOT an investment threshold. Conservative default pending owner review.
+const TIINGO_COMPARISON_MAX_PP=.25;
+let tiingoSiteTask=null;
+function normalizeTiingoSnapshot(snapshot,now=Date.now()){
+  if(snapshot?.provider!==TIINGO_MARKET.PROVIDER)throw Error('TIINGO_PROVIDER_MISMATCH');
+  const expected=US_SECTOR_SESSION.expectedLatestSession(now),captured=Date.parse(snapshot.checkedAt||'');
+  if(!Number.isFinite(captured)||captured>now+60000)throw Error('TIINGO_CAPTURE_INVALID');
+  if(snapshot.expectedSession!==expected)throw Error('TIINGO_LATEST_SESSION_MISSING');
+  const histories={},status={};
+  for(const id of TIINGO_MARKET.SYMBOLS){
+    const entry=snapshot.snapshots?.[id],selected=TIINGO_MARKET.selectSession(entry,expected);
+    const ok=selected.status==='ok'&&entry.symbol===id&&entry.priceField==='adjClose'&&selected.history.every(r=>!US_SECTOR_SESSION.calendarCovers(r.date)||US_SECTOR_SESSION.isSession(r.date));
+    histories[id]=ok?selected.history.map(r=>({date:r.date,close:r.price})):[];
+    status[id]={status:ok?'ok':'unknown',observed_at:ok?expected:null,count:histories[id].length,reason:ok?null:entry?.reasonCode||'TIINGO_INVALID_HISTORY'};
+  }
+  if(status.SPY.status!=='ok')throw Error('TIINGO_BENCHMARK_UNAVAILABLE');
+  return {provider:TIINGO_MARKET.PROVIDER,schema_version:1,source:TIINGO_SOURCE,priceField:'adjClose',histories,status,generated_at:snapshot.checkedAt,sourceObservedAt:expected,sessionFreshness:{ok:true,observed:expected,expected},fetchError:snapshot.fetchError||null};
+}
+function tiingoBreadthForAnalysis(data,referenceDate){
+  const snapshots={};
+  for(const id of TIINGO_MARKET.SYMBOLS){const history=(data.histories[id]||[]).filter(r=>!referenceDate||r.date<referenceDate).map(r=>({date:r.date,price:r.close}));snapshots[id]={status:data.status[id]?.status==='ok'&&history.length?'ok':'source_failed',history};}
+  return TIINGO_MARKET.breadth(snapshots);
+}
+function compareMarketProviders(primary,fallback){
+  const rows=[];
+  if(primary?.sourceObservedAt!==fallback?.sourceObservedAt)return {status:'not_compared',reason:'NO_COMMON_LATEST_SESSION',rows};
+  const a=US_SECTOR_CORE.buildSectorReport(primary),b=US_SECTOR_CORE.buildSectorReport(fallback);
+  if(a.status!=='OK'||b.status!=='OK')return {status:'not_compared',reason:'INCOMPLETE_COMMON_HISTORY',rows};
+  for(const id of US_SECTOR_CORE.SECTORS)for(const n of [5,10,20]){
+    const field=`return${n}d`,differencePp=a.sectors[id].relative[field]-b.sectors[id].relative[field];
+    rows.push({symbol:id,sessions:n,differencePp});
+  }
+  const maxDifferencePp=Math.max(...rows.map(r=>Math.abs(r.differencePp)));
+  return {status:maxDifferencePp>TIINGO_COMPARISON_MAX_PP?'blocked':'within_guard',maxDifferencePp,limitPp:TIINGO_COMPARISON_MAX_PP,limitPurpose:'source_quality_guard_pending_owner_review',priceFields:{primary:'adjClose',fallback:'close'},caveat:'Yahoo close 與 Tiingo adjClose 除息附近可能不同；超過來源保護界線先停用 Tiingo 報告待核，不拼接。',rows};
+}
+async function refreshTiingoSite(env,now=Date.now()){
+  const previous=await readRuntimeCache(env,TIINGO_PRIVATE_KEY);
+  if(!env.TIINGO_API_TOKEN||!env.DB)return {...previous?.payload,fetchError:!env.TIINGO_API_TOKEN?'TIINGO_NOT_CONFIGURED':'PRIVATE_STORAGE_UNAVAILABLE'};
+  let store,owner;
+  try{
+    const expectedSession=US_SECTOR_SESSION.expectedLatestSession(now);
+    store=await TIINGO_STORE.createPrivateStore({db:env.DB,read:key=>readRuntimeCache(env,key),write:(key,value,ttl)=>writeRuntimeCache(env,key,value,ttl)});
+    owner=crypto.randomUUID();
+    if(!await store.acquire(owner,now))return {...previous?.payload,pending:!previous?.payload,refreshing:true,fetchError:'PRIVATE_REFRESH_IN_PROGRESS'};
+    const payload=await TIINGO_MARKET.refreshPrivateMarket({token:env.TIINGO_API_TOKEN,expectedSession,now:new Date(now),cache:store.cache,quota:store.quota});
+    if(!await writeRuntimeCache(env,TIINGO_PRIVATE_KEY,payload,370*86400000))throw Error('PRIVATE_CACHE_WRITE_FAILED');
+    return payload;
+  }catch{return {...previous?.payload,pending:false,fetchError:'PRIVATE_REFRESH_FAILED'};}
+  finally{if(store&&owner)try{await store.release(owner);}catch{}}
+}
+async function readUSSectorSnapshot(env={},ctx={},force=false){
+  const fallback=await readYahooSectorSnapshot(env,ctx,force);
+  if(!env.TIINGO_API_TOKEN)return {...fallback,sourceRole:'備援來源',primaryError:'TIINGO_NOT_CONFIGURED'};
+  const saved=await readRuntimeCache(env,TIINGO_PRIVATE_KEY);
+  let payload=saved?.payload;
+  let ready=false;try{normalizeTiingoSnapshot(payload);ready=true;}catch{}
+  const retryAllowed=!payload?.checkedAt||Date.now()-Date.parse(payload.checkedAt)>=3600000;
+  if((force||!ready&&retryAllowed)&&(force||typeof ctx.waitUntil==='function')){
+    if(!tiingoSiteTask)tiingoSiteTask=refreshTiingoSite(env).finally(()=>{tiingoSiteTask=null;});
+    if(force)payload=await tiingoSiteTask;
+    else if(typeof ctx.waitUntil==='function')try{ctx.waitUntil(tiingoSiteTask);}catch{}
+  }
+  let primary;
+  try{primary=normalizeTiingoSnapshot(payload);}catch(error){return {...fallback,sourceRole:'備援來源',primaryError:payload?.fetchError||error.message,tiingoRefreshing:!!tiingoSiteTask};}
+  const comparison=compareMarketProviders(primary,fallback);
+  if(comparison.status==='blocked')return {...fallback,sourceRole:'備援來源',primaryError:'TIINGO_CROSS_SOURCE_DIFFERENCE',sourceComparison:comparison};
+  return {...primary,sourceRole:'主要來源',sourceComparison:comparison};
+}
+
 // Observation periods, publisher release times and retrieval times are separate.
 const TAIWAN_MARKET_AUDIT_IDS=Object.freeze(['TWSE_TAIEX','TWSE_TOTAL_TRADE_VALUE','TWSE_BREADTH','TPEX_BREADTH','TWSE_MARGIN_BALANCE_NTD','TWSE_SHORT_BALANCE','TWSE_MARGIN_MARKET_CAP_RATIO','TWSE_CREDIT_TRADE_VALUE','TWSE_DAYTRADE']);
 function marketAuditDate(value){return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&Number.isFinite(Date.parse(value))&&new Date(value).toISOString().slice(0,10)===value;}
@@ -5457,7 +5646,7 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
   gates[0].detail+=` ${usSectorContext.summary} ${sectorLines.join('；')}`;
   gates[0].sources.push(...crossMarket.sources);
   gates[0].sources.push(...rateContext.sources);
-  gates[0].sources.push({label:'SPY 與美股11板塊｜GitHub 驗證歷史',url:US_SECTOR_URL,sourceDate:usSectorContext.latestSourceObservedAt||null,detail:usSectorContext.summary,validationStatus:usSectorContext.status==='OK'?'VALIDATED_ETF_REFERENCE':'UNKNOWN'});
+  gates[0].sources.push({label:`SPY 與美股11板塊｜${usSectorContext.sourceRole||'備援來源'}`,url:usSectorContext.sourceUrl||US_SECTOR_URL,sourceDate:usSectorContext.latestSourceObservedAt||null,detail:usSectorContext.summary,validationStatus:usSectorContext.status==='OK'?'VALIDATED_ETF_REFERENCE':'UNKNOWN'});
   gates.find(gate=>gate.id===4).detail+=` 跨市場判讀 ${crossMarket.status}／${crossMarket.label}僅共用上游證據，10D新增分數0。`;
   scoring.crossMarketContext={status:crossMarket.status,classification:crossMarket.classification,scoreContribution:0};
   veto.crossMarketContext={status:crossMarket.status,warning:crossMarket.status==='RED',triggered:false,reason:'跨市場背離不構成獨立否決；已核實VETO優先保留'};
@@ -5910,7 +6099,7 @@ async function siteWatchlistResponse(request, env = {}) {
 }
 
 function summarizeSiteModule(id, payload) {
-  if(id==='usSectors'){const report=evaluateUSSectorContext(payload);return {status:payload?.pending?'pending':report.status==='OK'?'ok':report.coverage.valid?'partial':'missing',usable:report.coverage.valid,total:11,checkedAt:payload?.generated_at||null,observations:Object.entries(report.sectors).map(([key,row])=>({id:key,name:US_SECTOR_NAMES[key],date:row.observedAt,status:row.status,source:US_SECTOR_URL})),judgment:[report.summary],error:report.errorCode||payload?.fetchError||null};}
+  if(id==='usSectors'){const report=evaluateUSSectorContext(payload);return {status:payload?.pending?'pending':report.status==='OK'?'ok':report.coverage.valid?'partial':'missing',usable:report.coverage.valid,total:11,checkedAt:payload?.generated_at||null,observations:Object.entries(report.sectors).map(([key,row])=>({id:key,name:US_SECTOR_NAMES[key],date:row.observedAt,status:row.status,source:report.sourceUrl})),judgment:[report.summary],error:report.errorCode||payload?.fetchError||null};}
   if(id==='crossMarket'){
     const entries=Object.entries(payload?.markets||{}),usable=entries.filter(([,entry])=>entry.status==='ok'&&entry.history?.length>=21).length;
     return {status:payload?.pending?'pending':payload?.snapshotStale?'missing':usable===4&&payload?.status==='ok'?'ok':usable?'partial':'missing',usable,total:4,checkedAt:payload?.generated_at||null,observations:entries.map(([key,entry])=>({id:key,name:CM_NAMES[key],date:entry.history?.at(-1)?.date||null,value:entry.history?.at(-1)?.value??null,status:entry.status,source:entry.source,provider:entry.provider})),judgment:[`四個指數歷史來源 ${usable}/4；上市資金歷史 ${payload?.flows?.history?.length||0}/10 日。資料取得狀態不等於健康脫鉤；個股Forward EPS前後共識另行核驗。`],error:payload?.error||null};
diff --git a/tests/us-sector-session.test.mjs b/tests/us-sector-session.test.mjs
index 9b6a47a..0c9e802 100644
--- a/tests/us-sector-session.test.mjs
+++ b/tests/us-sector-session.test.mjs
@@ -70,5 +70,12 @@ test('NYSE 休市日、提前收盤、夏令時間結束', () => {
 
 test('超出休市日表的年份：失敗而不是放行', () => {
   const data = withSession(real, '2026-10-16');
-  assert.equal(usSectorFreshness(data, T('2028-01-05T12:00:00Z')).code, 'CALENDAR_NOT_COVERED');
+  assert.equal(usSectorFreshness(data, T('2029-01-05T12:00:00Z')).code, 'CALENDAR_NOT_COVERED');
+});
+
+test('2028 official NYSE calendar, Saturday New Year has no Friday substitute, two early closes',()=>{
+  for(const d of ['2028-01-17','2028-02-21','2028-04-14','2028-05-29','2028-06-19','2028-07-04','2028-09-04','2028-11-23','2028-12-25'])assert.equal(isSession(d),false,d);
+  assert.equal(isSession('2027-12-31'),true);
+  assert.equal(isSession('2028-01-03'),true);
+  for(const d of ['2028-07-03','2028-11-24'])assert.equal(new Date(sessionSettledAt(d)).toISOString(),`${d}T${d.endsWith('07-03')?'17':'18'}:15:00.000Z`);
 });
diff --git a/worker/macro.js b/worker/macro.js
index f3973c0..42f3db9 100644
--- a/worker/macro.js
+++ b/worker/macro.js
@@ -780,7 +780,7 @@ function evaluateMasterModel(stock, macro, market, freshness = {}, gateEvidence
   gates[0].detail+=` ${usSectorContext.summary} ${sectorLines.join('；')}`;
   gates[0].sources.push(...crossMarket.sources);
   gates[0].sources.push(...rateContext.sources);
-  gates[0].sources.push({label:'SPY 與美股11板塊｜GitHub 驗證歷史',url:US_SECTOR_URL,sourceDate:usSectorContext.latestSourceObservedAt||null,detail:usSectorContext.summary,validationStatus:usSectorContext.status==='OK'?'VALIDATED_ETF_REFERENCE':'UNKNOWN'});
+  gates[0].sources.push({label:`SPY 與美股11板塊｜${usSectorContext.sourceRole||'備援來源'}`,url:usSectorContext.sourceUrl||US_SECTOR_URL,sourceDate:usSectorContext.latestSourceObservedAt||null,detail:usSectorContext.summary,validationStatus:usSectorContext.status==='OK'?'VALIDATED_ETF_REFERENCE':'UNKNOWN'});
   gates.find(gate=>gate.id===4).detail+=` 跨市場判讀 ${crossMarket.status}／${crossMarket.label}僅共用上游證據，10D新增分數0。`;
   scoring.crossMarketContext={status:crossMarket.status,classification:crossMarket.classification,scoreContribution:0};
   veto.crossMarketContext={status:crossMarket.status,warning:crossMarket.status==='RED',triggered:false,reason:'跨市場背離不構成獨立否決；已核實VETO優先保留'};
@@ -1233,7 +1233,7 @@ async function siteWatchlistResponse(request, env = {}) {
 }
 
 function summarizeSiteModule(id, payload) {
-  if(id==='usSectors'){const report=evaluateUSSectorContext(payload);return {status:payload?.pending?'pending':report.status==='OK'?'ok':report.coverage.valid?'partial':'missing',usable:report.coverage.valid,total:11,checkedAt:payload?.generated_at||null,observations:Object.entries(report.sectors).map(([key,row])=>({id:key,name:US_SECTOR_NAMES[key],date:row.observedAt,status:row.status,source:US_SECTOR_URL})),judgment:[report.summary],error:report.errorCode||payload?.fetchError||null};}
+  if(id==='usSectors'){const report=evaluateUSSectorContext(payload);return {status:payload?.pending?'pending':report.status==='OK'?'ok':report.coverage.valid?'partial':'missing',usable:report.coverage.valid,total:11,checkedAt:payload?.generated_at||null,observations:Object.entries(report.sectors).map(([key,row])=>({id:key,name:US_SECTOR_NAMES[key],date:row.observedAt,status:row.status,source:report.sourceUrl})),judgment:[report.summary],error:report.errorCode||payload?.fetchError||null};}
   if(id==='crossMarket'){
     const entries=Object.entries(payload?.markets||{}),usable=entries.filter(([,entry])=>entry.status==='ok'&&entry.history?.length>=21).length;
     return {status:payload?.pending?'pending':payload?.snapshotStale?'missing':usable===4&&payload?.status==='ok'?'ok':usable?'partial':'missing',usable,total:4,checkedAt:payload?.generated_at||null,observations:entries.map(([key,entry])=>({id:key,name:CM_NAMES[key],date:entry.history?.at(-1)?.date||null,value:entry.history?.at(-1)?.value??null,status:entry.status,source:entry.source,provider:entry.provider})),judgment:[`四個指數歷史來源 ${usable}/4；上市資金歷史 ${payload?.flows?.history?.length||0}/10 日。資料取得狀態不等於健康脫鉤；個股Forward EPS前後共識另行核驗。`],error:payload?.error||null};
diff --git a/worker/us-sector-session.mjs b/worker/us-sector-session.mjs
index f593841..285be4d 100644
--- a/worker/us-sector-session.mjs
+++ b/worker/us-sector-session.mjs
@@ -13,10 +13,12 @@ export const NYSE_HOLIDAYS = new Set([
   '2026-09-07', '2026-11-26', '2026-12-25',
   '2027-01-01', '2027-01-18', '2027-02-15', '2027-03-26', '2027-05-31', '2027-06-18', '2027-07-05',
   '2027-09-06', '2027-11-25', '2027-12-24',
+  '2028-01-17', '2028-02-21', '2028-04-14', '2028-05-29', '2028-06-19', '2028-07-04',
+  '2028-09-04', '2028-11-23', '2028-12-25',
 ]);
-export const NYSE_EARLY_CLOSE = new Set(['2026-11-27', '2026-12-24', '2027-11-26']);   // 13:00 收盤
+export const NYSE_EARLY_CLOSE = new Set(['2026-11-27', '2026-12-24', '2027-11-26', '2028-07-03', '2028-11-24']);   // 13:00 收盤
 export const CALENDAR_FIRST_DAY = '2026-01-01';
-export const CALENDAR_LAST_DAY = '2027-12-31';
+export const CALENDAR_LAST_DAY = '2028-12-31';
 // 上游排程 23:35 UTC（週一至週五），GitHub 實際延遲約 1.9–2.5 小時（2026-10-14～10-17 的提交時間）；
 // 收盤後 8 小時內還沒發布，才算缺少該交易日。
 export const PUBLISH_GRACE_HOURS = 8;
diff --git a/worker/us-sectors.js b/worker/us-sectors.js
index 38372a9..a154881 100644
--- a/worker/us-sectors.js
+++ b/worker/us-sectors.js
@@ -28,7 +28,7 @@ function normalizeUSSectorSnapshot(data,now=Date.now()) {
 }
 function evaluateUSSectorContext(snapshot,{referenceDate=null,now=Date.now()}={}) {
   const limits={scoreContribution:0,macroGateOverride:null,vetoOverride:null},unknown=reason=>({...US_SECTOR_CORE.buildSectorReport(),...limits,errorCode:reason,sourceUrl:US_SECTOR_URL,pending:!!snapshot?.pending,refreshing:!!snapshot?.refreshing,referenceDate,summary:`美股板塊 UNKNOWN：${reason}；其他報告繼續輸出，新增評分0。`});
-  let data;try{data=normalizeUSSectorSnapshot(snapshot,now);}catch(error){return {...unknown(snapshot?.error||error.message),sessionFreshness:error.freshness||null};}
+  let data;try{data=snapshot?.provider===TIINGO_MARKET.PROVIDER?normalizeTiingoSnapshot(snapshot.snapshots?snapshot:{...snapshot,snapshots:Object.fromEntries(Object.entries(snapshot.histories||{}).map(([id,rows])=>[id,{symbol:id,status:snapshot.status[id]?.status==='ok'?'ok':'source_failed',priceField:'adjClose',history:rows.map(r=>({date:r.date,price:r.close}))}])),expectedSession:snapshot.sourceObservedAt,checkedAt:snapshot.generated_at},now):normalizeUSSectorSnapshot(snapshot,now);}catch(error){return {...unknown(snapshot?.error||error.message),sessionFreshness:error.freshness||null};}
   if(referenceDate!=null&&(!cmDate(referenceDate)||referenceDate>new Date(now+8*3600000).toISOString().slice(0,10)))return unknown('REFERENCE_DATE_INVALID');
   const sourceCoverage=['SPY',...US_SECTOR_CORE.SECTORS].filter(id=>data.status[id].status==='ok').length;
   const analysis={...data,histories:{},status:{}};
@@ -39,12 +39,16 @@ function evaluateUSSectorContext(snapshot,{referenceDate=null,now=Date.now()}={}
   }
   const report=US_SECTOR_CORE.buildSectorReport(analysis),observed=report.observedAt;
   if(!cmDate(observed)||(Date.UTC(new Date(now).getUTCFullYear(),new Date(now).getUTCMonth(),new Date(now).getUTCDate())-Date.parse(observed))/86400000>5)return {...unknown('STALE_OR_NO_COMPLETED_SESSION'),latestSourceObservedAt:data.sourceObservedAt};
-  const benchmarkReturns=US_SECTOR_CORE.returnsFromCloses(analysis.histories.SPY),sectors=Object.fromEntries(Object.entries(report.sectors).map(([id,row])=>[id,{...row,name:US_SECTOR_NAMES[id],returns:row.status==='OK'?US_SECTOR_CORE.returnsFromCloses(analysis.histories[id]):null,sourceUrl:`https://finance.yahoo.com/quote/${id}/`}]));
+  const isTiingo=data.provider===TIINGO_MARKET.PROVIDER,sourceUrl=isTiingo?'https://www.tiingo.com/documentation/end-of-day':US_SECTOR_URL;
+  const benchmarkReturns=US_SECTOR_CORE.returnsFromCloses(analysis.histories.SPY),sectors=Object.fromEntries(Object.entries(report.sectors).map(([id,row])=>[id,{...row,name:US_SECTOR_NAMES[id],returns:row.status==='OK'?US_SECTOR_CORE.returnsFromCloses(analysis.histories[id]):null,sourceUrl:isTiingo?sourceUrl:`https://finance.yahoo.com/quote/${id}/`}]));
+  const breadth=isTiingo?tiingoBreadthForAnalysis(data,referenceDate):null;
   const leads=Object.entries(sectors).filter(([,row])=>row.classification==='LEADING').map(([id])=>id),lags=Object.entries(sectors).filter(([,row])=>row.classification==='LAGGING').map(([id])=>id);
   const labels={BROAD_PARTICIPATION:'多板塊相對領先',NARROW_OR_WEAK:'相對領先集中／偏弱',MIXED_ROTATION:'板塊強弱分化',DATA_INCOMPLETE:'資料不足'};
   const returns=benchmarkReturns.status==='OK'?`SPY 5D／10D／20D ${[5,10,20].map(n=>`${benchmarkReturns['return'+n+'d'].toFixed(2)}%`).join('／')}`:'SPY 報酬 UNKNOWN';
   const summary=`美股板塊 ${report.status}／${labels[report.classification]}：${observed}（資料池最新 ${data.sourceObservedAt}${referenceDate?`，台股基準 ${referenceDate}`:''}）；來源 ${sourceCoverage}/12，板塊有效 ${report.coverage.valid}/11；${returns}。相對 SPY 三個期間皆領先：${leads.join('、')||'無'}；皆落後：${lags.join('、')||'無'}。ETF 價格輪動參考，採 USD 收盤價格報酬，含 Yahoo 非官方來源與ETF追蹤誤差；成分股廣度、資金流與 EPS 修正尚無資料，新增評分0。`;
-  return {...report,...limits,sectors,benchmarkReturns,sourceCoverage:{valid:sourceCoverage,total:12},latestSourceObservedAt:data.sourceObservedAt,referenceDate,sourceUrl:US_SECTOR_URL,errorCode:report.status==='OK'?null:'DATA_INCOMPLETE',pending:false,refreshing:!!snapshot?.refreshing,fetchError:snapshot?.fetchError||null,summary};
+  const breadthText=breadth?`美股寬度 ${breadth.sectorBreadth.above}/${breadth.sectorBreadth.coverage} 有效類股在200日線上（涵蓋${breadth.sectorBreadth.coverage}/11）；RSP/SPY 20日變化 ${breadth.equalWeightRatio20d===null?'缺值':breadth.equalWeightRatio20d.toFixed(2)+'%'}；全球 ${breadth.globalBreadth.spyAvailable?`${breadth.globalBreadth.above}/${breadth.globalBreadth.coverage} 個有效市場在200日線上`:'SPY缺值，全球比例不輸出'}（涵蓋${breadth.globalBreadth.coverage}/10；缺${breadth.globalBreadth.missing.join('、')||'無'}）。`:'';
+  const sourceText=isTiingo?'Tiingo 主要來源，完整 adjClose 歷史獨立重算':`Yahoo 備援來源，獨立 close 序列${snapshot?.primaryError?'；Tiingo '+snapshot.primaryError:''}`;
+  return {...report,...limits,sectors,benchmarkReturns,breadth,sourceRole:isTiingo?'主要來源':'備援來源',priceField:isTiingo?'adjClose':'close',sourceComparison:snapshot?.sourceComparison||null,sourceCoverage:{valid:sourceCoverage,total:12},latestSourceObservedAt:data.sourceObservedAt,referenceDate,sourceUrl,errorCode:report.status==='OK'?null:'DATA_INCOMPLETE',pending:false,refreshing:!!snapshot?.refreshing||!!snapshot?.tiingoRefreshing,fetchError:snapshot?.fetchError||null,summary:`${isTiingo?summary.replace('採 USD 收盤價格報酬，含 Yahoo 非官方來源','採 USD 調整收盤價格報酬，來源為 Tiingo'):summary} ${sourceText}。${breadthText}`};
 }
 async function refreshUSSectorSnapshot(env={}) {
   const previous=await readRuntimeCache(env,US_SECTOR_CACHE_KEY);
@@ -63,7 +67,7 @@ async function refreshUSSectorSnapshot(env={}) {
     usSectorMemory={snapshot,expiresAt:Date.now()+15*60000};return snapshot;
   }catch(error){const snapshot={...previous?.payload,pending:false,fetchError:String(error.message||error),...(!previous?.payload?{error:'DATA_UNAVAILABLE'}:{})};usSectorMemory={snapshot,expiresAt:Date.now()+60000};return snapshot;}
 }
-async function readUSSectorSnapshot(env={},ctx={},force=false) {
+async function readYahooSectorSnapshot(env={},ctx={},force=false) {
   if(!force&&usSectorMemory?.expiresAt>Date.now())return usSectorMemory.snapshot;
   const saved=await readRuntimeCache(env,US_SECTOR_CACHE_KEY);
   if(!force&&saved?.fresh){usSectorMemory={snapshot:saved.payload,expiresAt:Date.parse(saved.expiresAt)};return saved.payload;}
diff --git a/tests/tiingo-market.test.mjs b/tests/tiingo-market.test.mjs
new file mode 100644
index 0000000..cc8768b
--- /dev/null
+++ b/tests/tiingo-market.test.mjs
@@ -0,0 +1,67 @@
+import test from 'node:test';
+import assert from 'node:assert/strict';
+import {readFileSync} from 'node:fs';
+import {spawnSync} from 'node:child_process';
+import {SECTORS,GLOBAL,SYMBOLS,fetchTiingoDaily,selectSession,breadth,refreshPrivateMarket} from '../worker/tiingo-market.mjs';
+import {GUARD_SCHEMA,RESERVE_SQL,LEASE_SQL} from '../worker/tiingo-store.mjs';
+const now=new Date('2026-10-20T12:00:00Z'),expectedSession='2026-10-19';
+const history=Array.from({length:270},(_,i)=>({date:new Date(Date.parse(expectedSession)-(269-i)*86400000).toISOString().slice(0,10),price:100+i}));
+const item=(symbol,h=history)=>({status:'ok',symbol,priceField:'adjClose',observedAt:h.at(-1).date,history:h});
+const snapshots=()=>Object.fromEntries(SYMBOLS.map(s=>[s,item(s)]));
+
+test('exact 22 tickers; ten markets, one vote each',()=>{assert.equal(SYMBOLS.length,22);assert.equal(SECTORS.length,11);assert.deepEqual(GLOBAL,['SPY','EWJ','MCHI','EWU','EWC','INDA','EWT','EWG','EWQ','EWY']);});
+test('exclude later-than-expected bars before observedAt; auth header only, adjClose only',async()=>{
+  let call;const response=[{date:'2026-10-16',adjClose:101,close:1},{date:'2026-10-19',adjClose:102,close:2},{date:'2026-10-20',adjClose:9999,close:3}];
+  const r=await fetchTiingoDaily('SPY',{token:'synthetic-test-credential',expectedSession,now,fetchImpl:async(u,o)=>{call={u,o};return Response.json(response);}});
+  assert.equal(r.observedAt,expectedSession);assert.equal(r.history.at(-1).price,102);assert.equal(r.excludedFutureRows,1);assert.equal(selectSession(r,expectedSession).status,'ok');
+  assert.equal(call.o.headers.Authorization,'Token synthetic-test-credential');assert.ok(!call.u.includes('synthetic-test-credential'));assert.ok(!JSON.stringify(r).includes('credential'));
+});
+test('defensive stored-result filtering and missing completed session retain original last-good',()=>{
+  const old=item('SPY',history.slice(0,-1)),future={...item('SPY'),history:[...history,{date:'2026-10-20',price:999}]};
+  assert.equal(selectSession(future,expectedSession,old).observedAt,expectedSession);
+  const failed=selectSession(old,expectedSession,old);assert.equal(failed.status,'source_failed');assert.equal(failed.previous.observedAt,'2026-10-18');
+});
+test('401/403/429/empty/invalid JSON/exception are sanitized',async()=>{
+  for(const status of [401,403,429,503]){const r=await fetchTiingoDaily('SPY',{token:'test-secret',expectedSession,now,fetchImpl:async()=>new Response('test-secret',{status})});assert.equal(r.status,'source_failed');assert.ok(!JSON.stringify(r).includes('test-secret'));}
+  for(const fetchImpl of [async()=>Response.json([]),async()=>new Response('broken'),async()=>{throw Error('test-secret');}])assert.equal((await fetchTiingoDaily('SPY',{token:'test-secret',expectedSession,now,fetchImpl})).status,'source_failed');
+});
+test('conflicting duplicates are rejected, not overwritten',async()=>{const r=await fetchTiingoDaily('SPY',{token:'test',expectedSession,now,fetchImpl:async()=>Response.json([{date:expectedSession,adjClose:1},{date:expectedSession,adjClose:2}])});assert.equal(r.code,'conflicting_duplicate');});
+test('200 samples required; partial global breadth uses observed denominator only, SPY mandatory',()=>{
+  const data=snapshots();data.EWJ=item('EWJ',history.slice(-199));let b=breadth(data);assert.equal(b.globalBreadth.coverage,9);assert.equal(b.globalBreadth.denominator,9);assert.equal(b.globalBreadth.ratio,1);assert.equal(b.globalBreadth.complete,false);
+  data.SPY={status:'source_failed'};b=breadth(data);assert.equal(b.globalBreadth.ratio,null);assert.equal(b.globalBreadth.denominator,null);
+  data.XLK=item('XLK',history.slice(-199));assert.equal(breadth(data).sectorBreadth.coverage,10);
+});
+test('RSP/SPY is exactly 20 aligned sessions, not intersection extended across a hole',()=>{const data=snapshots();assert.equal(breadth(data).equalWeightRatio20d,0);data.RSP.history=data.RSP.history.filter((_,i)=>i!==260);assert.equal(breadth(data).equalWeightRatio20d,null);});
+test('persistent same-session cache survives a fresh refresh invocation without quota/fetch',async()=>{
+  const map=new Map(Object.entries(snapshots()).map(([s,x])=>[`tiingo:${s}`,x]));let calls=0;
+  const cache={get:async k=>map.get(k),set:async(k,x)=>{map.set(k,x);return true;}},quota={reserve:async()=>{calls++;return true;}};
+  const r=await refreshPrivateMarket({token:'test',expectedSession,now,cache,quota,fetchImpl:async()=>{throw Error('should not fetch');}});assert.equal(r.requestCount,0);assert.equal(calls,0);
+});
+test('429 stops the fan-out, persists cooldown; next invocation makes zero requests',async()=>{
+  const map=new Map(),cache={get:async k=>map.get(k),set:async(k,x)=>{map.set(k,x);return true;}},quota={reserve:async()=>true};let calls=0;
+  const args={token:'test',expectedSession,now,cache,quota,fetchImpl:async()=>{calls++;return new Response('',{status:429});}};
+  await refreshPrivateMarket(args);await refreshPrivateMarket(args);assert.equal(calls,1);assert.equal(map.size,22);
+});
+test('without persistent cache and atomic reservation no network call is allowed',async()=>{await assert.rejects(refreshPrivateMarket({token:'test',expectedSession,now,cache:{get(){},set(){}},quota:{canFetch(){},record(){}}}),/ATOMIC_QUOTA/);});
+test('actual SQLite: concurrent reservations cap at 50, rolling-hour boundary, day/month guards and single refresh lease',()=>{
+  const code=`import json,sqlite3,tempfile,concurrent.futures,sys,os
+d=json.load(sys.stdin);tmp=tempfile.TemporaryDirectory();path=os.path.join(tmp.name,'quota.db');now=1792497600000
+def conn():
+ c=sqlite3.connect(path,timeout=30);c.execute('PRAGMA journal_mode=WAL');return c
+c=conn();c.execute(d['schema']);c.execute('INSERT INTO tiingo_private_guard (id) VALUES (1)');c.commit();c.close()
+def reserve(i,t=now):
+ c=conn();sym='SPY';month='2026-10';p='$.SPY';args=[t-86400000,json.dumps({'at':t,'symbol':sym}),month,p,sym,month,t-3600000,t-86400000,month,p]
+ r=c.execute(d['reserve'],args).fetchall();c.commit();c.close();return bool(r)
+with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex: results=list(ex.map(reserve,range(100)))
+assert sum(results)==50,sum(results)
+assert not reserve(0,now+3599999)
+assert reserve(0,now+3600001)
+c=conn();c.execute('UPDATE tiingo_private_guard SET requests=?',(json.dumps([{'at':now-4000000,'symbol':'SPY'}]*1000),));c.commit();assert not reserve(0)
+c.execute('UPDATE tiingo_private_guard SET requests=?, symbols=?, month=?',('[]',json.dumps({str(i):1 for i in range(500)}),'2026-10'));c.commit();assert not reserve(0)
+c.execute('UPDATE tiingo_private_guard SET symbols=?',('{}',));c.commit()
+def lease(i):
+ c=conn();r=c.execute(d['lease'],[str(i),now+900000,now]).fetchall();c.commit();c.close();return bool(r)
+with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: assert sum(ex.map(lease,range(32)))==1
+print('SQL concurrency and all limits passed')`;
+  const r=spawnSync('python',['-c',code],{input:JSON.stringify({schema:GUARD_SCHEMA,reserve:RESERVE_SQL,lease:LEASE_SQL}),encoding:'utf8'});assert.equal(r.status,0,r.stderr);
+});
diff --git a/tests/tiingo-site.test.mjs b/tests/tiingo-site.test.mjs
new file mode 100644
index 0000000..2c93eda
--- /dev/null
+++ b/tests/tiingo-site.test.mjs
@@ -0,0 +1,26 @@
+import test from 'node:test';
+import assert from 'node:assert/strict';
+import {readFileSync} from 'node:fs';
+import {SYMBOLS,PROVIDER} from '../worker/tiingo-market.mjs';
+import {calendarCovers,isSession} from '../worker/us-sector-session.mjs';
+const source=readFileSync(new URL('../dist/server/index.js',import.meta.url),'utf8');
+const api=await import('data:text/javascript;base64,'+Buffer.from(source+'\nexport {normalizeTiingoSnapshot,evaluateUSSectorContext,compareMarketProviders,refreshTiingoSite};').toString('base64'));
+const now=Date.parse('2026-10-20T12:00:00Z'),dates=[];
+for(let t=Date.parse('2025-09-01');t<=Date.parse('2026-10-19');t+=86400000){const day=new Date(t).toISOString().slice(0,10);if(calendarCovers(day)?isSession(day):![0,6].includes(new Date(t).getUTCDay()))dates.push(day);}
+const make=()=>({provider:PROVIDER,expectedSession:'2026-10-19',checkedAt:new Date(now).toISOString(),snapshots:Object.fromEntries(SYMBOLS.map((s,j)=>[s,{symbol:s,status:'ok',priceField:'adjClose',history:dates.map((d,i)=>({date:d,price:100+j+i*(1+j/1000)}))}]))});
+test('Site uses full private adjClose history independently, including prior calendar year',()=>{
+ const p=make(),data=api.normalizeTiingoSnapshot(p,now),r=api.evaluateUSSectorContext(data,{now});
+ assert.equal(r.status,'OK');assert.equal(r.priceField,'adjClose');assert.equal(r.sourceRole,'主要來源');assert.equal(r.coverage.valid,11);
+ const h=p.snapshots.XLK.history;assert.ok(Math.abs(r.sectors.XLK.returns.return20d-(h.at(-1).price/h.at(-21).price-1)*100)<1e-10);
+ assert.equal(r.breadth.sectorBreadth.coverage,11);assert.equal(r.breadth.globalBreadth.coverage,10);assert.equal(r.scoreContribution,0);assert.equal(r.macroGateOverride,null);assert.equal(r.vetoOverride,null);
+ assert.ok(!JSON.stringify(r).includes('"histories"'));assert.ok(!JSON.stringify(r).includes('"snapshots"'));
+});
+test('Taiwan-close cutoff applies to breadth as well as relative returns',()=>{const r=api.evaluateUSSectorContext(api.normalizeTiingoSnapshot(make(),now),{now,referenceDate:'2026-10-19'});assert.equal(r.observedAt,'2026-10-16');assert.equal(r.breadth.ratioObservedAt,'2026-10-16');});
+test('same-date providers compare 33 relative returns; large differences block primary',()=>{
+ const p=api.normalizeTiingoSnapshot(make(),now),y={...structuredClone(p),provider:undefined,source:'Yahoo Finance chart API (unofficial)'};
+ for(const rows of Object.values(y.histories))rows.splice(0,rows.length-66);
+ assert.equal(api.compareMarketProviders(p,y).status,'within_guard');assert.equal(api.compareMarketProviders(p,y).rows.length,33);
+ y.histories.XLK.at(-1).close*=1.5;assert.equal(api.compareMarketProviders(p,y).status,'blocked');
+});
+test('one failed global market is partial; failed SPY makes primary unavailable',()=>{const p=make();p.snapshots.EWJ={status:'source_failed',reasonCode:'rate_limited'};const r=api.evaluateUSSectorContext(api.normalizeTiingoSnapshot(p,now),{now});assert.equal(r.breadth.globalBreadth.coverage,9);assert.equal(r.breadth.globalBreadth.denominator,9);p.snapshots.SPY={status:'source_failed'};assert.throws(()=>api.normalizeTiingoSnapshot(p,now),/BENCHMARK/);});
+test('missing private DB fails closed before any Tiingo request',async()=>{let calls=0;const old=globalThis.fetch;globalThis.fetch=async()=>{calls++;throw Error('unexpected');};try{const r=await api.refreshTiingoSite({TIINGO_API_TOKEN:'test-only'},now);assert.equal(r.fetchError,'PRIVATE_STORAGE_UNAVAILABLE');assert.equal(calls,0);}finally{globalThis.fetch=old;}});
diff --git a/worker/tiingo-market.mjs b/worker/tiingo-market.mjs
new file mode 100644
index 0000000..f20ab34
--- /dev/null
+++ b/worker/tiingo-market.mjs
@@ -0,0 +1,81 @@
+/** Private-owner EOD adapter. Never send raw histories to a public relay or logs. */
+export const SECTORS=Object.freeze(['XLB','XLC','XLE','XLF','XLI','XLK','XLP','XLRE','XLU','XLV','XLY']);
+export const GLOBAL=Object.freeze(['SPY','EWJ','MCHI','EWU','EWC','INDA','EWT','EWG','EWQ','EWY']);
+export const SYMBOLS=Object.freeze([...new Set([...SECTORS,'SPY','RSP',...GLOBAL])]);
+export const PRICE_FIELD='adjClose';
+export const PROVIDER='tiingo-eod-private-v1';
+const DAY=86400000;
+const safeDate=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&Number.isFinite(Date.parse(s))&&new Date(s).toISOString().slice(0,10)===s;
+const goodHistory=h=>Array.isArray(h)&&h.length>0&&h.every((r,i)=>safeDate(r?.date)&&Number.isFinite(r.price)&&r.price>0&&(!i||r.date>h[i-1].date));
+export async function fetchTiingoDaily(symbol,{token,expectedSession,fetchImpl=fetch,now=new Date()}={}) {
+  if(!token)return {status:'source_failed',code:'not_configured'};
+  if(!SYMBOLS.includes(symbol))return {status:'source_failed',code:'invalid_symbol'};
+  if(!safeDate(expectedSession))return {status:'source_failed',code:'invalid_expected_session'};
+  const start=new Date(new Date(now).getTime()-430*DAY).toISOString().slice(0,10);
+  const url=`https://api.tiingo.com/tiingo/daily/${symbol}/prices?startDate=${start}&endDate=${expectedSession}&format=json`;
+  let response;
+  try{response=await fetchImpl(url,{headers:{Authorization:`Token ${token}`,Accept:'application/json'},signal:AbortSignal.timeout(12000)});}catch{return {status:'source_failed',code:'network_error'};}
+  if([401,403,429].includes(response.status))return {status:'source_failed',code:response.status===429?'rate_limited':'unauthorized'};
+  if(!response.ok)return {status:'source_failed',code:'upstream_http_error'};
+  let json;try{json=await response.json();}catch{return {status:'source_failed',code:'invalid_json'};}
+  if(!Array.isArray(json)||!json.length)return {status:'source_failed',code:'empty_data'};
+  const unique=new Map();let excludedFutureRows=0;
+  for(const row of json){
+    const date=typeof row?.date==='string'?row.date.slice(0,10):'';
+    // Filter BEFORE determining observedAt: an intraday/next-session bar cannot invalidate an available completed session.
+    if(safeDate(date)&&date>expectedSession){excludedFutureRows++;continue;}
+    if(!safeDate(date)||date<start||!Number.isFinite(row?.adjClose)||row.adjClose<=0)continue;
+    if(unique.has(date)&&unique.get(date).price!==row.adjClose)return {status:'source_failed',code:'conflicting_duplicate'};
+    unique.set(date,{date,price:row.adjClose});
+  }
+  const history=[...unique.values()].sort((a,b)=>a.date.localeCompare(b.date));
+  return history.length?{status:'ok',symbol,history,observedAt:history.at(-1).date,priceField:PRICE_FIELD,excludedFutureRows}:{status:'source_failed',code:'invalid_prices'};
+}
+export function selectSession(result,expectedSession,previous=null){
+  const old=previous?.status==='ok'?previous:previous?.previous||null;
+  const failed=code=>({status:'source_failed',reasonCode:code,source:'tiingo',previous:old});
+  if(!safeDate(expectedSession))return failed('invalid_expected_session');
+  if(result?.status!=='ok')return failed(result?.code||'invalid_response');
+  // Defensive second check for stored/imported adapter results as well as HTTP results.
+  const history=result.history?.filter(r=>r.date<=expectedSession);
+  if(!goodHistory(history))return failed('invalid_prices');
+  const observedAt=history.at(-1).date;
+  if(observedAt!==expectedSession)return {...failed('expected_session_missing'),receivedSession:observedAt};
+  return {...result,history,observedAt,status:'ok',source:'tiingo',priceField:PRICE_FIELD};
+}
+export function sma200(history){return goodHistory(history)&&history.length>=200?history.slice(-200).reduce((s,r)=>s+r.price,0)/200:null;}
+export function breadth(snapshots){
+  const get=s=>snapshots[s]?.status==='ok'&&goodHistory(snapshots[s].history)?snapshots[s].history:null;
+  const count=symbols=>{let above=0;const missing=[];for(const s of symbols){const h=get(s),ma=sma200(h);if(ma===null)missing.push(s);else if(h.at(-1).price>ma)above++;}return {above,coverage:symbols.length-missing.length,total:symbols.length,missing};};
+  const sectors=count(SECTORS),global=count(GLOBAL),spy=get('SPY'),rsp=get('RSP');
+  let equalWeightRatio20d=null,ratioObservedAt=null;
+  if(spy&&rsp){
+    // Require identical last 21 sessions; an intersected gap would silently change the time window.
+    const a=rsp.slice(-21),b=spy.slice(-21);
+    if(a.length===21&&b.length===21&&a.every((r,i)=>r.date===b[i].date)){
+      equalWeightRatio20d=((a.at(-1).price/b.at(-1).price)/(a[0].price/b[0].price)-1)*100;ratioObservedAt=b.at(-1).date;
+    }
+  }
+  const spyAvailable=sma200(spy)!==null;
+  return {priceField:PRICE_FIELD,sectorBreadth:{...sectors,complete:sectors.coverage===11},globalBreadth:{...global,spyAvailable,ratio:spyAvailable&&global.coverage?global.above/global.coverage:null,denominator:spyAvailable?global.coverage:null,complete:global.coverage===10},equalWeightRatio20d,ratioObservedAt,ratioDirection:equalWeightRatio20d===null?'missing':equalWeightRatio20d>0?'rising':equalWeightRatio20d<0?'falling':'flat'};
+}
+export async function refreshPrivateMarket({token,expectedSession,cache,quota,now=new Date(),fetchImpl=fetch}){
+  if(!cache?.get||!cache?.set||!quota?.reserve)throw Error('PRIVATE_PERSISTENT_CACHE_AND_ATOMIC_QUOTA_REQUIRED');
+  const snapshots={};let requests=0,stopCode=null;
+  for(const symbol of SYMBOLS){
+    const old=await cache.get(`tiingo:${symbol}`);
+    if(old?.status==='ok'&&old.observedAt===expectedSession&&old.priceField===PRICE_FIELD){snapshots[symbol]=selectSession(old,expectedSession);continue;}
+    if(old?.expectedSession===expectedSession&&Date.parse(old.retryAt)>now.getTime()){snapshots[symbol]=old;continue;}
+    let result;
+    if(!token)result={status:'source_failed',code:'not_configured'};
+    else if(stopCode)result={status:'source_failed',code:stopCode};
+    else if(!await quota.reserve(symbol,now.getTime()))result={status:'source_failed',code:'quota_guard'};
+    else{requests++;result=await fetchTiingoDaily(symbol,{token,expectedSession,now,fetchImpl});if(['unauthorized','rate_limited'].includes(result.code))stopCode=result.code;}
+    const selected=selectSession(result,expectedSession,old);
+    const resolved={...selected,expectedSession,capturedAt:now.toISOString(),...(selected.status!=='ok'?{retryAt:new Date(now.getTime()+(stopCode==='unauthorized'?12:1)*3600000).toISOString()}: {})};
+    // Store failure/backoff separately from the original last-good observation. Never move the old date.
+    if(!await cache.set(`tiingo:${symbol}`,resolved))throw Error('PRIVATE_CACHE_WRITE_FAILED');
+    snapshots[symbol]=resolved;
+  }
+  return {provider:PROVIDER,expectedSession,checkedAt:now.toISOString(),snapshots,summary:breadth(snapshots),requestCount:requests};
+}
diff --git a/worker/tiingo-site.js b/worker/tiingo-site.js
new file mode 100644
index 0000000..d21e444
--- /dev/null
+++ b/worker/tiingo-site.js
@@ -0,0 +1,71 @@
+// Private Site adapter. This is deliberately absent from official-data-tools and public relay collectors.
+const TIINGO_PRIVATE_KEY='tiingo:private-market:v1';
+const TIINGO_SOURCE='Tiingo EOD (private owner; adjClose)';
+// Source validation guard only, NOT an investment threshold. Conservative default pending owner review.
+const TIINGO_COMPARISON_MAX_PP=.25;
+let tiingoSiteTask=null;
+function normalizeTiingoSnapshot(snapshot,now=Date.now()){
+  if(snapshot?.provider!==TIINGO_MARKET.PROVIDER)throw Error('TIINGO_PROVIDER_MISMATCH');
+  const expected=US_SECTOR_SESSION.expectedLatestSession(now),captured=Date.parse(snapshot.checkedAt||'');
+  if(!Number.isFinite(captured)||captured>now+60000)throw Error('TIINGO_CAPTURE_INVALID');
+  if(snapshot.expectedSession!==expected)throw Error('TIINGO_LATEST_SESSION_MISSING');
+  const histories={},status={};
+  for(const id of TIINGO_MARKET.SYMBOLS){
+    const entry=snapshot.snapshots?.[id],selected=TIINGO_MARKET.selectSession(entry,expected);
+    const ok=selected.status==='ok'&&entry.symbol===id&&entry.priceField==='adjClose'&&selected.history.every(r=>!US_SECTOR_SESSION.calendarCovers(r.date)||US_SECTOR_SESSION.isSession(r.date));
+    histories[id]=ok?selected.history.map(r=>({date:r.date,close:r.price})):[];
+    status[id]={status:ok?'ok':'unknown',observed_at:ok?expected:null,count:histories[id].length,reason:ok?null:entry?.reasonCode||'TIINGO_INVALID_HISTORY'};
+  }
+  if(status.SPY.status!=='ok')throw Error('TIINGO_BENCHMARK_UNAVAILABLE');
+  return {provider:TIINGO_MARKET.PROVIDER,schema_version:1,source:TIINGO_SOURCE,priceField:'adjClose',histories,status,generated_at:snapshot.checkedAt,sourceObservedAt:expected,sessionFreshness:{ok:true,observed:expected,expected},fetchError:snapshot.fetchError||null};
+}
+function tiingoBreadthForAnalysis(data,referenceDate){
+  const snapshots={};
+  for(const id of TIINGO_MARKET.SYMBOLS){const history=(data.histories[id]||[]).filter(r=>!referenceDate||r.date<referenceDate).map(r=>({date:r.date,price:r.close}));snapshots[id]={status:data.status[id]?.status==='ok'&&history.length?'ok':'source_failed',history};}
+  return TIINGO_MARKET.breadth(snapshots);
+}
+function compareMarketProviders(primary,fallback){
+  const rows=[];
+  if(primary?.sourceObservedAt!==fallback?.sourceObservedAt)return {status:'not_compared',reason:'NO_COMMON_LATEST_SESSION',rows};
+  const a=US_SECTOR_CORE.buildSectorReport(primary),b=US_SECTOR_CORE.buildSectorReport(fallback);
+  if(a.status!=='OK'||b.status!=='OK')return {status:'not_compared',reason:'INCOMPLETE_COMMON_HISTORY',rows};
+  for(const id of US_SECTOR_CORE.SECTORS)for(const n of [5,10,20]){
+    const field=`return${n}d`,differencePp=a.sectors[id].relative[field]-b.sectors[id].relative[field];
+    rows.push({symbol:id,sessions:n,differencePp});
+  }
+  const maxDifferencePp=Math.max(...rows.map(r=>Math.abs(r.differencePp)));
+  return {status:maxDifferencePp>TIINGO_COMPARISON_MAX_PP?'blocked':'within_guard',maxDifferencePp,limitPp:TIINGO_COMPARISON_MAX_PP,limitPurpose:'source_quality_guard_pending_owner_review',priceFields:{primary:'adjClose',fallback:'close'},caveat:'Yahoo close 與 Tiingo adjClose 除息附近可能不同；超過來源保護界線先停用 Tiingo 報告待核，不拼接。',rows};
+}
+async function refreshTiingoSite(env,now=Date.now()){
+  const previous=await readRuntimeCache(env,TIINGO_PRIVATE_KEY);
+  if(!env.TIINGO_API_TOKEN||!env.DB)return {...previous?.payload,fetchError:!env.TIINGO_API_TOKEN?'TIINGO_NOT_CONFIGURED':'PRIVATE_STORAGE_UNAVAILABLE'};
+  let store,owner;
+  try{
+    const expectedSession=US_SECTOR_SESSION.expectedLatestSession(now);
+    store=await TIINGO_STORE.createPrivateStore({db:env.DB,read:key=>readRuntimeCache(env,key),write:(key,value,ttl)=>writeRuntimeCache(env,key,value,ttl)});
+    owner=crypto.randomUUID();
+    if(!await store.acquire(owner,now))return {...previous?.payload,pending:!previous?.payload,refreshing:true,fetchError:'PRIVATE_REFRESH_IN_PROGRESS'};
+    const payload=await TIINGO_MARKET.refreshPrivateMarket({token:env.TIINGO_API_TOKEN,expectedSession,now:new Date(now),cache:store.cache,quota:store.quota});
+    if(!await writeRuntimeCache(env,TIINGO_PRIVATE_KEY,payload,370*86400000))throw Error('PRIVATE_CACHE_WRITE_FAILED');
+    return payload;
+  }catch{return {...previous?.payload,pending:false,fetchError:'PRIVATE_REFRESH_FAILED'};}
+  finally{if(store&&owner)try{await store.release(owner);}catch{}}
+}
+async function readUSSectorSnapshot(env={},ctx={},force=false){
+  const fallback=await readYahooSectorSnapshot(env,ctx,force);
+  if(!env.TIINGO_API_TOKEN)return {...fallback,sourceRole:'備援來源',primaryError:'TIINGO_NOT_CONFIGURED'};
+  const saved=await readRuntimeCache(env,TIINGO_PRIVATE_KEY);
+  let payload=saved?.payload;
+  let ready=false;try{normalizeTiingoSnapshot(payload);ready=true;}catch{}
+  const retryAllowed=!payload?.checkedAt||Date.now()-Date.parse(payload.checkedAt)>=3600000;
+  if((force||!ready&&retryAllowed)&&(force||typeof ctx.waitUntil==='function')){
+    if(!tiingoSiteTask)tiingoSiteTask=refreshTiingoSite(env).finally(()=>{tiingoSiteTask=null;});
+    if(force)payload=await tiingoSiteTask;
+    else if(typeof ctx.waitUntil==='function')try{ctx.waitUntil(tiingoSiteTask);}catch{}
+  }
+  let primary;
+  try{primary=normalizeTiingoSnapshot(payload);}catch(error){return {...fallback,sourceRole:'備援來源',primaryError:payload?.fetchError||error.message,tiingoRefreshing:!!tiingoSiteTask};}
+  const comparison=compareMarketProviders(primary,fallback);
+  if(comparison.status==='blocked')return {...fallback,sourceRole:'備援來源',primaryError:'TIINGO_CROSS_SOURCE_DIFFERENCE',sourceComparison:comparison};
+  return {...primary,sourceRole:'主要來源',sourceComparison:comparison};
+}
diff --git a/worker/tiingo-store.mjs b/worker/tiingo-store.mjs
new file mode 100644
index 0000000..cdc0761
--- /dev/null
+++ b/worker/tiingo-store.mjs
@@ -0,0 +1,26 @@
+/** Shared D1 storage; rolling request limits are reserved by ONE atomic SQL UPDATE. */
+export const GUARD_SCHEMA="CREATE TABLE IF NOT EXISTS tiingo_private_guard (id INTEGER PRIMARY KEY CHECK(id=1), requests TEXT NOT NULL DEFAULT '[]', symbols TEXT NOT NULL DEFAULT '{}', month TEXT NOT NULL DEFAULT '', lease_owner TEXT, lease_until INTEGER NOT NULL DEFAULT 0)";
+export const RESERVE_SQL=`UPDATE tiingo_private_guard SET
+ requests=json_insert(COALESCE((SELECT json_group_array(json(value)) FROM json_each(requests) WHERE json_extract(value,'$.at')>?), '[]'),'$[#]',json(?)),
+ symbols=CASE WHEN month=? THEN json_set(symbols,?,1) ELSE json_object(?,1) END, month=?
+ WHERE id=1 AND (SELECT count(*) FROM json_each(requests) WHERE json_extract(value,'$.at')>?)<50
+ AND (SELECT count(*) FROM json_each(requests) WHERE json_extract(value,'$.at')>?)<1000
+ AND (month<>? OR json_type(symbols,?) IS NOT NULL OR (SELECT count(*) FROM json_each(symbols))<500)
+ RETURNING id`;
+export const LEASE_SQL='UPDATE tiingo_private_guard SET lease_owner=?,lease_until=? WHERE id=1 AND lease_until<=? RETURNING id';
+export async function createPrivateStore({db,read,write}){
+  if(!db?.prepare||!read||!write)throw Error('PRIVATE_STORAGE_UNAVAILABLE');
+  await db.prepare(GUARD_SCHEMA).run();
+  await db.prepare('INSERT OR IGNORE INTO tiingo_private_guard (id) VALUES (1)').run();
+  const change=async(sql,args)=>(await db.prepare(sql).bind(...args).all())?.results?.length>0;
+  return {
+    cache:{get:async key=>(await read(key))?.payload||null,set:async(key,value)=>write(key,value,370*86400000)},
+    quota:{reserve:async(symbol,now)=>{
+      if(!/^[A-Z]{1,8}$/.test(symbol)||!Number.isFinite(now))return false;
+      const month=new Date(now).toISOString().slice(0,7),path=`$.${symbol}`;
+      return change(RESERVE_SQL,[now-86400000,JSON.stringify({at:now,symbol}),month,path,symbol,month,now-3600000,now-86400000,month,path]);
+    }},
+    acquire:(owner,now)=>change(LEASE_SQL,[owner,now+15*60000,now]),
+    release:async owner=>db.prepare('UPDATE tiingo_private_guard SET lease_until=0,lease_owner=NULL WHERE id=1 AND lease_owner=?').bind(owner).run()
+  };
+}

```
