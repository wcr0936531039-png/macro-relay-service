const isDay = s => typeof s==='string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(s)) && new Date(s).toISOString().slice(0,10)===s;
export function returnsFromCloses(rows) {
  if (!Array.isArray(rows)) return {status:'UNKNOWN',reason:'NO_HISTORY'};
  const filtered=rows.filter(x=>x && isDay(x.date) && typeof x.close==='number' && Number.isFinite(x.close) && x.close>0);
  const sorted=filtered.sort((a,b)=>a.date.localeCompare(b.date));
  const unique=[...new Map(sorted.map(x=>[x.date,x])).values()];
  if(unique.length<21)return {status:'UNKNOWN',reason:'INSUFFICIENT_HISTORY',available:unique.length};
  const latest=unique[unique.length-1];
  const result={status:'OK',observedAt:latest.date};
  for(const n of [5,10,20])result['return'+n+'d']=(latest.close/unique[unique.length-1-n].close-1)*100;
  return result;
}
