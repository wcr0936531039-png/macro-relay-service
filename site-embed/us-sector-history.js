const isDay = s => typeof s==='string' && /^\d{4}-\d{2}-\d{2}$/.test(s) && !Number.isNaN(Date.parse(s)) && new Date(s).toISOString().slice(0,10)===s;
export function returnsFromCloses(rows) {
  if (!Array.isArray(rows)) return {status:'UNKNOWN',reason:'NO_HISTORY'};
  if (rows.some(x=>!x || !isDay(x.date) || typeof x.close!=='number' || !Number.isFinite(x.close) || x.close<=0)) return {status:'UNKNOWN',reason:'INVALID_HISTORY'};
  const sorted=[...rows].sort((a,b)=>a.date.localeCompare(b.date));
  if (sorted.some((x,i)=>i>0 && x.date===sorted[i-1].date)) return {status:'UNKNOWN',reason:'DUPLICATE_DATES'};
  const unique=sorted;
  if(unique.length<21)return {status:'UNKNOWN',reason:'INSUFFICIENT_HISTORY',available:unique.length};
  const latest=unique[unique.length-1];
  const result={status:'OK',observedAt:latest.date};
  for(const n of [5,10,20])result['return'+n+'d']=(latest.close/unique[unique.length-1-n].close-1)*100;
  return result;
}
