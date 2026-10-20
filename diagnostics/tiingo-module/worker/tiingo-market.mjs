/** Private-owner EOD adapter. Never send raw histories to a public relay or logs. */
export const SECTORS=Object.freeze(['XLB','XLC','XLE','XLF','XLI','XLK','XLP','XLRE','XLU','XLV','XLY']);
export const GLOBAL=Object.freeze(['SPY','EWJ','MCHI','EWU','EWC','INDA','EWT','EWG','EWQ','EWY']);
export const SYMBOLS=Object.freeze([...new Set([...SECTORS,'SPY','RSP',...GLOBAL])]);
export const PRICE_FIELD='adjClose';
export const PROVIDER='tiingo-eod-private-v1';
const DAY=86400000;
const safeDate=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&Number.isFinite(Date.parse(s))&&new Date(s).toISOString().slice(0,10)===s;
const goodHistory=h=>Array.isArray(h)&&h.length>0&&h.every((r,i)=>safeDate(r?.date)&&Number.isFinite(r.price)&&r.price>0&&(!i||r.date>h[i-1].date));
export async function fetchTiingoDaily(symbol,{token,expectedSession,fetchImpl=fetch,now=new Date()}={}) {
  if(!token)return {status:'source_failed',code:'not_configured'};
  if(!SYMBOLS.includes(symbol))return {status:'source_failed',code:'invalid_symbol'};
  if(!safeDate(expectedSession))return {status:'source_failed',code:'invalid_expected_session'};
  const start=new Date(new Date(now).getTime()-430*DAY).toISOString().slice(0,10);
  const url=`https://api.tiingo.com/tiingo/daily/${symbol}/prices?startDate=${start}&endDate=${expectedSession}&format=json`;
  let response;
  try{response=await fetchImpl(url,{headers:{Authorization:`Token ${token}`,Accept:'application/json'},signal:AbortSignal.timeout(12000)});}catch{return {status:'source_failed',code:'network_error'};}
  if([401,403,429].includes(response.status))return {status:'source_failed',code:response.status===429?'rate_limited':'unauthorized'};
  if(!response.ok)return {status:'source_failed',code:'upstream_http_error'};
  let json;try{json=await response.json();}catch{return {status:'source_failed',code:'invalid_json'};}
  if(!Array.isArray(json)||!json.length)return {status:'source_failed',code:'empty_data'};
  const unique=new Map();let excludedFutureRows=0;
  for(const row of json){
    const date=typeof row?.date==='string'?row.date.slice(0,10):'';
    // Filter BEFORE determining observedAt: an intraday/next-session bar cannot invalidate an available completed session.
    if(safeDate(date)&&date>expectedSession){excludedFutureRows++;continue;}
    if(!safeDate(date)||date<start||!Number.isFinite(row?.adjClose)||row.adjClose<=0)continue;
    if(unique.has(date)&&unique.get(date).price!==row.adjClose)return {status:'source_failed',code:'conflicting_duplicate'};
    unique.set(date,{date,price:row.adjClose});
  }
  const history=[...unique.values()].sort((a,b)=>a.date.localeCompare(b.date));
  return history.length?{status:'ok',symbol,history,observedAt:history.at(-1).date,priceField:PRICE_FIELD,excludedFutureRows}:{status:'source_failed',code:'invalid_prices'};
}
export function selectSession(result,expectedSession,previous=null){
  const old=previous?.status==='ok'?previous:previous?.previous||null;
  const failed=code=>({status:'source_failed',reasonCode:code,source:'tiingo',previous:old});
  if(!safeDate(expectedSession))return failed('invalid_expected_session');
  if(result?.status!=='ok')return failed(result?.code||'invalid_response');
  // Defensive second check for stored/imported adapter results as well as HTTP results.
  const history=result.history?.filter(r=>r.date<=expectedSession);
  if(!goodHistory(history))return failed('invalid_prices');
  const observedAt=history.at(-1).date;
  if(observedAt!==expectedSession)return {...failed('expected_session_missing'),receivedSession:observedAt};
  return {...result,history,observedAt,status:'ok',source:'tiingo',priceField:PRICE_FIELD};
}
export function sma200(history){return goodHistory(history)&&history.length>=200?history.slice(-200).reduce((s,r)=>s+r.price,0)/200:null;}
export function breadth(snapshots){
  const get=s=>snapshots[s]?.status==='ok'&&goodHistory(snapshots[s].history)?snapshots[s].history:null;
  const count=symbols=>{let above=0;const missing=[];for(const s of symbols){const h=get(s),ma=sma200(h);if(ma===null)missing.push(s);else if(h.at(-1).price>ma)above++;}return {above,coverage:symbols.length-missing.length,total:symbols.length,missing};};
  const sectors=count(SECTORS),global=count(GLOBAL),spy=get('SPY'),rsp=get('RSP');
  let equalWeightRatio20d=null,ratioObservedAt=null;
  if(spy&&rsp){
    // Require identical last 21 sessions; an intersected gap would silently change the time window.
    const a=rsp.slice(-21),b=spy.slice(-21);
    if(a.length===21&&b.length===21&&a.every((r,i)=>r.date===b[i].date)){
      equalWeightRatio20d=((a.at(-1).price/b.at(-1).price)/(a[0].price/b[0].price)-1)*100;ratioObservedAt=b.at(-1).date;
    }
  }
  const spyAvailable=sma200(spy)!==null;
  return {priceField:PRICE_FIELD,sectorBreadth:{...sectors,complete:sectors.coverage===11},globalBreadth:{...global,spyAvailable,ratio:spyAvailable&&global.coverage?global.above/global.coverage:null,denominator:spyAvailable?global.coverage:null,complete:global.coverage===10},equalWeightRatio20d,ratioObservedAt,ratioDirection:equalWeightRatio20d===null?'missing':equalWeightRatio20d>0?'rising':equalWeightRatio20d<0?'falling':'flat'};
}
export async function refreshPrivateMarket({token,expectedSession,cache,quota,now=new Date(),fetchImpl=fetch}){
  if(!cache?.get||!cache?.set||!quota?.reserve)throw Error('PRIVATE_PERSISTENT_CACHE_AND_ATOMIC_QUOTA_REQUIRED');
  const snapshots={};let requests=0,stopCode=null;
  for(const symbol of SYMBOLS){
    const old=await cache.get(`tiingo:${symbol}`);
    if(old?.status==='ok'&&old.observedAt===expectedSession&&old.priceField===PRICE_FIELD){snapshots[symbol]=selectSession(old,expectedSession);continue;}
    if(old?.expectedSession===expectedSession&&Date.parse(old.retryAt)>now.getTime()){snapshots[symbol]=old;continue;}
    let result;
    if(!token)result={status:'source_failed',code:'not_configured'};
    else if(stopCode)result={status:'source_failed',code:stopCode};
    else if(!await quota.reserve(symbol,now.getTime()))result={status:'source_failed',code:'quota_guard'};
    else{requests++;result=await fetchTiingoDaily(symbol,{token,expectedSession,now,fetchImpl});if(['unauthorized','rate_limited'].includes(result.code))stopCode=result.code;}
    const selected=selectSession(result,expectedSession,old);
    const resolved={...selected,expectedSession,capturedAt:now.toISOString(),...(selected.status!=='ok'?{retryAt:new Date(now.getTime()+(stopCode==='unauthorized'?12:1)*3600000).toISOString()}: {})};
    // Store failure/backoff separately from the original last-good observation. Never move the old date.
    if(!await cache.set(`tiingo:${symbol}`,resolved))throw Error('PRIVATE_CACHE_WRITE_FAILED');
    snapshots[symbol]=resolved;
  }
  return {provider:PROVIDER,expectedSession,checkedAt:now.toISOString(),snapshots,summary:breadth(snapshots),requestCount:requests};
}
