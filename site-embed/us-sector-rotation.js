export const SECTORS = Object.freeze(['XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE']);
const valid = x => typeof x === 'number' && Number.isFinite(x);
export function evaluateSectorRotation(data = {}) {
  const benchmark = data.benchmark || {};
  const sectors = {};
  for (const symbol of SECTORS) {
    const source = (data.sectors || {})[symbol] || {};
    const relative = {};
    const missing = [];
    for (const days of [5,10,20]) {
      const key = 'return'+days+'d';
      if (valid(source[key]) && valid(benchmark[key])) relative[key] = source[key] - benchmark[key];
      else { relative[key] = null; missing.push(key); }
    }
    const complete = missing.length === 0;
    const values = Object.values(relative);
    const classification = !complete ? 'DATA_INCOMPLETE' : values.every(v=>v>0) ? 'LEADING' : values.every(v=>v<0) ? 'LAGGING' : 'MIXED';
    const fundamentals = {};
    for (const key of ['fundFlow','breadthAboveMA20','breadthAboveMA60','epsRevision','forwardPE','roic']) fundamentals[key] = valid(source[key]) ? source[key] : null;
    sectors[symbol] = {status:complete?'OK':'UNKNOWN',classification,relative,missing,fundamentals,observedAt:typeof source.observedAt==='string'?source.observedAt:null};
  }
  const all = Object.values(sectors);
  const coverage = all.filter(s=>s.status==='OK').length;
  const leaders = all.filter(s=>s.classification==='LEADING').length;
  const laggards = all.filter(s=>s.classification==='LAGGING').length;
  const classification = coverage !== SECTORS.length ? 'DATA_INCOMPLETE' : leaders>=7 ? 'BROAD_PARTICIPATION' : leaders<=2 && laggards>=5 ? 'NARROW_OR_WEAK' : 'MIXED_ROTATION';
  return {status:coverage===SECTORS.length?'OK':'UNKNOWN',classification,coverage,total:SECTORS.length,sectors,scoreContribution:0,veto:false};
}
