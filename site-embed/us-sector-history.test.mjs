import assert from 'node:assert/strict';
import {returnsFromCloses} from './us-sector-history.js';
assert.equal(returnsFromCloses([]).status,'UNKNOWN');
const rows=Array.from({length:21},(_,i)=>({date:new Date(Date.UTC(2026,8,i+1)).toISOString().slice(0,10),close:100+i}));
const result=returnsFromCloses(rows);
assert.equal(result.status,'OK');
assert.ok(Math.abs(result.return5d-100*(120/115-1))<1e-10);
assert.ok(Math.abs(result.return20d-20)<1e-10);
assert.equal(returnsFromCloses([...rows.slice(0,20),{date:'2026-09-31',close:120}]).status,'UNKNOWN');
console.log('history calculations passed');

assert.equal(returnsFromCloses([...rows,{date:'2026-09-21',close:122}]).reason,'DUPLICATE_DATES');
assert.equal(returnsFromCloses([...rows.slice(0,20),{date:'2026-09-21',close:NaN}]).reason,'INVALID_HISTORY');
assert.equal(returnsFromCloses([...rows.slice(0,20),null]).reason,'INVALID_HISTORY');
assert.equal(rows.length,21);
console.log('history integrity rejection passed');
