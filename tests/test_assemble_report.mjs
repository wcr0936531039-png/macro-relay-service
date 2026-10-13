import assert from 'node:assert/strict';
import {assembleStockReport} from '../site-contract/assemble-report.mjs';
const inputs=[
{ticker:'8299',metric:'revenue',value:'100',observed_at:'2026-09-30',source:'MOPS'},
{ticker:'5289',metric:'revenue',value:'200',observed_at:'2026-09-30',source:'MOPS'}
];
const a=assembleStockReport({ticker:'8299',observations:inputs,requiredMetrics:['revenue','eps']});
assert.equal(a.coverage.status,'partial');
assert.equal(a.observations.length,1);
assert.equal(a.observations[0].value,100);
assert.equal(a.final_rating,null);
assert.equal(a.modules.veto.status,'unknown');
const b=assembleStockReport({ticker:'5289',observations:inputs,requiredMetrics:['revenue']});
assert.equal(b.observations.length,1);
assert.equal(b.observations[0].value,200);
assert.equal(b.coverage.status,'complete');
assert.equal(b.final_rating,null);
assert.throws(()=>assembleStockReport({ticker:'8299',observations:[{...inputs[0],source:''}]}),/MISSING_SOURCE/);
console.log('assemble-report tests passed');
