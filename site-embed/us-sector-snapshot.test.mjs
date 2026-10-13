import assert from 'node:assert/strict';
import {evaluateSectorSnapshot} from './us-sector-snapshot.js';
import {SECTORS} from './us-sector-rotation.js';
assert.equal(evaluateSectorSnapshot().status,'UNKNOWN');
const rows=Array.from({length:21},(_,i)=>({date:new Date(Date.UTC(2026,8,i+1)).toISOString().slice(0,10),close:100+i}));
const histories={SPY:rows};
const status={SPY:{status:'ok'}};
for(const s of SECTORS){histories[s]=rows;status[s]={status:'ok'};}
const full=evaluateSectorSnapshot({histories,status,source:'fixture'});
assert.equal(full.status,'OK');
assert.equal(full.coverage,11);
assert.equal(full.classification,'MIXED_ROTATION');
assert.equal(full.scoreContribution,0);
histories.XLK=rows.slice(0,20);
const partial=evaluateSectorSnapshot({histories,status});
assert.equal(partial.status,'UNKNOWN');
assert.equal(partial.sectors.XLK.status,'UNKNOWN');
console.log('sector snapshot tests passed');

const metaHistories={SPY:rows},metaStatus={SPY:{status:'ok',observed_at:'2026-09-22'}};
for(const s of SECTORS){metaHistories[s]=rows;metaStatus[s]={status:'ok',observed_at:'2026-09-21'};}
const badMetadata=evaluateSectorSnapshot({histories:metaHistories,status:metaStatus});
assert.equal(badMetadata.status,'UNKNOWN');
assert.equal(badMetadata.coverage,0);
metaStatus.SPY.observed_at='2026-09-21';
const goodMetadata=evaluateSectorSnapshot({histories:metaHistories,status:metaStatus});
assert.equal(goodMetadata.status,'OK');
metaStatus.XLK.observed_at='2026-09-20';
const partialMetadata=evaluateSectorSnapshot({histories:metaHistories,status:metaStatus});
assert.equal(partialMetadata.status,'UNKNOWN');
assert.equal(partialMetadata.sectors.XLK.status,'UNKNOWN');
console.log('sector metadata alignment tests passed');

const gapHistories={SPY:rows};
const gapStatus={SPY:{status:'ok',observed_at:'2026-09-21'}};
for(const symbol of SECTORS){gapHistories[symbol]=rows;gapStatus[symbol]={status:'ok',observed_at:'2026-09-21'};}
gapHistories.XLK=[...rows.slice(0,8),...rows.slice(9),{date:'2026-09-22',close:121}];
const tradingCalendarMismatch=evaluateSectorSnapshot({histories:gapHistories,status:gapStatus});
assert.equal(tradingCalendarMismatch.status,'UNKNOWN');
assert.equal(tradingCalendarMismatch.sectors.XLK.status,'UNKNOWN');
assert.equal(tradingCalendarMismatch.coverage,10);
assert.equal(tradingCalendarMismatch.scoreContribution,0);
console.log('sector trading-session alignment test passed');
