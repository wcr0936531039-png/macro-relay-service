import {normalizeTicker,normalizeObservation} from './stock-source.mjs';
const ENDPOINT='https://api.finmindtrade.com/api/v4/data';
export function parseFinMindPrice(payload,ticker){
 ticker=normalizeTicker(ticker);
 if(payload?.status!==200||!Array.isArray(payload.data))throw new Error('FINMIND_UNAVAILABLE');
 const rows=payload.data.filter(r=>String(r.stock_id)===ticker&&/^\d{4}-\d{2}-\d{2}$/.test(r.date)).sort((a,b)=>a.date.localeCompare(b.date));
 if(!rows.length)throw new Error('FINMIND_NO_DATA');
 const last=rows.at(-1);
 const metrics=[['close','close'],['volume_shares','Trading_Volume'],['turnover_twd','Trading_money']];
 return metrics.map(([metric,field])=>{
   const n=Number(last[field]);
   if(!Number.isFinite(n)||n<0)throw new Error('FINMIND_INVALID_'+field);
   return normalizeObservation({ticker,metric,value:n,observed_at:last.date,source:'FinMind TaiwanStockPrice (secondary)',source_url:'https://finmind.github.io/',period:'daily'});
 });
}
export async function fetchFinMindPrice({ticker,fetchImpl=fetch,timeoutMs=12000,token,days=14}){
 ticker=normalizeTicker(ticker);
 const since=new Date(Date.now()-days*86400000).toISOString().slice(0,10);
 const params=new URLSearchParams({dataset:'TaiwanStockPrice',data_id:ticker,start_date:since});
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),timeoutMs);
 try{
  const response=await fetchImpl(ENDPOINT+'?'+params,{signal:controller.signal,headers:token?{Authorization:'Bearer '+token}:{}});
  if(!response.ok)throw new Error('FINMIND_HTTP_'+response.status);
  return parseFinMindPrice(await response.json(),ticker);
 }finally{clearTimeout(timer);}
}
