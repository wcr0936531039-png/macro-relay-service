import assert from 'node:assert/strict';
import {loadUSSectorReport} from '../site-embed/us-sector-loader.js';

const source='https://raw.githubusercontent.com/wcr0936531039-png/macro-relay-service/main/data/us_sector_history.json';
const maxAttempts=4;
let report;
for(let attempt=1;attempt<=maxAttempts;attempt++){
  report=await loadUSSectorReport(fetch,source,new Date());
  if(report.status==='OK' && report.coverage?.valid===11) break;
  if(attempt<maxAttempts) await new Promise(resolve=>setTimeout(resolve,5000));
}
console.log(JSON.stringify({
  check:'PUBLIC_RAW_SITE_READER',
  url:source,
  status:report?.status,
  errorCode:report?.errorCode||null,
  observedAt:report?.observedAt||null,
  coverage:report?.coverage||null,
  scoreContribution:report?.scoreContribution,
  vetoOverride:report?.vetoOverride
},null,2));
assert.equal(report?.status,'OK','Public Raw URL must yield a fresh complete sector report');
assert.equal(report?.coverage?.valid,11);
assert.equal(report?.scoreContribution,0);
assert.equal(report?.vetoOverride,null);
