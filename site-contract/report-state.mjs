// Proposed site-side Master Model V2 report state adapter.
// Independent of the existing macro snapshot schema_version=1 API.
export const MODULES = Object.freeze(['screening','fundamentals','macro','research','valuation','veto']);
const STATES = new Set(['complete','partial','pending','unavailable','unknown']);
export function createReport(ticker) {
  if (!/^[0-9]{4,6}$/.test(String(ticker))) throw new Error('INVALID_TICKER');
  return {schema_version:2,ticker:String(ticker),as_of:null,status:'pending',
    modules:Object.fromEntries(MODULES.map(k=>[k,{status:k==='veto'?'unknown':'pending',evidence:[]}])),
    final_rating:null};
}
export function updateModule(report, key, patch) {
  if (!MODULES.includes(key)) throw new Error('UNKNOWN_MODULE');
  if (!STATES.has(patch?.status)) throw new Error('INVALID_STATUS');
  if (!Array.isArray(patch.evidence)) throw new Error('INVALID_EVIDENCE');
  const next=structuredClone(report);
  next.modules[key]={status:patch.status,evidence:patch.evidence.map(e=>({...e}))};
  const statuses=Object.values(next.modules).map(m=>m.status);
  next.status=statuses.every(s=>s==='complete')?'complete':
    statuses.every(s=>s==='pending'||s==='unknown')?'pending':'partial';
  // Never carry an old confirmed rating through a data-state change.
  next.final_rating=null;
  return next;
}
export function evaluateReport(report, {rating=null}={}) {
  const next=structuredClone(report);
  const veto=next.modules.veto;
  // Confirmation requires verified non-veto and all substantive modules complete.
  const ready=MODULES.every(k=>next.modules[k].status==='complete');
  const evidenceValid=MODULES.every(k=>next.modules[k].evidence.length>0);
  const vetoClear=veto.evidence.some(e=>e?.decision==='PASS' && e?.verified===true)
    && !veto.evidence.some(e=>e?.decision==='VETO');
  next.final_rating=ready && evidenceValid && vetoClear && typeof rating==='string'?rating:null;
  return next;
}
