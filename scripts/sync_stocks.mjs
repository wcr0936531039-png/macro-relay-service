import {fetchTwseStockDay} from '../site-contract/twse-stock-day.mjs';
import {fetchTpexQuotes} from '../site-contract/tpex-quotes.mjs';
const OTC=new Set(['8299','5289','5009']);
import {normalizeTicker} from '../site-contract/stock-source.mjs';
const tickers=(process.env.STOCK_TICKERS||'8299,5289,2404,5009').split(',').map(normalizeTicker);
const month=new Date().toISOString().slice(0,7);
const account=process.env.CF_ACCOUNT_ID,namespace=process.env.CF_KV_NAMESPACE_ID,token=process.env.CF_API_TOKEN;
const dryRun=process.env.DRY_RUN!=='false';
const summary=[];
for(const ticker of tickers){
  try{
    const rows=OTC.has(ticker)?await fetchTpexQuotes({ticker}):await fetchTwseStockDay({ticker,month});
    const valid=rows.filter(x=>x.status==='ok');
    if(!valid.length){summary.push({ticker,status:'missing',reason:'NO_VALID_ROWS'});continue;}
    const key='stock_snapshot_v2:'+ticker;
    // Snapshot is published only if credentials are explicitly supplied.
    if(!dryRun){
      if(!account||!namespace||!token)throw new Error('CLOUDFLARE_NOT_CONFIGURED');
      const endpoint='https://api.cloudflare.com/client/v4/accounts/'+encodeURIComponent(account)+'/storage/kv/namespaces/'+encodeURIComponent(namespace)+'/values/'+encodeURIComponent(key);
      const previousResponse=await fetch(endpoint,{headers:{Authorization:'Bearer '+token}});
      if(!previousResponse.ok && previousResponse.status!==404)throw new Error('KV_READ_HTTP_'+previousResponse.status);
      const previous=previousResponse.ok?await previousResponse.json():null;
      if(previous && (previous.schema_version!==2||previous.ticker!==ticker||!Array.isArray(previous.observations)))throw new Error('KV_EXISTING_SCHEMA_MISMATCH');
      const combined=new Map();
      for(const item of [...(previous?.observations||[]),...valid])combined.set(item.metric+'|'+item.observed_at,item);
      const snapshot={schema_version:2,ticker,updated_at:new Date().toISOString(),observations:[...combined.values()]};
      const response=await fetch(endpoint,{method:'PUT',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify(snapshot)});
      if(!response.ok)throw new Error('KV_HTTP_'+response.status);
    }
    summary.push({ticker,market:OTC.has(ticker)?'TPEx':'TWSE',status:dryRun?'validated':'published',count:valid.length,last_observed:valid.at(-1).observed_at});
  }catch(error){summary.push({ticker,status:'error',reason:String(error?.message||error)});}
}
console.log(JSON.stringify({month,dry_run:dryRun,summary},null,2));
if(summary.some(x=>x.status==='error'||x.status==='missing'))process.exitCode=1;
