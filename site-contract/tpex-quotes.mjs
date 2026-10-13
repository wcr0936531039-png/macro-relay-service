import {normalizeTicker,normalizeObservation} from './stock-source.mjs';
const URL='https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes';
function isoRoc(raw) {
 const s=String(raw??'').trim();
 if(!/^[0-9]{7}$/.test(s))throw new Error('INVALID_TPEX_DATE');
 const year=Number(s.slice(0,3))+1911,month=Number(s.slice(3,5)),day=Number(s.slice(5,7));
 const dt=new Date(Date.UTC(year,month-1,day));
 if(dt.getUTCFullYear()!==year||dt.getUTCMonth()!==month-1||dt.getUTCDate()!==day)throw new Error('INVALID_TPEX_DATE');
 return dt.toISOString().slice(0,10);
}
function value(raw){
 const s=String(raw??'').replaceAll(',','').trim();
 if(!s||s==='--'||s==='-')return null;
 const n=Number(s);return Number.isFinite(n)?n:null;
}
export function parseTpexQuotes(payload,ticker) {
 ticker=normalizeTicker(ticker);
 if(!Array.isArray(payload))throw new Error('TPEX_UNAVAILABLE');
 const match=payload.find(row=>String(row?.SecuritiesCompanyCode??'').trim()===ticker);
 if(!match)throw new Error('TPEX_TICKER_NOT_FOUND');
 const observed_at=isoRoc(match.Date);
 const metrics=[['close','Close'],['volume_shares','TradingShares'],['turnover_twd','TransactionAmount']];
 for(const [,field] of metrics)if(!(field in match))throw new Error('TPEX_SCHEMA_CHANGED');
 return metrics.map(([metric,field])=>normalizeObservation({ticker,metric,value:value(match[field]),observed_at,source:'TPEx mainboard daily close quotes',source_url:URL,period:'daily'}));
}
export async function fetchTpexQuotes({ticker,fetchImpl=fetch,timeoutMs=15000}){
 ticker=normalizeTicker(ticker);
 const controller=new AbortController();
 const timer=setTimeout(()=>controller.abort(),timeoutMs);
 try{
   const response=await fetchImpl(URL,{headers:{Accept:'application/json'},signal:controller.signal});
   if(!response.ok)throw new Error('TPEX_HTTP_'+response.status);
   return parseTpexQuotes(await response.json(),ticker);
 }finally{clearTimeout(timer);}
}
