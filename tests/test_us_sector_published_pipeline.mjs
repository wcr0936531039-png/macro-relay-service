import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {handle} from '../api-worker/index.mjs';
import {attachUSSectorContext} from '../site-embed/us-sector-context.js';

// End-to-end contract against the actually committed production data file,
// not an invented fixture or an external network request.
const snapshot=JSON.parse(readFileSync(new URL('../data/us_sector_history.json',import.meta.url),'utf8'));
assert.equal(snapshot.schema_version,1);
const observation=snapshot.status?.SPY?.observed_at;
assert.match(observation,/^\d{4}-\d{2}-\d{2}$/);
const now=Date.parse(observation+'T12:00:00Z');
const sectorRequest=new Request('https://example.invalid/api/us-sector-report');
let calls=0;
const fetchSnapshot=async(_url,opts)=>{
  calls++;
  assert.ok(opts.signal);
  return {ok:true,json:async()=>snapshot};
};
const response=await handle(sectorRequest,{},now,fetchSnapshot);
assert.equal(response.status,200);
const body=await response.json();
assert.equal(body.status,'OK');
assert.equal(body.coverage.valid,11);
assert.equal(body.observedAt,observation);
assert.equal(body.benchmark,'SPY');
assert.equal(body.scoreContribution,0);
assert.equal(body.macroGateOverride,null);
assert.equal(body.vetoOverride,null);
const masterReport=Object.freeze({score:81,macroGate:Object.freeze({status:'WATCH'}),tenD:Object.freeze({score:78}),veto:Object.freeze({blocked:true})});
const extended=await attachUSSectorContext(masterReport,fetchSnapshot,new Date(now));
assert.equal(extended.usSectorContext.status,'OK');
assert.equal(extended.usSectorContext.observedAt,observation);
assert.equal(extended.usSectorContext.coverage.valid,11);
assert.equal(extended.score,81);
assert.equal(extended.tenD.score,78);
assert.equal(extended.veto.blocked,true);
assert.equal(extended.usSectorContext.scoreContribution,0);
assert.equal(extended.usSectorContext.vetoOverride,null);
assert.equal(calls,2);
const unavailable=await handle(sectorRequest,{},now,async()=>{throw Error('offline');});
assert.equal((await unavailable.json()).status,'UNKNOWN');
console.log('Committed US sector snapshot -> API Worker -> Master Model report: PASS',observation);
