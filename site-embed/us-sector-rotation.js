export const SECTORS = ['XLK','XLC','XLY','XLP','XLF','XLI','XLV','XLE','XLB','XLU','XLRE'];
export function evaluateSectorRotation(data = {}) {
  const benchmark = data.benchmark || {};
  const sectors = {};
  for (const symbol of SECTORS) {
    const source = (data.sectors || {})[symbol] || {};
    const relative = {};
    const missing = [];
    for (const days of [5,10,20]) {
      const key = `return${days}d`;
      if (Number.isFinite(source[key]) && Number.isFinite(benchmark[key])) relative[key] = source[key] - benchmark[key];
      else { relative[key] = null; missing.push(key); }
    }
    sectors[symbol] = {status:missing.length ? 'UNKNOWN':'OK',relative,missing,observedAt:source.observedAt || null};
  }
  const complete = Object.values(sectors).filter(s => s.status === 'OK').length;
  return {status:complete === SECTORS.length ? 'OK':'UNKNOWN',coverage:complete,total:SECTORS.length,sectors,scoreContribution:0,veto:false};
}
