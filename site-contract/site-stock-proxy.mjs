// Copy this into a server-capable Sites backend; never use in browser code.
export async function siteStockProxy(request,env,fetchImpl=fetch){
 const u=new URL(request.url),ticker=u.searchParams.get('ticker');
 const json=(data,status)=>new Response(JSON.stringify(data),{status,headers:{'content-type':'application/json','cache-control':'no-store'}});
 if(request.method!=='GET')return json({error:'METHOD_NOT_ALLOWED'},405);
 if(!/^[0-9]{4,6}$/.test(ticker||''))return json({error:'INVALID_TICKER'},400);
 if(!env?.RELAY_ORIGIN||!env?.SNAPSHOT_READ_TOKEN)return json({error:'RELAY_NOT_CONFIGURED'},503);
 let target;
 try {
  target=new URL('/api/stock-report',env.RELAY_ORIGIN);
  if(target.protocol!=='https:')throw new Error('INVALID_ORIGIN');
  target.searchParams.set('ticker',ticker);
 }catch{return json({error:'INVALID_RELAY_ORIGIN'},503);}
 try{
  const response=await fetchImpl(target.toString(),{headers:{Authorization:'Bearer '+env.SNAPSHOT_READ_TOKEN,Accept:'application/json'}});
  if(!response.ok)return json({error:'RELAY_UNAVAILABLE',upstream_status:response.status},response.status===401?503:response.status);
  const payload=await response.json();
  if(payload?.report?.ticker!==ticker)return json({error:'RELAY_TICKER_MISMATCH'},502);
  return json(payload,200);
 }catch{return json({error:'RELAY_UNAVAILABLE'},503);}
}
