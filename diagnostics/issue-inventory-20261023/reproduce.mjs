// Local synthetic checks only. Usage: node reproduce.mjs /path/to/dist/server/index.js
import fs from 'node:fs';
const file=process.argv[2];
if(!file)throw Error('Supply the built Worker path');
const source=fs.readFileSync(file,'utf8');
const api=await import('data:text/javascript;base64,'+Buffer.from(source+'\nexport {loadStockCreditDataset,persistSiteRefreshStatus};').toString('base64'));
function db(seed,fail=false){
 return {prepare(){return {run:async()=>{if(fail)throw Error('synthetic storage unavailable');return {success:true};},bind(){return {all:async()=>({results:seed?[{payload:JSON.stringify(seed),updated_at:seed.capturedAt,expires_at:'2026-11-01T00:00:00Z'}]:[]}),run:async()=>{if(fail)throw Error('synthetic storage unavailable');return {success:true};}};}};}};
}
const base={symbol:'8299',dataset:'TaiwanStockMarginPurchaseShortSale',source:'https://api.finmindtrade.com/api/v4/data?dataset=TaiwanStockMarginPurchaseShortSale',capturedAt:'2026-10-22T15:00:00Z'};
const row={stock_id:'8299',date:'2020-01-02',MarginPurchaseTodayBalance:100,MarginPurchaseYesterdayBalance:90,ShortSaleTodayBalance:10};
const old=await api.loadStockCreditDataset('8299',{DB:db({...base,rows:[row]})},async()=>{throw Error('unexpected upstream');},Date.parse('2026-10-23T02:00:00Z'));
const missing=await api.loadStockCreditDataset('8299',{DB:db({...base,rows:[{stock_id:'8299',date:'2026-10-22'}]})},async()=>{throw Error('unexpected upstream');},Date.parse('2026-10-23T02:00:00Z'));
let persistence='resolved';
try{await api.persistSiteRefreshStatus({DB:db(null,true)},{runId:'synthetic-storage-failure',startedAt:'2026-10-22T15:00:00Z',status:'complete',completedAt:'2026-10-22T15:01:00Z'});}catch(error){persistence='rejected: '+error.message;}
console.log(JSON.stringify({synthetic:true,scope:'local revision2 only; no production requests',oldObservation:{date:old.rows[0]?.date,status:old.status,is_stale:old.is_stale},missingBalances:{status:missing.status,rows:missing.rows},storageUnavailable:{persistSiteRefreshStatus:persistence}},null,2));
