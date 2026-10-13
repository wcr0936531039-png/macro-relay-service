import assert from 'node:assert/strict';
import {loadUSSectorReport} from './us-sector-loader.js';
const bad=await loadUSSectorReport(async()=>({ok:false,status:503}));
assert.equal(bad.status,'UNKNOWN');
assert.equal(bad.errorCode,'DATA_UNAVAILABLE');
assert.equal(bad.scoreContribution,0);
const mismatch=await loadUSSectorReport(async()=>({ok:true,json:async()=>({schema_version:9})}));
assert.equal(mismatch.status,'UNKNOWN');
const empty=await loadUSSectorReport(async()=>({ok:true,json:async()=>({schema_version:1,histories:{},status:{}})}));
assert.equal(empty.status,'UNKNOWN');
console.log('sector loader fallbacks passed');

const validRows=Array.from({length:21},(_,i)=>({date:new Date(Date.UTC(2026,8,23+i)).toISOString().slice(0,10),close:100+i}));
const tickers=['SPY','XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE'];
const complete={schema_version:1,source:'test',generated_at:'2026-10-13T00:00:00Z',histories:Object.fromEntries(tickers.map(t=>[t,validRows])),status:Object.fromEntries(tickers.map(t=>[t,{status:'ok',observed_at:'2026-10-13'}]))};
const fresh=await loadUSSectorReport(async()=>({ok:true,json:async()=>complete}),'test-url',new Date('2026-10-14T12:00:00Z'));
assert.equal(fresh.status,'OK');
const stale=await loadUSSectorReport(async()=>({ok:true,json:async()=>complete}),'test-url',new Date('2026-10-20T12:00:00Z'));
assert.equal(stale.status,'UNKNOWN');
assert.equal(stale.errorCode,'STALE_DATA');
assert.equal(stale.scoreContribution,0);
console.log('sector loader freshness gate passed');

let observedSignal;
const aborted=await loadUSSectorReport(async(_url,opts)=>{observedSignal=opts.signal;throw Object.assign(new Error('aborted'),{name:'AbortError'});});
assert.equal(observedSignal instanceof AbortSignal,true);
assert.equal(aborted.status,'UNKNOWN');
assert.equal(aborted.errorCode,'DATA_UNAVAILABLE');
console.log('sector fetch abort fallback passed');
