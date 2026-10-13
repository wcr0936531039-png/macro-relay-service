import assert from 'node:assert/strict';
import {returnsFromCloses} from './us-sector-history.js';
assert.equal(returnsFromCloses([]).status,'UNKNOWN');
const rows=Array.from({length:21},(_,i)=>({date:`2026-09-${String(i+1).padStart(2,'0')}`,close:100+i}));
const result=returnsFromCloses(rows);
assert.equal(result.status,'OK');
assert.equal(result.return5d,100*(120/115-1));
assert.equal(result.return20d,20);
console.log('history calculations passed');
