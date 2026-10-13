import assert from 'node:assert/strict';
import {handle} from '../api-worker/index.mjs';
import {saveStockSnapshot} from '../site-contract/stock-store.mjs';
const data=new Map();
const kv={get:async(key,format)=>{const raw=data.get(key)??null;return format==='json'&&raw?JSON.parse(raw):raw;},put:async(key,value)=>data.set(key,value)};
const env={SNAPSHOT_READ_TOKEN:'integration-test',MACRO_KV:kv};
const request=(path,auth=true)=>new Request('https://test.invalid'+path,{headers:auth?{Authorization:'Bearer integration-test'}:{}});
assert.equal((await handle(request('/api/stock-report?ticker=8299',false),env)).status,401);
assert.equal((await handle(request('/api/stock-report?ticker=8299'),env)).status,503);
await saveStockSnapshot(kv,{ticker:'8299',as_of:'2026-10-13T00:00:00Z',observations:[{ticker:'8299',metric:'close',value:200,observed_at:'2026-10-12',source:'TWSE STOCK_DAY',status:'ok'}]});
const response=await handle(request('/api/stock-report?ticker=8299'),env,Date.parse('2026-10-13T00:00:00Z'));
assert.equal(response.status,200);
const result=await response.json();
assert.equal(result.report.observations[0].value,200);
assert.equal(result.report.final_rating,null);
assert.equal((await handle(request('/api/market-snapshot'),env)).status,503); // no macro snapshot; unchanged route
console.log('Worker end-to-end mock KV routing passed');
