import {normalizeTicker,normalizeObservation} from './stock-source.mjs';
const TIMEOUT_MS=10000;
function rocDate(value) {
  const parts=String(value).trim().split('/');
  if(parts.length!==3) throw new Error('INVALID_TWSE_DATE');
  const [y,m,d]=parts.map(Number);
  const date=new Date(Date.UTC(y+1911,m-1,d));
  if(!Number.isInteger(y)||!Number.isInteger(m)||!Number.isInteger(d)||date.getUTCFullYear()!==y+1911||date.getUTCMonth()!==m-1||date.getUTCDate()!==d) throw new Error('INVALID_TWSE_DATE');
  return date.toISOString().slice(0,10);
}
function number(value) {
  const s=String(value??'').replaceAll(',','').trim();
  if(s==='--'||s===''||s==='-') return null;
  const n=Number(s);return Number.isFinite(n)?n:null;
}
export function parseTwseStockDay(payload,ticker) {
  ticker=normalizeTicker(ticker);
  if(!payload||payload.stat!=='OK'||!Array.isArray(payload.fields)||!Array.isArray(payload.data)) throw new Error('TWSE_UNAVAILABLE');
  const col=key=>payload.fields.findIndex(x=>String(x).includes(key));
  const dateCol=col('日期'),closeCol=col('收盤價'),volumeCol=col('成交股數'),turnoverCol=col('成交金額');
  if([dateCol,closeCol,volumeCol,turnoverCol].some(x=>x<0)) throw new Error('TWSE_SCHEMA_CHANGED');
  const out=[];
  for(const row of payload.data){
    if(!Array.isArray(row)) continue;
    const observed_at=rocDate(row[dateCol]);
    for(const [metric,index] of [['close',closeCol],['volume_shares',volumeCol],['turnover_twd',turnoverCol]]) {
      out.push(normalizeObservation({ticker,metric,value:number(row[index]),observed_at,source:'TWSE STOCK_DAY',source_url:'https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY',period:'daily'}));
    }
  }
  return out;
}
export async function fetchTwseStockDay({ticker,month,fetchImpl=fetch,timeoutMs=TIMEOUT_MS}) {
  ticker=normalizeTicker(ticker);
  if(!/^\\d{4}-\\d{2}$/.test(month)) throw new Error('INVALID_MONTH');
  const [y,m]=month.split('-').map(Number);
  if(m<1||m>12) throw new Error('INVALID_MONTH');
  const url=new URL('https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY');
  url.searchParams.set('date',String(y)+String(m).padStart(2,'0')+'01');
  url.searchParams.set('stockNo',ticker);
  url.searchParams.set('response','json');
  const controller=new AbortController();
  const timer=setTimeout(()=>controller.abort(),timeoutMs);
  try {
    const response=await fetchImpl(url.toString(),{headers:{Accept:'application/json','User-Agent':'Mozilla/5.0 (compatible; MacroRelay/1.0)'},signal:controller.signal});
    if(!response.ok) throw new Error('TWSE_HTTP_'+response.status);
    return parseTwseStockDay(await response.json(),ticker);
  } finally {clearTimeout(timer);}
}
