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
