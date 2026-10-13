// Stock source adapter: fail closed and preserve provenance. No fake fundamentals.
const CODE=/^[0-9]{4,6}$/;
export function normalizeTicker(value) {
  const ticker=String(value??'').trim();
  if(!CODE.test(ticker)) throw new Error('INVALID_TICKER');
  return ticker;
}
export function normalizeObservation({ticker,metric,value,observed_at,source,source_url=null,period=null}) {
  ticker=normalizeTicker(ticker);
  if(typeof metric!=='string'||!metric.trim()) throw new Error('INVALID_METRIC');
  if(typeof source!=='string'||!source.trim()) throw new Error('MISSING_SOURCE');
  if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(observed_at)||Number.isNaN(Date.parse(observed_at+'T00:00:00Z'))) throw new Error('INVALID_DATE');
  if(value===null||value===undefined||value===''||value==='.') return {ticker,metric,value:null,observed_at,period,source,source_url,status:'missing'};
  const num=typeof value==='number'?value:typeof value==='string'&&value.trim()?Number(value):NaN;
  if(!Number.isFinite(num)) throw new Error('INVALID_VALUE');
  return {ticker,metric,value:num,observed_at,period,source,source_url,status:'ok'};
}
export function selectLatest(observations,ticker,metric) {
  ticker=normalizeTicker(ticker);
  const rows=observations.filter(o=>o.ticker===ticker&&o.metric===metric&&o.status==='ok');
  return rows.reduce((best,o)=>!best||o.observed_at>best.observed_at?o:best,null);
}
export function sourceCoverage(observations,ticker,requiredMetrics) {
  ticker=normalizeTicker(ticker);
  const metrics=requiredMetrics.map(metric=>{
    const row=selectLatest(observations,ticker,metric);
    return {metric,status:row?'ok':'missing',observed_at:row?.observed_at??null,source:row?.source??null};
  });
  return {ticker,status:metrics.every(m=>m.status==='ok')?'complete':'partial',metrics};
}
