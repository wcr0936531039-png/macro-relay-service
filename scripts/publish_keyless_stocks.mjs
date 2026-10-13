import {writeFile,mkdir} from 'node:fs/promises';
import {fetchTwseStockDay} from '../site-contract/twse-stock-day.mjs';
import {fetchTpexQuotes} from '../site-contract/tpex-quotes.mjs';
const codes=['8299','5289','2404','5009'];
const month=new Date().toISOString().slice(0,7);
const generated_at=new Date().toISOString();
const stocks={};
let errors=0;
for(const ticker of codes){
 try{
  const rows=ticker==='2404'?await fetchTwseStockDay({ticker,month}):await fetchTpexQuotes({ticker});
  const observations=rows.filter(row=>row.status==='ok');
  if(!observations.length)throw new Error('NO_VALID_OBSERVATIONS');
  stocks[ticker]={schema_version:2,ticker,updated_at:generated_at,observations};
 }catch(e){stocks[ticker]={status:'unavailable',reason:String(e?.message||e)};errors++;}
}
await mkdir('data',{recursive:true});
await writeFile('data/stock_snapshots_v2.json',JSON.stringify({schema_version:2,generated_at,stocks},null,2)+'\n');
console.log(JSON.stringify({generated_at,results:Object.fromEntries(Object.entries(stocks).map(([k,v])=>[k,v.status||'validated']))}));
if(errors)process.exitCode=1;
