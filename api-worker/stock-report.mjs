import {loadStockSnapshot} from '../site-contract/stock-store.mjs';
import {assembleStockReport} from '../site-contract/assemble-report.mjs';
// Private endpoint for the existing site server; do not expose bearer tokens to browsers.
const json=(body,status=200)=>new Response(JSON.stringify(body),{status,headers:{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});
export async function handleStockReport(request,env,now=Date.now()){
  const url=new URL(request.url);
  if(url.pathname!=='/api/stock-report')return json({error:'NOT_FOUND'},404);
  if(request.method!=='GET')return new Response(null,{status:405,headers:{Allow:'GET'}});
  if(!env?.SNAPSHOT_READ_TOKEN||!env?.MACRO_KV?.get)return json({error:'NOT_CONFIGURED'},503);
  if(request.headers.get('Authorization')!==`Bearer ${env.SNAPSHOT_READ_TOKEN}`)return json({error:'UNAUTHORIZED'},401);
  const ticker=url.searchParams.get('ticker');
  if(!/^[0-9]{4,6}$/.test(ticker??''))return json({error:'INVALID_TICKER'},400);
  try {
    const snapshot=await loadStockSnapshot(env.MACRO_KV,ticker);
    if(!snapshot)return json({status:'uninitialized',ticker,error:'STOCK_SNAPSHOT_NOT_INITIALIZED'},503);
    const report=assembleStockReport({ticker,observations:snapshot.observations,requiredMetrics:['close','volume_shares','turnover_twd']});
    const updated=Date.parse(snapshot.updated_at);
    const stale=!Number.isFinite(updated)||updated>now+60000||now-updated>36*3600000;
    return json({status:stale?'stale':report.status,is_stale:stale,updated_at:snapshot.updated_at,report});
  }catch{return json({status:'unavailable',error:'STOCK_REPORT_UNAVAILABLE'},503);}
}
